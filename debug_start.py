print("1. Testing core.agent import...")
try:
    from core.agent import handle_input
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("2. Testing voice.output import...")
try:
    from voice.output import speak
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("3. Testing voice.input import...")
try:
    from voice.input import listen
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("4. Testing pyttsx3 initialization...")
try:
    import pyttsx3
    engine = pyttsx3.init()
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("5. Testing speech_recognition initialization...")
try:
    import speech_recognition as sr
    r = sr.Recognizer()
    print("   Success.")
except Exception as e:
    print(f"   Failed: {e}")

print("All diagnostic tests complete.")
