from ta.momentum import RSIIndicator

RSI_UP = 70
RSI_DOWN = 30


def calculate_rsi(df, period=14):
    """
    Calculate RSI indicator and add it as a column to the DataFrame.
    Args:
        df (pd.DataFrame): DataFrame with at least a 'Close' column.
        period (int): Period for RSI calculation (default 14).
    Returns:
        pd.DataFrame: DataFrame with new 'RSI' column.
    """
    df['RSI'] = RSIIndicator(close=df['Close'], window=period).rsi()
    return df


def generate_signal(df, index=None, symbol="", rsi_up=RSI_UP, rsi_down=RSI_DOWN):
    """
    Generate a signal based on RSI values at a specific index.

    Args:
        df (pd.DataFrame): DataFrame containing 'RSI' column.
        index (int): The row index to evaluate. If None or out of bounds, returns "HOLD".
        symbol (str): Symbol name (optional, not used here).
        rsi_up (float): RSI threshold for sell signal.
        rsi_down (float): RSI threshold for buy signal.

    Returns:
        str: "BUY", "SELL", or "HOLD" signal.
    """
    if index is None or index < 0 or index >= len(df):
        return "HOLD"

    rsi_value = df['RSI'].iloc[index]

    if rsi_value < rsi_down:
        return "BUY"
    elif rsi_value > rsi_up:
        return "SELL"
    else:
        return "HOLD"
