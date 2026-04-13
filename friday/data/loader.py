import pandas as pd
from .validator import validate_data
import os

DATA_PATH = "friday/intelligence/data/sim_daily.csv"

def load_clean_data():
    df = pd.read_csv(DATA_PATH)
    df = validate_data(df)
    df = df.fillna(method='ffill').dropna()
    return df

