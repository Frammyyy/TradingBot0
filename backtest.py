import yfinance as yf
import pandas as pd
from STRATS import strat
import pytz

PAIR_CONFIG = {
    'EURUSD=X': {
        'rsi_period': 10,
        'rsi_up': 70,
        'rsi_down': 30,
        'ema_short': 12,
        'ema_long': 26,
        'sl_pct': 0.02,
        'tp_pct': 0.015,
        'position_size': 1000
    },
    'GBPUSD=X': {
        'rsi_period': 14,
        'rsi_up': 65,
        'rsi_down': 35,
        'ema_short': 10,
        'ema_long': 30,
        'sl_pct': 0.01,
        'tp_pct': 0.02,
        'position_size': 800
    },
    'USDCAD=X': {
        'rsi_period': 20,
        'rsi_up': 65,
        'rsi_down': 35,
        'ema_short': 12,
        'ema_long': 26,
        'sl_pct': 0.01,
        'tp_pct': 0.01,
        'position_size': 800
    }
}

# --- SETTINGS ---
SYMBOLS = list(PAIR_CONFIG.keys())
INTERVAL = '5m'
FETCH_PERIOD = '60d'
INITIAL_BALANCE = 100
SLIPPAGE = 0.001
START_TIME = 8
END_TIME = 18


def get_data(symbol):
    df = yf.download(symbol, period=FETCH_PERIOD, interval=INTERVAL)
    df.dropna(inplace=True)
    df.columns = df.columns.get_level_values(0)
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    df['Symbol'] = symbol
    return strat.calculate_indicators(df, symbol)


def main():
    eastern = pytz.timezone('US/Eastern')
    global_balance = INITIAL_BALANCE
    trades = []

    # Load and combine data
    dfs = [get_data(sym) for sym in SYMBOLS]
    combined = pd.concat(dfs)
    combined.sort_index(inplace=True)

    # Per-symbol state
    symbol_state = {
        sym: {
            'in_position': False,
            'position_type': None,
            'entry_price': None
        } for sym in SYMBOLS
    }

    for idx, row in combined.iterrows():
        symbol = row['Symbol']
        local_time = idx.tz_convert(eastern)
        if local_time.hour < START_TIME or local_time.hour >= END_TIME:
            continue

        state = symbol_state[symbol]
        cfg = PAIR_CONFIG[symbol]
        close_price = row['Close']

        # ENTRY
        if not state['in_position']:
            symbol_df = combined[combined['Symbol'] == symbol]
            if idx not in symbol_df.index:
                continue
            row_index = symbol_df.index.get_loc(idx)
            signal = strat.generate_entry_signal(symbol_df, index=row_index, symbol=symbol)
            if signal == "BUY":
                state.update({'in_position': True, 'position_type': 'long', 'entry_price': close_price})
                trades.append({'Date': idx, 'Type': 'Buy', 'Price': close_price, 'Symbol': symbol})
            elif signal == "SELL":
                state.update({'in_position': True, 'position_type': 'short', 'entry_price': close_price})
                trades.append({'Date': idx, 'Type': 'Short Sell', 'Price': close_price, 'Symbol': symbol})

        # EXIT
        else:
            entry_price = state['entry_price']
            position_type = state['position_type']
            stop_loss = entry_price * (1 - cfg['sl_pct']) if position_type == "long" else entry_price * (
                        1 + cfg['sl_pct'])
            take_profit = entry_price * (1 + cfg['tp_pct']) if position_type == "long" else entry_price * (
                        1 - cfg['tp_pct'])

            signal_df = combined[combined['Symbol'] == symbol]
            try:
                i = signal_df.index.get_loc(idx)
            except KeyError:
                continue

            exit_trade, reason = strat.generate_exit_signal(signal_df, index=i, position_type=position_type,
                                                            symbol=symbol)

            if not exit_trade:
                if position_type == "long" and close_price <= stop_loss:
                    reason, exit_trade = "Stop Loss", True
                elif position_type == "long" and close_price >= take_profit:
                    reason, exit_trade = "Take Profit", True
                elif position_type == "short" and close_price >= stop_loss:
                    reason, exit_trade = "Stop Loss", True
                elif position_type == "short" and close_price <= take_profit:
                    reason, exit_trade = "Take Profit", True

            if exit_trade:
                if position_type == "long":
                    exit_price = close_price - SLIPPAGE
                    profit = ((exit_price - entry_price) * cfg['position_size'])
                else:
                    exit_price = close_price + SLIPPAGE
                    profit = ((entry_price - exit_price) * cfg['position_size'])

                # Adjust profit to USD if quote currency is not USD (like JPY pairs)
                if not (symbol.endswith("USD=X")):
                    profit /= exit_price  # Convert from quote to USD

                commission = max(0.000035 * cfg['position_size'] * close_price, 0.01)
                profit -= commission
                global_balance += profit

                trades.append({
                    'Date': idx,
                    'Type': 'Sell' if position_type == "long" else 'Buy to Cover',
                    'Price': close_price,
                    'Profit': profit,
                    'Balance': global_balance,
                    'Reason': reason,
                    'Symbol': symbol
                })

                print(
                    f"Exit trade on {idx}: {position_type} exit for {profit:.2f}, Balance: {global_balance:.2f}, "
                    f"Reason: {reason}")
                state.update({'in_position': False, 'position_type': None, 'entry_price': None})

    # Export results
    result_df = pd.DataFrame(trades)
    if not result_df.empty:
        result_df['Date'] = result_df['Date'].dt.tz_localize(None)
        result_df.to_excel("rsi_backtest_results.xlsx", index=False)
        print("\n✅ Final Balance from Trade Log: ${:.2f}".format(global_balance))
    else:
        print("\n⚠️ No trades executed.")


if __name__ == "__main__":
    main()
