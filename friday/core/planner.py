from friday.llm.local_llm import generate_response
from friday.tools.tools import get_tools
import json
import re

def plan_task(user_input: str, context: str = "") -> list:
    """LLM planner: Generate JSON step plan."""
    tools = list(get_tools().keys())
    tools_str = ', '.join(tools)
    
    prompt = """User request: """ + user_input + """

Context: """ + context + """

Available tools: """ + tools_str + """

Plan in JSON array of steps:
[
  {"step": 1, "tool": "tool_name", "args": "arg_string"},
  ...
]

Rules:
- Break complex tasks into steps
- Use tools for actions
- Args: string for tool input
- End with final step if needed
- Simple requests: single step or 'llm'

Output ONLY valid JSON array, no other text."""

    response = generate_response(prompt)
    
    # Extract JSON
    json_match = re.search(r'\[.*?\]', response, re.DOTALL)
    if json_match:
        try:
            plan = json.loads(json_match.group())
            return plan if isinstance(plan, list) else []
        except:
            pass
    
    # Fallback
    return [{"step": 1, "tool": "llm", "args": user_input}]

