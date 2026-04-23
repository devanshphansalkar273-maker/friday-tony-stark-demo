import speech_recognition as sr

r = sr.Recognizer()

def listen() -> str:
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source, timeout=5)
    try:
        print("Voice input placeholder - install local whisper for offline speech recognition.")
        return ""  # Placeholder - replace with local whisper
    except:
        return ""

