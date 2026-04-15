import pyautogui
import os
import time
from datetime import datetime

# Safety settings
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort

def take_screenshot() -> str:
    """Take a screenshot and return the path."""
    log_dir = "logs/screenshots"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{log_dir}/screenshot_{timestamp}.png"
    
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return f"Screenshot saved to {filename}"

def type_text(text: str) -> str:
    """Type text using the keyboard."""
    # Small delay to ensure the window is focused
    time.sleep(0.5)
    pyautogui.write(text, interval=0.1)
    return f"Typed: '{text}'"

def press_key(key: str) -> str:
    """Press a specific key (e.g., 'enter', 'tab')."""
    pyautogui.press(key)
    return f"Pressed {key}"

def click_current_pos() -> str:
    """Perform a mouse click at current position."""
    pyautogui.click()
    return "Click performed."

def move_mouse(x: int, y: int) -> str:
    """Move mouse to absolute coordinates."""
    pyautogui.moveTo(x, y, duration=0.5)
    return f"Moved mouse to {x}, y"

def get_mouse_pos() -> str:
    """Get current mouse coordinates."""
    x, y = pyautogui.position()
    return f"Mouse is at {x}, {y}"
