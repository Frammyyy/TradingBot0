import pandas as pd

def calculate_macd(df, short=12, long=26, signal=9):
    """
    Calculates MACD, Signal Line, and Histogram and adds them as columns to the input DataFrame.

    Parameters:
    - df: pandas DataFrame containing at least a 'Close' column
    - short: period for the short-term EMA (default = 12)
    - long: period for the long-term EMA (default = 26)
    - signal: period for the signal line EMA (default = 9)

    Returns:
    - df: DataFrame with new columns: 'MACD_EMA_short', 'MACD_EMA_long', 'MACD', 'Signal_Line', 'MACD_Hist'
    """

    df['MACD_EMA_short'] = df['Close'].ewm(span=short, adjust=False).mean()
    df['MACD_EMA_long'] = df['Close'].ewm(span=long, adjust=False).mean()
    df['MACD'] = df['MACD_EMA_short'] - df['MACD_EMA_long']
    df['Signal_Line'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['Signal_Line']

    return df


def generate_signal(df, index=-1):
    """
    Generates a simple MACD-based trading signal: BUY, SELL, or HOLD.

    Parameters:
    - df: pandas DataFrame that already contains 'MACD_Hist' column
    - index: the row index to check for the signal (default = -1, i.e., the latest row)

    Returns:
    - String: "BUY" if bullish crossover, "SELL" if bearish crossover, otherwise "HOLD"
    """
    if index < 1 or index >= len(df):
        return "HOLD"

    prev_hist = df['MACD_Hist'].iloc[index - 1]
    curr_hist = df['MACD_Hist'].iloc[index]

    # 🟢 BUY Signal: Histogram crossed from negative to positive (MACD crossed above Signal)
    if (prev_hist < 0) and (curr_hist > 0):
        return "BUY"

    # 🔴 SELL Signal: Histogram crossed from positive to negative (MACD crossed below Signal)
    elif (prev_hist > 0) and (curr_hist < 0):
        return "SELL"

    # 🟡 HOLD Signal: No meaningful crossover
    else:
        return "HOLD"
