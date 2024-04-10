import tensorflow as tf
import numpy as np
import cv2
from keras import layers, models
from PedestrianDetection import PedestrianDetection
from car_detection import CarDetection

class Autopilot:
    def __init__(self, car_cascade_path, pedestrian_cascade_path):
        self.car_detector = CarDetection(car_cascade_path)
        self.pedestrian_detector = PedestrianDetection(pedestrian_cascade_path)
        self.model = self.create_behavior_classification_model()
        self.previous_frame = None

    def create_behavior_classification_model(self):
        model = models.Sequential([
            layers.Dense(16, activation='relu', input_shape=(4,)),
            layers.Dense(8, activation='relu'),
            layers.Dense(2, activation='softmax')
        ])
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        return model

    def process_frame(self, frame):
        cars = self.car_detector.detect_cars(frame)
        pedestrians = self.pedestrian_detector.detect_pedestrians(frame)

        car_features = []
        for car in cars:
            car_features.append([car[0], car[1], car[2], car[3]])

        pedestrian_features = []

        features = car_features + pedestrian_features

        if features:
            predictions = self.model.predict(tf.convert_to_tensor(features))
            decision = tf.argmax(predictions, axis=1)

            if decision == 0:
                print("Решение: СТОП")
            elif decision == 1:
                print("Решение: ДВИЖЕНИЕ")
            else:
                print("Неизвестное решение:", decision)

        if self.previous_frame is not None:
            current_features = self.extract_features(frame)
            previous_features = self.extract_features(self.previous_frame)
            features = [previous_features, current_features]
            labels = self.determine_labels(features)
            self.model.fit(tf.convert_to_tensor(features), tf.convert_to_tensor(labels))

        self.previous_frame = frame
        return frame
    def extract_features(self, frame):
        features = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Extract car features (assuming car detection is already done)
        cars = self.car_detector.detect_cars(frame)
        for (x, y, w, h) in cars:
            # Feature 1: Distance from center of car to center of image
            center_x = x + w // 2
            distance_from_center = abs(center_x - frame.shape[1] // 2)
            # Feature 2: Average pixel intensity within car bounding box
            average_intensity = np.mean(gray[y:y+h, x:x+w])
            features.append([distance_from_center, average_intensity])

        # Extract pedestrian features (assuming pedestrian detection is already done)
        pedestrians = self.pedestrian_detector.detect_pedestrians(frame)
        for (x, y, w, h) in pedestrians:
            center_x = x + w // 2
            distance_from_center = abs(center_x - frame.shape[1] // 2)
            average_intensity = np.mean(gray[y:y+h, x:x+w])
            features.append([distance_from_center, average_intensity])

        return features

    def determine_labels(self, features):
        """
        Determines labels for training data based on a simple proximity rule.

        Args:
            features: A list of feature vectors.

        Returns:
            A label (0 for stop, 1 for go) based on the closest object distance.
        """
        threshold_distance = 100  # Adjust this threshold as needed
        closest_object_distance = min([feature[0] for feature in features])

        if closest_object_distance[0] < threshold_distance:
            return [0, 0]  # Stop in both previous and current frames
        else:
            return [1, 1]  # Go in both previous and current frames

    def save_model(self, file_path):
        self.model.save(file_path)

    def load_model(self, file_path):
        self.model = models.load_model(file_path)