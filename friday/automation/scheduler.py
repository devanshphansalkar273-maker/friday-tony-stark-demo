import threading
import time
from typing import Callable, Dict

from numpy.random import f
from friday.core.agent import StarkAgent
from friday.learning.metrics import print_stats as show_stats

class Scheduler:
    def __init__(self):
        self.tasks: Dict[str, tuple[Callable, float]] = {}  # name: (func, interval)
        self.agent = StarkAgent()
        self.running = False

    def add_task(self, name: str, func: Callable, interval: float):
        self.tasks[name] = (func, interval)

    def start(self):
        self.running = True
        thread = threading.Thread(target=self._run_loop)
        thread.daemon = True
        thread.start()

    def _run_loop(self):
        while self.running:
            for name, (func, interval) in self.tasks.items():
                # Simple timer
                time.sleep(interval)
                try:
                    func()
                except Exception as e:
                    print(f\"Task {name} error: {e}\")
            time.sleep(1)

    def stop(self):
        self.running = False

# Example tasks
def hourly_check():
    show_stats()
    print(\"Hourly system check complete.\")

scheduler = Scheduler()
scheduler.add_task(\"metrics\", hourly_check, 3600)  # 1 hour

def start_scheduler():
    scheduler.start()

if __name__ == '__main__':
    start_scheduler()
    input(\"Press enter to stop...\")

