"""Memory facade for simple key-value + conversation history."""

from .store import store_memory, retrieve_memory

class Memory:
    def __init__(self):
        self.history = []

    def remember(self, key: str, value: str):
        store_memory(f"{key}: {value}")
        self.history.append(f"{key}: {value}")

    def recall(self, text: str) -> str:
        return retrieve_memory(text)

    def get_context(self) -> str:
        # Return last 5 items of history as context
        return ' | '.join(self.history[-5:])

memory = Memory()
