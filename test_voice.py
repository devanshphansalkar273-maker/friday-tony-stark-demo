import time
from friday.voice.input import listen
from friday.voice.output import speak

def test_voice():
    print("--- FRIDAY Voice Verification ---")
    
    # Test Output
    print("Testing Output (TTS)...")
    message = "Greetings boss. I am online and functional. Can you hear me?"
    speak(message)
    print("Done.")
    
    time.sleep(1)
    
    # Test Input
    print("Testing Input (STT)...")
    print("Please say something within 5 seconds.")
    text = listen()
    
    if text:
        print(f"I heard: {text}")
        speak(f"You said: {text}. Voice systems are green.")
    else:
        print("I didn't hear anything or there was an error.")
        speak("I am having trouble hearing you, boss. Please check the microphone.")

if __name__ == "__main__":
    test_voice()
