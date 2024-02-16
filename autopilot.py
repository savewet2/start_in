import cv2

class Autopilot:
    def __init__(self, cascade_path):
        self.car_cascade = cv2.CascadeClassifier(cascade_path)

    def calculate_distance(self, object_bbox):
        # Ваш код для вычисления расстояния между камерой и машиной
        # В этом примере, используем высоту объекта на изображении как приблизительную метрику
        _, _, _, h = object_bbox

        # Параметр для приблизительного масштабирования пикселей в метры
        pixel_to_meter_scale = 0.1  # Вы можете настроить это значение в зависимости от ваших данных

        # Вычисляем расстояние в метрах (просто пример, может потребоваться дополнительная настройка)
        distance = h * pixel_to_meter_scale

        return distance

    def process_frame(self, frame):
        # Переводим кадр в оттенки серого (если изображение еще не в оттенках серого)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = self.car_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5
        )

        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Получаем ограничивающий прямоугольник машины
            object_bbox = (x, y, w, h)

            # Вычисляем расстояние между машиной и камерой
            distance = self.calculate_distance(object_bbox)

            # Выводим расстояние в консоль (можно заменить на другие действия)
            print("Distance to the car: {:.2f} meters".format(distance))

        return frame

# Пример использования:
cascade_path = "cars.xml"
autopilot = Autopilot(cascade_path)

# Открываем видеопоток из файла
cap = cv2.VideoCapture("cari.mp4")

while True:
    # Считываем кадр из видеопотока
    ret, img = cap.read()

    # Проверяем, успешно ли произошло считывание кадра
    if not ret:
        break

    # Обрабатываем кадр с помощью автопилота
    processed_frame = autopilot.process_frame(img)

    # Отображаем обработанный кадр
    cv2.imshow("Processed Frame", processed_frame)

    # Проверяем, была ли нажата клавиша выхода (ESC)
    if cv2.waitKey(33) == 27:
        break

# Закрываем окна и освобождаем ресурсы
cv2.destroyAllWindows()
cap.release()