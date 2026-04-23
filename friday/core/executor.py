from friday.tools.tools import TOOLS
from friday.core.agent import StarkAgent

def execute_plan(plan: list, agent: StarkAgent = None) -> str:
    \"\"\"Execute JSON plan steps sequentially, accumulating context.\"\"\"
    context = ""
    results = []
    
    for step in plan:
        tool = step.get("tool", "llm")
        args = step.get("args", "")
        
        if tool == "llm":
            prompt = f"Context: {context}\nTask: {args}"
            result = agent.llm(prompt) if agent else "LLM not available."
        else:
            try:
                func = TOOLS.get(tool)
                if func:
                    result = func(args)
                else:
                    result = f"Tool {tool} not found."
            except Exception as e:
                result = f"Tool error: {str(e)}"
        
        results.append(result)
        context += f"Step {{step}}: {tool}({args}) = {result}\n"
        print(f"Step {step.get('step', '?')}: {tool} -> {result[:100]}...")
    
    return "\n".join(results)

