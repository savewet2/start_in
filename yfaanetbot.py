import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from tokenz import tokenzz, api_key
from yandexmapclass import YandexGeocoder


TOKEN = tokenzz
geocoder = YandexGeocoder(api_key)

user_requests = {}


admin_chat_id = 1313197485 

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect('support_requests.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    address TEXT,
    coordinates TEXT,
    problem_description TEXT,
    photo_url TEXT,
    status TEXT
)''')

conn.commit()


@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton('Сообщить о проблеме'))
    markup.add(KeyboardButton('Чат поддержки'))
    bot.send_message(
        message.chat.id,
        'Добро пожаловать в службу поддержки! Выберите действие:',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Сообщить о проблеме':
        request_address(message)
    elif message.text == 'Чат поддержки':
        support_chat(message)
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите один из доступных вариантов.')

def request_address(message):
    bot.send_message(message.chat.id, 'Пожалуйста, укажите ваш адрес:')
    bot.register_next_step_handler(message, save_address)

def save_address(message):
    user_requests[message.chat.id] = {'address': message.text}
    bot.send_message(message.chat.id, 'Опишите вашу проблему:')
    bot.register_next_step_handler(message, save_problem)

def save_problem(message):
    user_requests[message.chat.id]['problem_description'] = message.text
    bot.send_message(message.chat.id, 'Прикрепите фотографию проблемы (если есть):')
    bot.register_next_step_handler(message, save_photo)

def save_photo(message):
    if message.photo:
        photo_id = message.photo[-1].file_id  
        file_info = bot.get_file(photo_id)
        photo_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}'
        user_requests[message.chat.id]['photo_url'] = photo_url
    else:
        photo_url = None
        user_requests[message.chat.id]['photo_url'] = None

    address = user_requests[message.chat.id]['address']
    problem_description = user_requests[message.chat.id]['problem_description']
    
    coordinates = geocoder.address_to_coordinates(address)
    
    if coordinates:
        # Преобразуем координаты в строку, если они есть
        coordinates_str = ','.join(map(str, coordinates))  # Например, 'lat,lng'
        user_requests[message.chat.id]['coordinates'] = coordinates_str
        save_to_database(
            message.chat.username,
            address,
            coordinates_str,
            problem_description,
            photo_url
        )
        bot.send_message(
            message.chat.id,
            f'Спасибо! Ваша заявка принята. Адрес: {address}, Координаты: {coordinates_str}. Мы свяжемся с вами в ближайшее время.'
        )
        notify_admin(message.chat.id, address, coordinates_str, problem_description, photo_url)

    else:
        bot.send_message(
            message.chat.id,
            'Не удалось определить координаты по указанному адресу. Пожалуйста, проверьте адрес и попробуйте снова.'
        )

def save_to_database(username, address, coordinates, problem_description, photo_url):
    cursor.execute(
        'INSERT INTO requests (username, address, coordinates, problem_description, photo_url, status) VALUES (?, ?, ?, ?, ?, ?)',
        (username, address, coordinates, problem_description, photo_url, 'Ожидает')
    )
    conn.commit()

def notify_admin(user_chat_id, address, coordinates, problem_description, photo_url):
    message = f'Новая заявка от пользователя {user_chat_id}:\n\n'
    message += f'Адрес: {address}\n'
    message += f'Координаты: {coordinates}\n'
    message += f'Описание проблемы: {problem_description}\n'
    if photo_url:
        message += f'Фото проблемы: {photo_url}\n'
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Просмотреть заявку', callback_data=f'view_{user_chat_id}'))
    markup.add(InlineKeyboardButton('Ответить', callback_data=f'reply_{user_chat_id}'))
    bot.send_message(admin_chat_id, message, reply_markup=markup)

def support_chat(message):
    if message.chat.id == admin_chat_id:
        cursor.execute('SELECT id, username, address, problem_description, status FROM requests WHERE status = "Ожидает"')
        requests = cursor.fetchall()
        markup = InlineKeyboardMarkup()
        for req in requests:
            markup.add(InlineKeyboardButton(f'Заявка от {req[1]}', callback_data=f'view_{req[0]}'))
        bot.send_message(message.chat.id, 'Выберите заявку для просмотра:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Вы можете задать вопрос нашему администратору.')

@bot.callback_query_handler(func=lambda call: call.data.startswith('view_'))
def view_request(call):
    request_id = int(call.data.split('_')[1])
    cursor.execute('SELECT username, address, coordinates, problem_description, photo_url, status FROM requests WHERE id = ?', (request_id,))
    request = cursor.fetchone()
    
    if request:
        username, address, coordinates, problem_description, photo_url, status = request
        message = f'Заявка от {username}:\n\n'
        message += f'Адрес: {address}\n'
        message += f'Координаты: {coordinates}\n'
        message += f'Описание проблемы: {problem_description}\n'
        message += f'Статус: {status}\n'
        
        if photo_url:
            message += f'Фото проблемы: {photo_url}\n'

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Ответить на заявку', callback_data=f'reply_{request_id}'))
        bot.send_message(call.message.chat.id, message, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def handle_answer(call):
    if call.data.startswith('reply_'):
        request_id = int(call.data.split('_')[1])
        cursor.execute('SELECT username, address, problem_description FROM requests WHERE id = ?', (request_id,))
        request = cursor.fetchone()
        
        if request:
            username, address, problem_description = request
            bot.send_message(call.message.chat.id, f'Ответ на запрос от {username}:\n\nАдрес: {address}\nОписание проблемы: {problem_description}\n\nВведите ваш ответ:')
            bot.register_next_step_handler(call.message, send_response, request_id)

def send_response(message, request_id):
    response = message.text
    cursor.execute('SELECT username FROM requests WHERE id = ?', (request_id,))
    user_chat_id = cursor.fetchone()[0]
    
    bot.send_message(user_chat_id, f'Ответ от администратора: {response}')
    cursor.execute('UPDATE requests SET status = "Закрыт" WHERE id = ?', (request_id,))
    conn.commit()
    
    bot.send_message(message.chat.id, 'Ваш ответ отправлен пользователю.')
    support_chat(message)

if __name__ == '__main__':
    print('Бот запущен...')
    bot.infinity_polling()
