import os
import shutil
import glob
from pathlib import Path
from typing import List

def create_file(path: str, content: str = '') -> str:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)
    return f\"Created {path}\"

def delete_file(path: str) -> str:
    if os.path.exists(path):
        os.remove(path)
        return f\"Deleted {path}\"
    return \"File not found.\"

def move_file(src: str, dst: str) -> str:
    shutil.move(src, dst)
    return f\"Moved {src} to {dst}\"

def search_files(pattern: str, path: str = '.') -> List[str]:
    return glob.glob(os.path.join(path, '**', pattern), recursive=True)

def read_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return \"File not found.\"

if __name__ == '__main__':
    print(search_files('*.py', '.'))

