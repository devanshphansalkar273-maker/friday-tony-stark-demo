import sqlite3

DB_PATH = "friday/learning/feedback.db"

def calculate_score(symbol, conf, actual_return):
    if actual_return > 0.01:  # Profitable
        score = conf / 100  # Normalize
    elif actual_return < -0.01:
        score = -conf / 100
    else:
        score = 0
    return score

def evaluate_all():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, symbol, conf, actual_return FROM predictions WHERE actual_return IS NOT NULL AND score IS NULL")
    rows = c.fetchall()
    for row in rows:
        id_, symbol, conf, actual_return = row
        score = calculate_score(symbol, conf, actual_return)
        c.execute("UPDATE predictions SET score = ? WHERE id = ?", (score, id_))
    conn.commit()
    conn.close()
    print("Evaluated pending outcomes.")

