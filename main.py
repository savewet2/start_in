import cv2
from car_detection import CarDetector
from autopilot import Autopilot
model_path = 'путь_к_модели/ssd_inference_graph.pb'
label_map_path = 'путь_к_модели/label_map.pbtxt'

# Создание экземпляров классов
car_detector = CarDetector(model_path, label_map_path)
autopilot = Autopilot(car_detector)

# Запуск обработки видеопотока
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    processed_frame = autopilot.process_frame(frame)

    # Отображение результата
    cv2.imshow('Autopilot', cv2.resize(processed_frame, (800, 600)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
