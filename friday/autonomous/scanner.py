import pandas as pd
import numpy as np
from friday.intelligence.indicators import rsi, macd, sma
from friday.intelligence.strategy import load_data

def scan_events(df: pd.DataFrame, threshold_vol=1.5, threshold_drop=0.05) -> list:
    df = load_data()
    df['returns'] = df.groupby('symbol')['close'].pct_change()
    df['vol_ma'] = df.groupby('symbol')['volume'].rolling(20).mean().reset_index(0, drop=True)
    df['vol_spike'] = df['volume'] / df['vol_ma'] > threshold_vol
    df['sudden_drop'] = df['returns'] < -threshold_drop
    df['rsi_low'] = rsi(df.groupby('symbol')['close']) < 30
    macd_l, sig, hist = macd(df.groupby('symbol')['close'])
    df['macd_cross'] = (hist.shift(1) < 0) & (hist > 0)  # Bull cross
    
    events = df[(df['vol_spike'] | df['sudden_drop'] | df['macd_cross'])].tail(10)
    return events.to_dict('records')

