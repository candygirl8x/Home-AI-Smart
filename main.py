import speech_recognition as sr

from automation import AutomationManager
from commands import process_command


print("Smart Home AI Started")

automation = AutomationManager()

recognizer = sr.Recognizer()


while True:

    try:

        with sr.Microphone(device_index=1) as source:

            print("\nListening...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=5
            )


        text = recognizer.recognize_google(audio)

        print("Command:", text)


        process_command(
            text,
            automation
        )


    except sr.WaitTimeoutError:

        print("No voice detected")


    except sr.UnknownValueError:

        print("Could not understand")


    except KeyboardInterrupt:

        print("Assistant stopped")
        break


    except Exception as e:

        print("Error:", e)