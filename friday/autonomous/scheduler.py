import threading
import time
from friday.learning.evaluator import evaluate_all
from friday.learning.trainer import retrain_model

def learning_loop():
    while True:
        evaluate_all()
        retrain_model()
        time.sleep(600)  # 10 min

def start_learning_loop():
    thread = threading.Thread(target=learning_loop, daemon=True)
    thread.start()
    print("Learning loop started in background.")

class Scheduler:
    def start(self):
        start_learning_loop()

scheduler = Scheduler()
