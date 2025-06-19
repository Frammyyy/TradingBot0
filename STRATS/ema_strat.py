import pandas as pd


def calculate_ema(df, short=12, long=26):
    """
    Calculate short-term and long-term EMAs and add as columns to the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with a 'Close' column.
        short (int): Period for short-term EMA (default 12).
        long (int): Period for long-term EMA (default 26).

    Returns:
        pd.DataFrame: DataFrame with 'EMA_Short' and 'EMA_Long' columns added.
    """
    df["EMA_Short"] = df['Close'].ewm(span=short, adjust=False).mean()
    df["EMA_Long"] = df['Close'].ewm(span=long, adjust=False).mean()
    return df


def generate_signal(df, index=None, symbol=""):
    """
    Generate buy/sell signal based on EMA crossovers at a specific index.

    Args:
        df (pd.DataFrame): DataFrame containing 'EMA_Short' and 'EMA_Long' columns.
        index (int): Row index to evaluate. Requires index >= 1.
        symbol (str): Symbol name (optional, not used here).

    Returns:
        str: "BUY", "SELL", or "HOLD" signal.
    """
    if index is None or index < 1 or index >= len(df):
        return "HOLD"

    prev_short = df['EMA_Short'].iloc[index - 1]
    prev_long = df['EMA_Long'].iloc[index - 1]
    curr_short = df['EMA_Short'].iloc[index]
    curr_long = df['EMA_Long'].iloc[index]

    if prev_short < prev_long and curr_short > curr_long:
        return "BUY"
    elif prev_short > prev_long and curr_short < curr_long:
        return "SELL"
    else:
        return "HOLD"


def get_trend(df, index):
    """
    Returns trend based on EMA relationship.

    Args:
        df (pd.DataFrame): DataFrame with 'EMA_Short' and 'EMA_Long'.
        index (int): Row index to evaluate (can be 0).

    Returns:
        str: "BULL" if EMA_Short > EMA_Long,
             "BEAR" if EMA_Short < EMA_Long,
             "FLAT" if equal,
             "NONE" if index is invalid.
    """
    if index < 0 or index >= len(df):
        return "NONE"
    if df["EMA_Short"].iloc[index] > df["EMA_Long"].iloc[index]:
        return "BULL"
    elif df["EMA_Short"].iloc[index] < df["EMA_Long"].iloc[index]:
        return "BEAR"
    else:
        return "FLAT"
