def route_command(text: str) -> str:
    \"\"\"Enhanced router for tool calling. Returns module for execution.\"\"\"
    text_lower = text.lower()
    if any(word in text_lower for word in ['open', 'close', 'app', 'calculator', 'chrome', 'shutdown', 'restart', 'volume', 'shell']):
        return 'system.actions'
    if any(word in text_lower for word in ['create file', 'delete file', 'move file', 'search file', 'read file']):
        return 'system.files'
    if any(word in text_lower for word in ['remember', 'recall', 'memory']):
        return 'memory'
    if 'stock' in text_lower or 'trade' in text_lower:
        return 'intelligence'
    if 'news' in text_lower or 'search web' in text_lower:
        return 'tools.web'
    if 'learn' in text_lower or 'train' in text_lower:
        return 'learning'
    if 'schedule' in text_lower or 'remind' in text_lower:
        return 'automation'
    return 'llm'  # Default LLM response

