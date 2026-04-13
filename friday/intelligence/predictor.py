import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from .indicators import rsi, macd, sma

def train_model(data: pd.DataFrame) -> RandomForestClassifier:
    # Synthetic labels: next return >1% = 1 (buy), else 0
    data['returns'] = data.groupby('symbol')['close'].pct_change().shift(-1)
    data['target'] = (data['returns'] > 0.01).astype(int)
    data = data.dropna()

    features = ['rsi', 'macd', 'signal', 'sma_ratio']  # Add more
    X = data[features]
    y = data['target']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model

def predict(model, features: pd.DataFrame) -> pd.DataFrame:
    probs = model.predict_proba(features)[:, 1] * 100  # Buy prob %
    features['confidence'] = probs
    return features

