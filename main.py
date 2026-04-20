from core.agent import handle_input

def main():
    print("FRIDAY is running...")

    while True:
        user_input = input("You: ")

        response = handle_input(user_input)

        print("FRIDAY:", response)

if __name__ == "__main__":
    main()
