import pandas as pd
from mcp.server.fastmcp import FastMCP
from .indicators import rsi, macd, sma
from .predictor import train_model, predict
import os

DATA_PATH = "friday/intelligence/data/sim_daily.csv"

def load_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Generate data first: {DATA_PATH}")
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
    df = compute_signals(load_data())
    from .risk_manager import is_safe_trade
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

def explain_decision(symbol: str) -> str:
    df = compute_signals(load_data())
    row = df[df['symbol'] == symbol].iloc[-1]
    expl = f"{symbol}: RSI {row['rsi']:.1f}, MACD {row['macd']:.2f}, SMA ratio {row['sma_ratio']:.2f}. Rule score {row['rule_conf']:.0f}%, ML {row['ml_conf']:.0f}%."
    return expl

def register(mcp):
    @mcp.tool()
    def get_best_stock_tool() -> str:
        \"\"\"
        Get the best stock buy today + top 3 with confidence %.
        \"\"\"
    result = get_best_stock()
    from friday.learning.logger import log_prediction
    log_prediction(result['symbol'], result['combined_conf'])
    return f"Best: {result['symbol']} (${result['close']:.2f}) conf {result['combined_conf']:.1f}%. Top3: {result['top3']}"

    @mcp.tool()
    def explain_stock(symbol: str) -> str:
        \"\"\"
        Explain decision for stock.
        \"\"\"
        return explain_decision(symbol)

