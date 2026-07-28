import sys
import random
import importlib

# Cross-platform TTS setup - only import on Windows
if sys.platform == 'win32':
    try:
        pyttsx3 = importlib.import_module('pyttsx3')
        engine = pyttsx3.init()
        TTS_AVAILABLE = True
    except (ImportError, ModuleNotFoundError):
        pyttsx3 = None
        engine = None
        TTS_AVAILABLE = False
        print("pyttsx3 not installed; TTS disabled.")
else:
    # On Linux/Render, don't even try to import pyttsx3
    pyttsx3 = None
    engine = None
    TTS_AVAILABLE = False
    print("TTS not available on this platform (Linux/Render)")

# List of funny/clever responses
RESPONSES = [
    "Smart Home AI is ready!",
    "Welcome back!",
    "All systems are operational.",
    "How can I assist you today?",
    "Smart Home AI activated!",
    "Ready to serve."
]

def speak(text):
    """
    Cross-platform text-to-speech function.
    Works on Windows with pyttsx3, falls back to print on Linux/Render.
    """
    if TTS_AVAILABLE and pyttsx3:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
            print(f"TTS (fallback): {text}")
    else:
        # Linux/Render fallback - just print
        print(f"TTS: {text}")

def random_response():
    """Returns a random response for when TTS is not available"""
    return random.choice(RESPONSES)

def speak_random():
    """Speaks a random response"""
    response = random_response()
    speak(response)
    return response

# Test if running directly
if __name__ == "__main__":
    speak("Testing cross-platform TTS")
    speak_random()