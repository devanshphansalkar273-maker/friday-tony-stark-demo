import sqlite3
import logging
from .logger import DB_PATH, logger

def evaluate_trade(trade_id, actual_return):
    \"\"\"Update trade outcome and log evaluation.\"\"\"
    update_outcome(trade_id, actual_return)
    profit_loss = 'profit' if actual_return > 0 else 'loss'
    logger.info(f"Trade {trade_id} evaluation: {profit_loss} (actual_return={actual_return})")

def evaluate_all():
    \"\"\"Evaluate all pending trades (simplified - assume actuals available).\"\"\"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, predicted_return, actual_return FROM trades WHERE actual_return IS NULL")
    pending = c.fetchall()
    conn.close()
    for trade_id, pred, _ in pending:
        # Simulate actual for demo
        actual = pred + (0.01 if pred > 0 else -0.01)  # Simple bias
        evaluate_trade(trade_id, actual)
    logger.info(f"Evaluated {len(pending)} trades.")

def print_pending():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM trades WHERE actual_return IS NULL")
    pending = c.fetchall()
    conn.close()
    logger.info(f"Pending evaluations: {len(pending)}")
    for trade in pending:
        logger.info(trade)

if __name__ == "__main__":
    from logger import init_db, log_decision
    init_db()
    tid = log_decision("GOOG", "sell", -0.03, 0.7)
    evaluate_trade(tid, 0.02)
