def process_command(text, automation):

    command = text.lower().strip()

    print("Processing command:", repr(command))


    if "light on" in command or "lights on" in command:
        print("Light command detected")
        automation.execute_action("LIGHT_ON")


    elif "light off" in command or "lights off" in command:
        print("Light off command detected")
        automation.execute_action("LIGHT_OFF")


    elif "fan on" in command:
        print("Fan on command detected")
        automation.execute_action("FAN_ON")


    elif "fan off" in command:
        print("Fan off command detected")
        automation.execute_action("FAN_OFF")


    elif "door open" in command or "open door" in command:
        print("Door open command detected")
        automation.execute_action("DOOR_OPEN")


    elif "door close" in command or "close door" in command:
        print("Door close command detected")
        automation.execute_action("DOOR_CLOSE")


    else:
        print("Command not recognized")