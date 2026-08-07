import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

class HandDetector:

    def __init__(self):
        self.hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def get_hand_state(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        hand_state = "NO HAND"

        if results.multi_hand_landmarks:

            for hand_landmarks, handedness in zip(
                    results.multi_hand_landmarks,
                    results.multi_handedness):

                hand_label = handedness.classification[0].label

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                lm = hand_landmarks.landmark

                fingers = 0

                # ---------- THUMB ----------
                if hand_label == "Right":
                    if lm[4].x < lm[3].x:
                        fingers += 1
                else:
                    if lm[4].x > lm[3].x:
                        fingers += 1

                # ---------- INDEX ----------
                if lm[8].y < lm[6].y:
                    fingers += 1

                # ---------- MIDDLE ----------
                if lm[12].y < lm[10].y:
                    fingers += 1

                # ---------- RING ----------
                if lm[16].y < lm[14].y:
                    fingers += 1

                # ---------- PINKY ----------
                if lm[20].y < lm[18].y:
                    fingers += 1

                print("--------------------------------")
                print("Hand :", hand_label)
                print("Finger Count :", fingers)

                if fingers >= 4:
                    hand_state = "OPEN"
                else:
                    hand_state = "CLOSED"

                print("State :", hand_state)

        cv2.putText(
            frame,
            hand_state,
            (20, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        return frame, hand_state


if __name__ == "__main__":

    detector = HandDetector()

    cap = cv2.VideoCapture(0)

    while True:

        success, frame = cap.read()

        if not success:
            break

        # Mirror camera
        frame = cv2.flip(frame, 1)

        frame, state = detector.get_hand_state(frame)

        cv2.imshow("Hand Detection", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()