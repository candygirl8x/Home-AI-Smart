import sys
import random
import importlib
from typing import TYPE_CHECKING

# Allow linters/type-checkers to see the pyttsx3 import during type checking
if TYPE_CHECKING:  # pragma: no cover - only for static analysis
    import pyttsx3  # type: ignore

# Cross-platform TTS setup
# Import pyttsx3 dynamically at runtime so IDEs that can't resolve the
# package won't raise errors and environments without the package fall back.
if sys.platform == 'win32':
    try:
        pyttsx3 = importlib.import_module('pyttsx3')
        engine = pyttsx3.init()
        TTS_AVAILABLE = True
    except Exception:
        # pyttsx3 may not be installed in the environment; fall back gracefully
        pyttsx3 = None
        engine = None
        TTS_AVAILABLE = False
        print("TTS not available: pyttsx3 import/init failed")
else:
    pyttsx3 = None
    engine = None
    TTS_AVAILABLE = False
    print("TTS not available on this platform (Linux/Render)")

# List of funny/clever responses (for when TTS is not available)
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