# pyright: reportMissingImports=false
try:
    import speech_recognition as sr
except ImportError as e:
    print("Error: speech_recognition module not found.")
    print("Install it using: pip install SpeechRecognition")
    exit(1)

print("Available microphones:\n")

for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {name}")