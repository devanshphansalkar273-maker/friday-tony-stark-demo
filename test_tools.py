import sys
sys.path.insert(0, 'friday')

from friday.core.agent import StarkAgent

a = StarkAgent()

cmds = [
    'open notepad',
    'list files',
    'create file test.txt with hello',
    'search AI news',
    'hello friday'
]

for cmd in cmds:
    print(f"CMD: {cmd}")
    print(f"RESP: {a.process_input(cmd)}")
    print("---")
