import cv2

class Autopilot:
    def __init__(self, cascade_path):
        self.car_cascade = cv2.CascadeClassifier(cascade_path)

    def calculate_distance(self, object_bbox):
        _, _, _, h = object_bbox

        pixel_to_meter_scale = 0.1 
        distance = h * pixel_to_meter_scale

        return distance

    def process_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = self.car_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=5
        )

        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            object_bbox = (x, y, w, h)

            distance = self.calculate_distance(object_bbox)


            print("Дистанция: {:.2f} м".format(distance))

        return frame

cascade_path = "cars.xml" # Haarcascades 
autopilot = Autopilot(cascade_path)

cap = cv2.VideoCapture("cari.mp4") # file

while True:
    ret, img = cap.read()

    if not ret:
        break

    processed_frame = autopilot.process_frame(img)
    cv2.imshow("Processed Frame", processed_frame)
    if cv2.waitKey(33) == 27:
        break

cv2.destroyAllWindows()
cap.release()
