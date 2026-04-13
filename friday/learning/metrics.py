import sqlite3

DB_PATH = "friday/learning/feedback.db"

def calculate_accuracy():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions WHERE score > 0")
    wins = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM predictions WHERE score IS NOT NULL")
    total = c.fetchone()[0]
    conn.close()
    return wins / total if total > 0 else 0

def calculate_win_rate():
    return calculate_accuracy()

def average_profit():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT AVG(actual_return) FROM predictions WHERE actual_return IS NOT NULL")
    avg = c.fetchone()[0]
    conn.close()
    return avg or 0

def print_stats():
    accuracy = calculate_accuracy()
    win_rate = calculate_win_rate()
    avg_profit = average_profit()
    
    print("=== AI PERFORMANCE ===")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM predictions")
    total_trades = c.fetchone()[0]
    conn.close()
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.1%}")
    print(f"Avg Profit: {avg_profit:.1%}")

if __name__ == "__main__":
    print_stats()

