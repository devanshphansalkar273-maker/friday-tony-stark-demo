from core.router import route_command
from llm.local_llm import generate_response

def handle_input(user_input):
    action = route_command(user_input)

    if action:
        return action

    return generate_response(user_input)
