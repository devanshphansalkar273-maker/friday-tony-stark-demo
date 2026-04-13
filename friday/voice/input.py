import speech_recognition as sr

r = sr.Recognizer()

def listen() -> str:
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = r.listen(source, timeout=5)
    try:
        text = r.recognize_google(audio)  # Local fallback whisper later
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("Speech service error - use text.")
        return ""

