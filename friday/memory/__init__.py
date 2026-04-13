"""
MCP Memory — persistent user memory layer for FRIDAY.
"""
from friday.memory.store import register as register_store
from friday.memory.retrieve import register as register_retrieve
from friday.memory.summarize import register as register_summarize

def register_all_memory(mcp):
    \"\"\"Register all memory tools/prompts to MCP.\"\"\"
    register_store(mcp)
    register_retrieve(mcp)
    register_summarize(mcp)

