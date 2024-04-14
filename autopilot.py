import tensorflow as tf
import numpy as np
import cv2
from keras import layers, models
from PedestrianDetection import PedestrianDetection
from car_detection import CarDetection


class Autopilot:
    def __init__(self, car_cascade_path, pedestrian_cascade_path, model_path=None):
        self.car_detector = CarDetection(car_cascade_path)
        self.pedestrian_detector = PedestrianDetection(pedestrian_cascade_path)

        if model_path:
            self.model = models.load_model(model_path)
        else:
            self.model = self.create_behavior_classification_model()

        self.previous_frame = None
        self.previous_detections = []

    def create_behavior_classification_model(self, input_shape=(2,), num_classes=2, hidden_layers=[16, 8]):
        """
        Creates a behavior classification model.

        Args:
            input_shape: Shape of the input feature vector.
            num_classes: Number of output classes (e.g., 2 for "STOP" and "GO").
            hidden_layers: A list of integers specifying the number of units in each hidden layer.

        Returns:
            A compiled Keras model for behavior classification.
        """
        model = models.Sequential()

        # Input layer
        model.add(layers.Dense(hidden_layers[0], activation='relu', input_shape=input_shape))

        # Hidden layers
        for units in hidden_layers[1:]:
            model.add(layers.Dense(units, activation='relu'))

        # Output layer
        model.add(layers.Dense(num_classes, activation='softmax'))

        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        return model
    def process_frame(self, frame):
        cars = self.car_detector.detect_cars(frame)
        pedestrians = self.pedestrian_detector.detect_pedestrians(frame)

        features, self.previous_detections = self.extract_features_and_track(frame, cars, pedestrians)

        if features:
            predictions = self.model.predict(tf.convert_to_tensor(features))
            decision = tf.argmax(predictions, axis=1)[0]  # Get the class index
            if decision == 0:
                print("Решение: СТОП")
            elif decision == 1:
                print("Решение: ДВИЖЕНИЕ")
            else:
                print("Неизвестное решение:", decision)

        # Online learning (optional, requires careful implementation)
        # ...

        # Visualize detections
        for detection in self.previous_detections:
            x, y, w, h, _, _ = detection
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return frame

    def extract_features_and_track(self, frame, cars, pedestrians):
        features = []
        current_detections = []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for car in cars:
            x, y, w, h = car
            center_x = x + w // 2
            distance_from_center = abs(center_x - frame.shape[1] // 2)
            average_intensity = np.mean(gray[y:y + h, x:x + w])
            features.append([distance_from_center, average_intensity])
            current_detections.append([x, y, w, h, "car", None])  # Add type and ID

        for pedestrian in pedestrians:
            x, y, w, h = pedestrian
            center_x = x + w // 2
            distance_from_center = abs(center_x - frame.shape[1] // 2)
            average_intensity = np.mean(gray[y:y + h, x:x + w])
            features.append([distance_from_center, average_intensity])
            current_detections.append([x, y, w, h, "pedestrian", None])



        return features, current_detections
    def determine_labels(self, features):

        """
        Determines labels for training data based on a simple proximity rule.

        Args:
            features: A list of feature vectors.

        Returns:
            A label (0 for stop, 1 for go) based on the closest object distance.
        """

        threshold_distance = 100
        closest_object_distance = min([feature[0] for feature in features])

        if type(closest_object_distance) is type(threshold_distance):
            if closest_object_distance < threshold_distance:
                return [0, 0]
            else:
                return [1, 1]

    def save_model(self, file_path):
        self.model.save(file_path)

    def load_model(self, file_path):
        self.model = models.load_model(file_path)


