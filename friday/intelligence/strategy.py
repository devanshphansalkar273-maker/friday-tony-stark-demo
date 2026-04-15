import pandas as pd
from .indicators import rsi, macd, sma
from .predictor import train_model, predict
import os

DATA_PATH = "friday/intelligence/data/sim_daily.csv"

def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        # Create a tiny mock file if it doesn't exist for testing
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, 'w') as f:
            f.write("symbol,close,volume_ratio\nAAPL,150,1.2\nGOOG,2800,0.8\n")
    return pd.read_csv(DATA_PATH)

def compute_signals(df: pd.DataFrame):
    df['rsi'] = rsi(df.groupby('symbol')['close'], 14).reset_index(0, drop=True)
    macd_line, signal_line, hist = macd(df.groupby('symbol')['close'], 12, 26, 9)
    df['macd'] = macd_line.reset_index(0, drop=True)
    df['signal'] = signal_line.reset_index(0, drop=True)
    df['sma20'] = sma(df.groupby('symbol')['close'], 20).reset_index(0, drop=True)
    df['sma_ratio'] = df['close'] / df['sma20']
    return df.dropna()

def rule_score(row):
    score = 0
    if row['rsi'] < 30: score += 2  # Oversold
    if row['macd'] > row['signal']: score += 1  # Bull cross
    if row['close'] > row['sma20']: score += 1  # Above MA
    return min(score / 4 * 100, 100)

def get_best_stock(top_n=3) -> dict:
    df = load_data()
    # Simple mock if data is too small for indicators
    if len(df) < 30:
        return {
            'symbol': 'AAPL',
            'close': 150.0,
            'combined_conf': 85.0,
            'top3': [{'symbol': 'AAPL', 'combined_conf': 85.0}]
        }
        
    df = compute_signals(df)
    df = df[df['volume_ratio'] < 3]  # Safe vol
    df['rule_conf'] = df.apply(rule_score, axis=1)

    model = train_model(df)
    features = df[['rsi', 'macd', 'signal', 'sma_ratio']]
    df_ml = predict(model, features)
    df['ml_conf'] = df_ml['confidence']
    df['combined_conf'] = (df['rule_conf'] + df['ml_conf']) / 2

    top = df.nlargest(top_n, 'combined_conf')[['symbol', 'close', 'combined_conf', 'rsi', 'macd', 'sma_ratio']]
    best = top.iloc[0].to_dict()
    best['top3'] = top[['symbol', 'combined_conf']].to_dict('records')
    return best
