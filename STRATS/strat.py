from STRATS import ema_strat as ema
from STRATS import rsi_strat as rsi
from pair_config import PAIR_CONFIG


def calculate_indicators(df, symbol):
    """
    Calculates all indicators needed for the strategy.
    Adds RSI, EMA_Short, and EMA_Long columns to the DataFrame.
    """
    config = PAIR_CONFIG[symbol]
    df = rsi.calculate_rsi(df, period=config['rsi_period'])
    df = ema.calculate_ema(df, short=config['ema_short'], long=config['ema_long'])
    return df


def generate_entry_signal(df, index, symbol):
    """
    Signal entry if RSI is extreme AND aligned with EMA trend.
    - BUY means entering a long position
    - SELL means entering a short position (short selling)
    - HOLD means no action

    BUY if RSI < rsi_down AND trend is bullish
    SELL if RSI > rsi_up AND trend is bearish (short entry)
    """
    config = PAIR_CONFIG[symbol]
    rsi_signal = rsi.generate_signal(df, index=index, rsi_up=config['rsi_up'],
                                     rsi_down=config['rsi_down'])
    trend = ema.get_trend(df, index)

    if rsi_signal == "BUY":     # == "BULL"
        return "BUY"
    elif rsi_signal == "SELL" and trend == "BEAR":
        # SELL here means short entry signal
        return "SELL"
    else:
        return "HOLD"


def generate_exit_signal(df, index, position_type, symbol):
    """
    Exits only on RSI reversal (for now).
    Supports exiting both long and short positions:
    - For longs, exit if RSI sell signal + trend is not bullish
    - For shorts, exit if RSI buy signal + trend is not bearish
    """
    config = PAIR_CONFIG[symbol]

    rsi_signal = rsi.generate_signal(
        df, index=index,
        rsi_up=config['rsi_up'],
        rsi_down=config['rsi_down']
    )
    trend = ema.get_trend(df, index)

    if position_type == "long" and (rsi_signal == "SELL" and trend != "BULL"):
        return True, "RSI Reversal"
    if position_type == "short" and (rsi_signal == "BUY" and trend != "BEAR"):
        return True, "RSI Reversal"
    return False, ""


def get_trend(df, index):
    """
    Optional helper for trend filtering, based on EMA relationship.
    Returns: "BULL", "BEAR", or "FLAT"
    """
    return ema.get_trend(df, index)
