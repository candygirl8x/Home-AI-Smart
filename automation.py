from voice import VoiceAssistant

print("Loaded automation.py")

import threading
import time


class AutomationManager:

    def __init__(self):

        print("Automation Manager Started")

        self.voice = VoiceAssistant()


    def execute_action(self, action):

        if action is None:
            return

        print("Executing Action:", action)


        if action == "LIGHT_ON":

            self.light_on()


        elif action == "LIGHT_OFF":

            self.light_off()


        elif action == "DOOR_OPEN":

            self.open_door()


        elif action == "DOOR_CLOSE":

            self.close_door()


        elif action == "FAN_ON":

            self.fan_on()


        elif action == "FAN_OFF":

            self.fan_off()


        else:

            print("Unknown Action")



    # =========================
    # Device Actions
    # =========================


    def light_on(self):

        print("💡 Light turned ON")

        self.voice.text_to_speech(
            "Light turned on"
        )



    def light_off(self):

        print("💡 Light turned OFF")

        self.voice.text_to_speech(
            "Light turned off"
        )



    def open_door(self):

        print("🚪 Door open")

        self.voice.text_to_speech(
            "Door opened"
        )



    def close_door(self):

        print("🚪 Door close")

        self.voice.text_to_speech(
            "Door closed"
        )



    def fan_on(self):

        print("🌀 Fan turned ON")

        self.voice.text_to_speech(
            "Fan turned on"
        )



    def fan_off(self):

        print("🌀 Fan turned OFF")

        self.voice.text_to_speech(
            "Fan turned off"
        )



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