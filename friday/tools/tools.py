"""
Tool Registry: Central dictionary of all available tools.
Each tool is a callable function that takes args and returns str response.
"""

from typing import Callable, Dict
from friday.system.actions import open_app, close_app, shutdown, restart
from friday.system.files import create_file, delete_file, read_file, list_files
from friday.tools.web import web_search  # implemented next
from friday.automation.scheduler import add_task

TOOLS: Dict[str, Callable] = {
    "open_app": open_app,
    "close_app": close_app,
    "shutdown": shutdown,
    "restart": restart,
    "create_file": create_file,
    "delete_file": delete_file,
    "read_file": read_file,
    "web_search": web_search,
"add_task": add_task,
    "write_code": write_code_in_editor,
    "save_code": save_code_to_file,
    # Add more as implemented

}

def get_tools() -> Dict[str, Callable]:
    """Get the current tools registry."""
    return TOOLS
