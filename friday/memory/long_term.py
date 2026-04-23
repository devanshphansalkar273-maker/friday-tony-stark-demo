import sqlite3
import json
from pathlib import Path

class LongTermMemory:
    def __init__(self, db_path: str = "friday/memory/long_term.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY, key TEXT, value TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')
        self.conn.commit()
    
    def store(self, data: str):
        key = data[:50]  # Truncate key
        self.conn.execute('INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)', (key, data))
        self.conn.commit()
    
    def retrieve(self, query: str) -> str:
        cur = self.conn.execute('SELECT value FROM memory WHERE key LIKE ? ORDER BY timestamp DESC LIMIT 5', (f'%{query}%',))
        return '\n'.join(row[0] for row in cur.fetchall())

