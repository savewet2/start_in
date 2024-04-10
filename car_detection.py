import cv2

class CarDetection:
    def __init__(self, cascade_path):
        self.car_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_cars(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cars = self.car_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5
        )
        return cars
