import time
from friday.system.actions import open_app
from friday.system.code_writer import generate_code
from friday.automation.gui import type_text
from friday.system.files import create_file

def write_code_in_editor(editor: str, task: str) -> str:
    \"\"\"Open editor, wait, generate code, type it in.\"\"\"
    # Open editor
    open_app(editor)
    
    # Wait for editor to load
    print("Waiting for editor to open...")
    time.sleep(5)
    
    # Generate code
    code = generate_code(task)
    
    # Type the code
    print("Typing code...")
    type_text(code)
    
    return f"Code written in {editor}. Code:\\n{code[:200]}..."

def save_code_to_file(filename: str, task: str) -> str:
    \"\"\"Generate code and save to file, then open in editor."""
    code = generate_code(task)
    create_file(filename, code)
    open_app(filename)
    time.sleep(3)
    return f"Code saved to {filename} and opened."

