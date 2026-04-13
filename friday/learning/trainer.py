import pickle
import sqlite3
from friday.intelligence.predictor import train_model
from friday.intelligence.strategy import load_data
from .logger import DB_PATH

MODEL_PATH = "friday/learning/intelligence.model"

def retrain_model():
    df = load_data()
    model = train_model(df)
    
    # Adjust weights based on past scores
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT score FROM predictions WHERE score IS NOT NULL")
    scores = [r[0] for r in c.fetchall()]
    conn.close()
    
    if scores:
        avg_score = sum(scores) / len(scores)
        # Simple adjustment: scale feature weights (stub)
        print(f"Avg score {avg_score:.2f}, model retrained.")
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)

def update_model():
    retrain_model()

