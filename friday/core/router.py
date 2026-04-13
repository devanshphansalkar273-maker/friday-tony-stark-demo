def route_command(text: str):
    if 'stock' in text or 'trade' in text:
        return 'intelligence'
    if 'remember' in text:
        return 'memory'
    if 'news' in text:
        return 'web'
    return 'llm'

