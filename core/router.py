from system.actions import open_notepad, shutdown

def route_command(text):
    text = text.lower()

    if "open notepad" in text:
        open_notepad()
        return "Opening Notepad"

    if "shutdown" in text:
        shutdown()
        return "Shutting down system"

    return None
