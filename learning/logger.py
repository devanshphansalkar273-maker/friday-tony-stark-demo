import sqlite3
import datetime
import logging
from logging.handlers import RotatingFileHandler
import os

DB_PATH = 'learning/database.db'
LOG_FILE = 'learning/trading.log'

# Setup logging
logger = logging.getLogger('trading')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(LOG_FILE, maxBytes=10**6, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            decision TEXT,
            predicted_return REAL,
            confidence REAL,
            actual_return REAL
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def log_decision(symbol, decision, predicted_return, confidence):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    c.execute('''
        INSERT INTO trades (timestamp, symbol, decision, predicted_return, confidence, actual_return)
        VALUES (?, ?, ?, ?, ?, NULL)
    ''', (timestamp, symbol, decision, predicted_return, confidence))
    conn.commit()
    trade_id = c.lastrowid
    conn.close()
    logger.info(f"Logged decision for {symbol}: {decision}, pred_return={predicted_return}, conf={confidence}, id={trade_id}")
    return trade_id

def update_outcome(trade_id, actual_return):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE trades SET actual_return = ? WHERE id = ?', (actual_return, trade_id))
    conn.commit()
    conn.close()
    logger.info(f"Updated outcome for trade {trade_id}: actual_return={actual_return}")

if __name__ == "__main__":
    init_db()
    log_decision("AAPL", "buy", 0.05, 0.8)
