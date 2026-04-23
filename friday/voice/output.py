import pyttsx3

engine = None

def init_speech():
    global engine
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        print("Speech engine initialized.")
    except Exception as e:
        print(f"Speech init error: {e}")
        engine = None

def speak(text: str):
    global engine
    try:
        if engine is None:
            init_speech()
        if engine:
            engine.say(text)
            engine.runAndWait()
            print(f"Spoke: {text}")
        else:
            print(f"No speech engine, text: {text}")
    except Exception as e:
        print(f"Speech error: {e}")

