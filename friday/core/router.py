from typing import Tuple

def route_command(text: str) -> Tuple[str, str] | str:
    """Tool-using router. Returns ('tool_name', 'arg_str') or 'llm'."""
    text_lower = text.lower().strip()

    if 'open ' in text_lower:
        parts = text.split('open ', 1)
        app = parts[1].strip() if len(parts) > 1 else ''
        return 'open_app', app

    if 'close ' in text_lower:
        parts = text.split('close ', 1)
        app = parts[1].strip() if len(parts) > 1 else ''
        return 'close_app', app

    if 'shutdown' in text_lower:
        return 'shutdown', ''

    if 'restart' in text_lower:
        return 'restart', ''

    if 'list files' in text_lower:
        parts = text_lower.split('list files in ', 1)
        path = parts[1].strip() if len(parts) > 1 else '.'
        return 'list_files', path

    if 'delete file ' in text_lower:
        parts = text_lower.split('delete file ', 1)
        path = parts[1].strip() if len(parts) > 1 else ''
        return 'delete_file', path

    if 'read file ' in text_lower:
        parts = text_lower.split('read file ', 1)
        path = parts[1].strip() if len(parts) > 1 else ''
        return 'read_file', path

    if 'create file ' in text_lower:
        rest = text_lower.split('create file ', 1)[1]
        parts = rest.split(' with ', 1)
        path = parts[0].strip()
        content = parts[1].strip() if len(parts) > 1 else ''
        return 'create_file', f"{path}|{content}"

    if 'search ' in text_lower:
        parts = text.split('search ', 1)
        query = parts[1].strip() if len(parts) > 1 else ''
        return 'web_search', query

    if 'add task' in text_lower:
        parts = text.split('add task ', 1)
        arg = parts[1].strip() if len(parts) > 1 else ''
        return 'add_task', arg

    if 'write code ' in text_lower or 'code for ' in text_lower or 'program to ' in text_lower:
        # Extract editor and task
        words = text_lower.split()
        editor = 'notepad'
        task = text
        for i, word in enumerate(words):
            if word in ['notepad', 'vscode', 'code', 'codeblocks']:
                editor = word.replace('codeblocks', 'codeblocks.exe')
                task = ' '.join(words[i+1:])
                break
        return 'write_code', f"{editor}|{task}"
    
    return 'llm'

