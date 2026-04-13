import os
import subprocess
import platform
import pyautogui
from typing import Optional

def open_app(app_name: str) -> str:
    \"\"\"Open application. Windows examples: 'chrome', 'notepad', 'calculator'.\"\"\"
    system = platform.system()
    if system == 'Windows':
        apps = {
            'chrome': 'chrome',
            'notepad': 'notepad',
            'calculator': 'calc',
            'cmd': 'cmd',
            'powershell': 'powershell',
            'explorer': 'explorer'
        }
        cmd = apps.get(app_name.lower(), app_name)
        subprocess.Popen(cmd)
    return f\"Opening {app_name}...\"

def close_app(app_name: str) -> str:
    \"\"\"Close application by name. Uses taskkill on Windows.\"\"\"
    if platform.system() == 'Windows':
        subprocess.run(['taskkill', '/f', '/im', f'{app_name}.exe'], capture_output=True)
    return f\"Closing {app_name}...\"

def shutdown() -> str:
    os.system('shutdown /s /t 30')  # 30s delay
    return \"Shutting down in 30 seconds. Cancel with shutdown /a.\"

def restart() -> str:
    os.system('shutdown /r /t 30')
    return \"Restarting in 30 seconds.\"

def set_volume(level: int) -> str:
    \"\"\"Set volume 0-100. Windows: download nircmd.exe or use powershell.\"\"\"
    # Assume nircmd.exe in PATH or system dir
    subprocess.run(['nircmd.exe', 'changesysvolume', str(level*655)], capture_output=True)
    return f\"Volume set to {level}%\"

def execute_shell(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr

if __name__ == '__main__':
    print(open_app('notepad'))

