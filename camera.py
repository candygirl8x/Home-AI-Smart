import cv2
from hand_detection import HandDetector
from automation import AutomationManager


class Camera:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)

        self.automation = AutomationManager()
        self.detector = HandDetector()

        self.last_state = None


    def get_frame(self):

        success, frame = self.cap.read()

        if not success:
            return None

        frame = cv2.flip(frame, 1)

        frame, state = self.detector.get_hand_state(frame)


        # Only execute when gesture changes
        if state != self.last_state:

            self.last_state = state


            if state == "OPEN":

                self.automation.execute_action({
                    "device": "Light",
                    "status": "ON"
                })

                print("✋ OPEN HAND")
                print("ACTION : LIGHT ON")


            elif state == "CLOSED":

                self.automation.execute_action({
                    "device": "Light",
                    "status": "OFF"
                })

                print("✊ CLOSED HAND")
                print("ACTION : LIGHT OFF")


        return frame



    def show_frame(self, frame):

        if frame is not None:
            cv2.imshow(
                "Smart Home AI Camera",
                frame
            )


    def stop(self):

        self.cap.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":

    camera = Camera()

    while True:

        frame = camera.get_frame()

        if frame is not None:
            camera.show_frame(frame)


        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    camera.stop()