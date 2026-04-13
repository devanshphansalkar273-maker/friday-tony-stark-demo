"""
Memory-aware prompt templates.
"""
from friday.memory.retrieve import recall

def register(mcp):
    @mcp.prompt()
    def memory_recall(query: str, user_id: str = "boss") -> str:
        \"\"\"
        BEFORE every response, recall relevant memories and inject.
        LLM will see this context.
        \"\"\"
        memories = recall(query, user_id=user_id)
        if memories == "No relevant memories found, boss.":
            return ""
        return f"""RELEVANT USER MEMORIES:
{memories}

Personalize response using these. If irrelevant, ignore."""

