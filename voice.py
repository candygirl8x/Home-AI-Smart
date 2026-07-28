import importlib

try:
    sr = importlib.import_module("speech_recognition")
except ImportError:
    sr = None

try:
    pyttsx3 = importlib.import_module("pyttsx3")
except ImportError:
    pyttsx3 = None


class VoiceAssistant:

    def __init__(self):

        if sr is None:
            raise ImportError("speech_recognition module is required. Install via pip install SpeechRecognition")

        self.recognizer = sr.Recognizer()

        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        print("\nAvailable microphones:\n")

        microphones = sr.Microphone.list_microphone_names()

        for i, mic in enumerate(microphones):
            print(i, mic)

        # Try to use External Mic first
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

            print("\nUsing microphone:")
            print(microphones[index])

        except Exception as e:

            print(e)

            self.microphone = None

        if pyttsx3:

            self.engine = pyttsx3.init()

            self.engine.setProperty("rate", 160)

        else:

            self.engine = None

        self.adjust_noise()

    def adjust_noise(self):

        if self.microphone is None:
            return

        try:

            with self.microphone as source:

                print("Adjusting microphone...")

                self.recognizer.adjust_for_ambient_noise(source, duration=2)

                print("Ready!")

        except Exception as e:

            print(e)

    def speech_to_text(self):

        if self.microphone is None:
            return ""

        try:

            with self.microphone as source:

                print("\nSpeak now...")

                audio = self.recognizer.listen(
                    source,
                    timeout=15,
                    phrase_time_limit=8
                )

            print("Recognizing...")

            text = self.recognizer.recognize_google(audio)

            print("You said:", text)

            return text

        except sr.WaitTimeoutError:

            print("No speech detected.")

            return ""

        except sr.UnknownValueError:

            print("Could not understand.")

            return ""

        except Exception as e:

            print(e)

            return ""

    def text_to_speech(self, text):

        print("Assistant:", text)

        if self.engine:

            self.engine.say(text)

            self.engine.runAndWait()

    def get_voice_input(self, prompt="I'm listening..."):

        print(prompt)

        return self.speech_to_text()