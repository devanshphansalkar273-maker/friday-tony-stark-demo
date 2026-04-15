from core.agent import handle_input
from voice.output import speak
from voice.input import listen

def main():
    print("FRIDAY is running...", flush=True)

    while True:
        user_input = listen()

        if not user_input:
            continue

        print("You:", user_input, flush=True)

        response = handle_input(user_input)

        print("FRIDAY:", response, flush=True)
        speak(response)

if __name__ == "__main__":
    main()
