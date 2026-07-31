import threading
import pyttsx3

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class VoiceAssistant:

    def __init__(self):

        if sr is None:
            raise ImportError(
                "Install SpeechRecognition:\n\npip install SpeechRecognition"
            )

        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        print("\nAvailable microphones:\n")

        microphones = sr.Microphone.list_microphone_names()

        for i, mic in enumerate(microphones):
            print(i, mic)

        index = None

        for i, mic in enumerate(microphones):
            if "External Mic" in mic:
                index = i
                break

        if index is None:
            for i, mic in enumerate(microphones):
                if "Microphone Array" in mic:
                    index = i
                    break

        try:
            self.microphone = sr.Microphone(device_index=index)

            if index is not None:
                print("\nUsing microphone:", microphones[index])
            else:
                print("\nUsing default microphone")

        except Exception as e:
            print("Microphone Error:", e)
            self.microphone = None

        # Lock prevents multiple speech calls at once
        self.tts_lock = threading.Lock()

    def adjust_noise(self):

        if self.microphone is None:
            return

        try:
            with self.microphone as source:

                print("Adjusting microphone...")

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                print("Ready!")

        except Exception as e:
            print("Noise Adjustment Error:", e)

    def speech_to_text(self):

        if self.microphone is None:
            return ""

        try:
            with self.microphone as source:

                print("\nListening...")

                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=8
                )

            print("Recognizing...")

            text = self.recognizer.recognize_google(audio)

            print("You said:", text)

            return text.lower()

        except sr.WaitTimeoutError:
            print("No speech detected.")
            return ""

        except sr.UnknownValueError:
            print("Could not understand.")
            return ""

        except Exception as e:
            print("Speech Error:", e)
            return ""

    def text_to_speech(self, text):

        print("Speaking:", text)

        with self.tts_lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", 160)

                engine.say(text)
                engine.runAndWait()
                engine.stop()

            except Exception as e:
                print("TTS Error:", e)

    def get_voice_input(self):

        self.adjust_noise()

        return self.speech_to_text()