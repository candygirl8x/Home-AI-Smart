class AIAssistant:

    def __init__(self):
        print("AI Assistant Started")


    def process_command(self, command):

        if not command:

            return {
                "response": "Please say a command.",
                "action": None
            }


        command = command.lower().strip()


        print("Processing command:", command)


        # =====================
        # Lights
        # =====================

        if "light on" in command or "lights on" in command:

            return {
                "response": "Turning the light on.",
                "action": {
                    "device": "Light",
                    "status": "ON"
                }
            }


        elif "light off" in command or "lights off" in command:

            return {
                "response": "Turning the light off.",
                "action": {
                    "device": "Light",
                    "status": "OFF"
                }
            }


        # =====================
        # Fan
        # =====================

        elif "fan on" in command or "fans on" in command:

            return {
                "response": "Turning the fan on.",
                "action": {
                    "device": "Fan",
                    "status": "ON"
                }
            }


        elif "fan off" in command or "fans off" in command:

            return {
                "response": "Turning the fan off.",
                "action": {
                    "device": "Fan",
                    "status": "OFF"
                }
            }


        # =====================
        # Door
        # =====================

        elif "open door" in command or "door open" in command:

            return {
                "response": "Opening the door.",
                "action": {
                    "device": "Door",
                    "status": "OPEN"
                }
            }


        elif "close door" in command or "door close" in command:

            return {
                "response": "Closing the door.",
                "action": {
                    "device": "Door",
                    "status": "CLOSED"
                }
            }


        # =====================
        # TV
        # =====================

        elif "tv on" in command or "television on" in command:

            return {
                "response": "Turning the TV on.",
                "action": {
                    "device": "TV",
                    "status": "ON"
                }
            }


        elif "tv off" in command or "television off" in command:

            return {
                "response": "Turning the TV off.",
                "action": {
                    "device": "TV",
                    "status": "OFF"
                }
            }


        # =====================
        # Unknown command
        # =====================

        else:

            return {
                "response": "Sorry, I didn't understand the command.",
                "action": None
            }