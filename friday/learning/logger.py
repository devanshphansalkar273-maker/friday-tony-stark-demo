import sqlite3
import datetime
from friday.config import config

DB_PATH = "friday/learning/feedback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY, symbol TEXT, conf REAL, timestamp TEXT, actual_return REAL, score REAL)''')
    conn.commit()
    conn.close()

def log_prediction(symbol, conf):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO predictions (symbol, conf, timestamp) VALUES (?, ?, ?)",
              (symbol, conf, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()


def log_decision(symbol, decision, pred_return, conf):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO predictions (symbol, conf, timestamp, score) VALUES (?, ?, ?, ?)",
              (symbol, conf, datetime.datetime.now().isoformat(), conf))
    conn.commit()
    conn.close()


def update_outcome(symbol, actual_return):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE predictions SET actual_return = ? WHERE symbol = ? AND actual_return IS NULL ORDER BY id DESC LIMIT 1", (actual_return, symbol))
    conn.commit()
    conn.close()

