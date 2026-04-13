"""
MCP Prompts — reusable prompt templates exposed to the client.
"""

from friday.prompts import templates


def register_all_prompts(mcp):\n    templates.register(mcp)\n    from friday.memory import register_summarize\n    register_summarize(mcp)
