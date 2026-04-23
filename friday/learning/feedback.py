import json
from pathlib import Path

FEEDBACK_DB = Path("friday/learning/feedback.json")

class FeedbackTracker:
    def __init__(self):
        self.db = self.load_db()
    
    def load_db(self):
        if FEEDBACK_DB.exists():
            with open(FEEDBACK_DB) as f:
                return json.load(f)
        return {}
    
    def save_db(self):
        with open(FEEDBACK_DB, 'w') as f:
            json.dump(self.db, f)
    
    def track_tool(self, tool: str, success: bool, context: str = ""):
        if tool not in self.db:
            self.db[tool] = {"success": 0, "fail": 0, "conf": 0.5}
        if success:
            self.db[tool]["success"] += 1
        else:
            self.db[tool]["fail"] += 1
        total = self.db[tool]["success"] + self.db[tool]["fail"]
        self.db[tool]["conf"] = self.db[tool]["success"] / total if total > 0 else 0.5
        self.save_db()
    
    def get_tool_conf(self, tool: str) -> float:
        return self.db.get(tool, {"conf": 0.5})["conf"]

