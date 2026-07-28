import speech_recognition as sr

recognizer = sr.Recognizer()

with sr.Microphone(device_index=1) as source:
    print("Adjusting noise...")
    recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Speak now...")
    audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)

print("Processing...")

try:
    text = recognizer.recognize_google(audio)
    print("You said:", text)

    # Voice command processing
    command = text.lower()

    if "light on" in command:
        print("Turning ON light")

    elif "light off" in command:
        print("Turning OFF light")

    elif "open door" in command:
        print("Opening door")

    else:
        print("Command not recognized")

except sr.UnknownValueError:
    print("Could not understand your voice")

except sr.RequestError as e:
    print("Google API error:", e)