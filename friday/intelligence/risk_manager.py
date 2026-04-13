def calculate_position_size(account_balance: float = 100000, conf: float = 0.8, risk_per_trade: float = 0.02) -> float:
    \"\"\"
    Kelly Criterion inspired position sizing.
    Max 2% risk per trade.
    \"\"\"
    risk_amount = account_balance * risk_per_trade
    position_size = risk_amount / (1 - conf)  # Simplified
    return min(position_size, account_balance * 0.1)  # Max 10%

def stop_loss(current_price: float, low: float) -> float:
    \"\"\"
    Dynamic stop loss.
    \"\"\"
    return current_price * 0.95 if low < current_price * 0.98 else low

def is_safe_trade(symbol_conf: float, vol: float) -> bool:
    return symbol_conf > 70 and vol < 3  # Moderate vol

