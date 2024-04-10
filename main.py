from autopilot import Autopilot
import cv2
class Main:
    def __init__(self, car_cascade_path, pedestrian_cascade_path, autopilot_save_path=None):
        self.autopilot = Autopilot(car_cascade_path, pedestrian_cascade_path)
        self.autopilot_save_path = autopilot_save_path

    def train_autopilot(self, video_path, num_frames=100):
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            self.autopilot.process_frame(frame)

            frame_count += 1
            if frame_count >= num_frames:
                break

        cap.release()

        # Save the trained autopilot model if a save path is provided
        if self.autopilot_save_path:
            self.autopilot.save_model(self.autopilot_save_path)

    def run_autopilot(self, video_path):
        cap = cv2.VideoCapture(video_path)
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            self.autopilot.process_frame(frame)

        cap.release()


if __name__ == "__main__":
    car_cascade_path = "C:\\Users\\savewet\\Desktop\\Project\\start_in\\haarcascade_car.xml"
    pedestrian_cascade_path = "C:\\Users\\savewet\\Desktop\\Project\\start_in\\haarcascade_fullbody.xml"
    autopilot_save_path = "C:\\Users\\savewet\\Desktop\\Project\\start_in\\autopilot_model.h5"

    main = Main(car_cascade_path, pedestrian_cascade_path, autopilot_save_path)

    video_path = "cari.mp4"
    main.train_autopilot(video_path)

    # Run the autopilot on a new video
    test_video_path = "cari.mp4"
    main.run_autopilot(test_video_path)
