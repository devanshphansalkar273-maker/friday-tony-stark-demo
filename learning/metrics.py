import sqlite3
from .logger import DB_PATH, logger


def calculate_accuracy():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN (predicted_return > 0 AND actual_return > 0) OR (predicted_return < 0 AND actual_return < 0) THEN 1 ELSE 0 END) as correct
        FROM trades WHERE actual_return IS NOT NULL
    """)
    result = c.fetchone()
    conn.close()
    if result[0] == 0:
        return 0.0
    return result[1] / result[0]


def calculate_win_rate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM trades WHERE actual_return > 0 AND actual_return IS NOT NULL")
    wins = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM trades WHERE actual_return IS NOT NULL")
    total = c.fetchone()[0]
    conn.close()
    return wins / total if total > 0 else 0.0


def average_profit():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT AVG(actual_return) FROM trades WHERE actual_return IS NOT NULL")
    avg = c.fetchone()[0] or 0.0
    conn.close()
    return avg


def show_stats():
    """Alias for print_stats."""
    print_stats()


def print_stats():
    accuracy = calculate_accuracy()
    win_rate = calculate_win_rate()
    avg_profit = average_profit()
    print("=== AI PERFORMANCE ===")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Win Rate: {win_rate:.2%}")
    print(f"Avg Profit: {avg_profit:.4f}")
    logger.info(f"Stats - Acc: {accuracy:.2%}, Win: {win_rate:.2%}, AvgP: {avg_profit:.4f}")


if __name__ == "__main__":
    from logger import init_db, log_decision
    from evaluator import evaluate_trade
    init_db()
    tid = log_decision("MSFT", "buy", 0.04, 0.85)
    evaluate_trade(tid, 0.06)
    print_stats()

