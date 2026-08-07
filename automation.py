import threading
import time
import cv2
import mediapipe as mp
from hand_detection import HandDetector
print("Loaded automation.py")


class AutomationManager:

    def __init__(self):
        print("Automation Manager Started")
        self.hand_detector = HandDetector()
        self.last_hand_state = None
        # Hand Detection Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7
        )

        self.mp_draw = mp.solutions.drawing_utils

    def process_hand(self, frame):
        frame, state = self.hand_detector.get_hand_state(frame)

        # Only when gesture changes
        if state != self.last_hand_state:
            self.last_hand_state = state

            if state == "OPEN":
                print("OPEN Hand -> Light ON")
                self.execute_action({
                    "device": "Light",
                    "status": "ON"
                })

            elif state == "CLOSED":
                print("CLOSED Hand -> Light OFF")
                self.execute_action({
                    "device": "Light",
                    "status": "OFF"
                })

        return frame, state

    def detect_hand(self, frame):
        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        result = self.hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
            return True

        return False    

    # =========================
    # Execute Actions
    # =========================

    def execute_action(self, action):

        print("ACTION RECEIVED:", action)
        if action is None:
            return

        print("Executing Action:", action)
        if isinstance(action, dict) and action.get("source") == "hand":
           print("Hand Gesture Action")


        if isinstance(action, dict):

            device = action.get("device")
            status = action.get("status")

            if device == "Light":
                if status == "ON":
                    self.light_on()
                elif status == "OFF":
                    self.light_off()

            elif device == "Fan":
                if status == "ON":
                    self.fan_on()
                elif status == "OFF":
                    self.fan_off()

            elif device == "Door":
                if status == "OPEN":
                    self.open_door()
                elif status == "CLOSED":
                    self.close_door()

            else:
                print("Unknown Device")

        else:
            print("Invalid Action Format")

    # =========================
    # Device Actions
    # =========================

    def light_on(self):
        print("💡 Light turned ON")

    def light_off(self):
        print("💡 Light turned OFF")

    def fan_on(self):
        print("🌀 Fan turned ON")

    def fan_off(self):
        print("🌀 Fan turned OFF")

    def open_door(self):
        print("🚪 Door Opened")

    def close_door(self):
        print("🚪 Door Closed")

    # =========================
    # Automation Rules
    # =========================

    def check_rules(self):
        print("Checking Automation Rules")

    def reload_rules(self):
        print("Reloading Rules")

    # =========================
    # Background Scheduler
    # =========================

    def scheduler(self):
        while True:
            print("Scheduler Running...")
            self.check_rules()
            time.sleep(30)

    def start_scheduler(self):
        thread = threading.Thread(
            target=self.scheduler,
            daemon=True
        )
        thread.start()