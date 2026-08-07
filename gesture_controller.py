from hand_detection import HandDetector
from database import Database
import cv2
import time


class GestureController:

    def __init__(self):
        self.detector = HandDetector()
        self.db = Database()

        self.last_state = ""
        self.last_time = time.time()

    def run(self):

        cap = cv2.VideoCapture(0)

        while True:

            success, frame = cap.read()

            if not success:
                break

            frame, state = self.detector.get_hand_state(frame)

            current_time = time.time()

            # Execute only if state changes and 2 seconds have passed
            if (
                state != self.last_state
                and current_time - self.last_time > 2
            ):

                if state == "OPEN":
                    print("Gesture: OPEN -> Light ON")

                    devices = self.db.get_devices()

                    for device in devices:
                        if device["type"].lower() == "light":
                            self.db.update_device_status(
                                device["id"],
                                "ON"
                            )

                elif state == "CLOSED":
                    print("Gesture: CLOSED -> Light OFF")

                    devices = self.db.get_devices()

                    for device in devices:
                        if device["type"].lower() == "light":
                            self.db.update_device_status(
                                device["id"],
                                "OFF"
                            )

                self.last_state = state
                self.last_time = current_time

            cv2.imshow("Gesture Controller", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    controller = GestureController()
    controller.run()