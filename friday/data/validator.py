import pandas as pd
import numpy as np

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    # Outliers
    q1 = df['close'].quantile(0.25)
    q3 = df['close'].quantile(0.75)
    iqr = q3 - q1
    df = df[(df['close'] >= q1 - 1.5*iqr) & (df['close'] <= q3 + 1.5*iqr)]
    
    # Volume
    df = df[df['volume'] > 0]
    
    # Normalize
    df['close_norm'] = (df['close'] - df['close'].mean()) / df['close'].std()
    
    return df

