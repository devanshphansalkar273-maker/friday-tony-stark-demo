from friday.memory.short_term import ShortTermMemory
from friday.memory.long_term import LongTermMemory

class MemoryManager:
    def __init__(self):
        self.short = ShortTermMemory()
        self.long = LongTermMemory()
    
    def add_context(self, data: str):
        self.short.add(data)
        self.long.store(data)
    
    def get_context(self, query: str = "") -> str:
        short_c = self.short.recall()
        long_c = self.long.retrieve(query) if query else ""
        return f"Short-term: {short_c}\nLong-term: {long_c}"
    
    def remember(self, key: str, value: str):
        self.long.store(f"{key}: {value}")

