"""Learning facade for usage tracking and improvement."""

from .logger import log_decision
from .trainer import retrain_model
from .metrics import print_stats

class LearningSystem:
    def __init__(self):
        self.usage_count = 0

    def track_usage(self, action: str):
        self.usage_count += 1
        log_decision('SYSTEM', action, 1.0, 1.0)  # Log system actions

    def improve(self):
        retrain_model()
        print_stats()

    def log_trade(self, symbol: str, decision: str, pred_return: float, conf: float):
        log_decision(symbol, decision, pred_return, conf)

learning = LearningSystem()
