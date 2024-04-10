import cv2

class PedestrianDetection:
    def __init__(self, cascade_path):
        self.pedestrian_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_pedestrians(self, image, scale_factor=1.1, min_neighbors=5):
        """
        Detects pedestrians in an image.

        Args:
            image: The input image.
            scale_factor: Parameter specifying how much the image size is reduced at each image scale.
            min_neighbors: Parameter specifying how many neighbors each candidate rectangle should have to retain it.

        Returns:
            A list of bounding boxes for detected pedestrians.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        pedestrians = self.pedestrian_cascade.detectMultiScale(
            gray,
            scaleFactor=scale_factor,
            minNeighbors=min_neighbors
        )
        return pedestrians

    def visualize_detections(self, image, pedestrians):
        """
        Visualizes pedestrian detections on an image.

        Args:
            image: The input image.
            pedestrians: A list of bounding boxes for detected pedestrians.

        Returns:
            The image with pedestrian detections visualized.
        """
        for (x, y, w, h) in pedestrians:
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)  # Green rectangle
        return image

    def calculate_distance_score(self, image_width, pedestrian_bbox):
        """
        Calculates a distance-based score for a detected pedestrian.

        Args:
            image_width: The width of the image.
            pedestrian_bbox: The bounding box of the detected pedestrian.

        Returns:
            A distance score (higher for closer pedestrians, 0 for those at the edges).
        """
        x, y, w, h = pedestrian_bbox
        center_x = x + w // 2

        # Calculate distance from center of image
        distance_from_center = abs(center_x - image_width // 2)

        # Map distance to a score (adjust parameters as needed)
        max_distance = image_width // 2
        score = 1 - (distance_from_center / max_distance)

        # Set score to 0 if pedestrian is at the edge
        if center_x < w // 2 or center_x > image_width - w // 2:
            score = 0

        return score

    def determine_direction(self, current_bbox, previous_bbox):
        """
        Determines the direction of movement for a pedestrian.

        Args:
            current_bbox: The bounding box of the pedestrian in the current frame.
            previous_bbox: The bounding box of the pedestrian in the previous frame.

        Returns:
            A string indicating the direction ("left", "right", "forward", or "backward").
        """
        curr_x, _, _, _ = current_bbox
        prev_x, _, _, _ = previous_bbox

        if abs(curr_x - prev_x) < 5:  # Threshold for minimal movement
            return "forward"  # Assume forward if movement is negligible

        if curr_x > prev_x:
            return "right"
        else:
            return "left"