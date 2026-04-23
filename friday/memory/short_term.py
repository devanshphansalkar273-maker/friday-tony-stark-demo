class ShortTermMemory:
    def __init__(self, max_items: int = 10):
        self.context = []
        self.max_items = max_items
    
    def add(self, item: str):
        self.context.append(item)
        if len(self.context) > self.max_items:
            self.context.pop(0)
    
    def recall(self) -> str:
        return '\n'.join(self.context[-5:])  # Recent 5

