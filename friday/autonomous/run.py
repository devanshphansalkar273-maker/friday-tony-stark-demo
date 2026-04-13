import sys
from friday.config import config
from .scheduler import start_scheduler

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'off':
        print("Autonomous mode OFF")
        sys.exit(0)
    print("Autonomous scanner ON - Ctrl+C to stop")
    start_scheduler()

