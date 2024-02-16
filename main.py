import cv2
from car_detection import CarDetector
from autopilot import Autopilot

model_path = ''
#label_map_path = ''
#car_detector = CarDetector(model_path, label_map_path)

autopilot = Autopilot(model_path)

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    processed_frame = autopilot.process_frame(frame)

    cv2.imshow('Autopilot', cv2.resize(processed_frame, (800, 600)))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
