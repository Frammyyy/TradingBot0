import time
import pytz
import datetime
import pandas as pd
import os
from STRATS import strat
from pair_config import API, TIME, PAIR_CONFIG
import oandapyV20
# import oandapyV20.endpoints.pricing as pricing  # NOT USED RN
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments  # for historical candles

# --GLOBAL-- #
client = oandapyV20.API(access_token=API['TOKEN'])
ACCOUNT_ID = API['ACCOUNT_ID']
START_TIME = TIME['START']
END_TIME = TIME['END']
LOOPBACK = 100


# --FUNCTIONS-- #
def is_market_open():
    """
    Checks for weekdays and given market hours
    :return: true/false based on the check
    """
    eastern = pytz.timezone("US/Eastern")
    now = datetime.datetime.now(tz=pytz.utc).astimezone(eastern)
    start_time = datetime.datetime.strptime(START_TIME, "%H:%M").time()
    end_time = datetime.datetime.strptime(END_TIME, "%H:%M").time()
    return now.weekday() < 5 and start_time <= now.time() <= end_time


def get_price_data(symbol, lookback=LOOPBACK, granularity="M5"):
    """
    Fetch historical candle close prices for `lookback` periods with given granularity.
    granularity examples: "M1", "M5", "H1", "D"
    :return: a DataFrame with datetime index and 'close' price column.
    """
    try:
        params = {
            "count": lookback,
            "granularity": granularity,
            "price": "M"  # midpoint prices (bid/ask average)
        }
        r = instruments.InstrumentsCandles(instrument=symbol, params=params)
        client.request(r)
        candles = r.response['candles']

        data = []
        for candle in candles:
            if candle['complete']:
                time_str = candle['time']
                close_price = float(candle['mid']['c'])
                data.append({'time': pd.to_datetime(time_str), 'Close': close_price})

        df = pd.DataFrame(data)
        df.set_index('time', inplace=True)
        df.index = df.index.tz_convert('UTC')

        # Calculate indicators with your strat module
        df = strat.calculate_indicators(df, symbol)
        return df

    except Exception as e:
        print(f"[ERROR] Could not fetch historical data for {symbol}: {e}")
        return pd.DataFrame()


def log_trade(trade_type, symbol, qty, price, reason):
    filename = 'trade_log.csv'
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([{
        'timestamp': timestamp,
        'trade_type': trade_type,
        'symbol': symbol,
        'quantity': qty,
        'price': price,
        'reason': reason
    }])
    if os.path.isfile(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(filename, index=False)


def submit_order(symbol, units, order_type="MARKET"):
    data = {
        "order": {
            "instrument": symbol,
            "units": str(units),
            "type": order_type,
            "positionFill": "DEFAULT"
        }
    }
    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=data)
    client.request(r)


def get_position(symbol):
    r = positions.PositionDetails(accountID=ACCOUNT_ID, instrument=symbol)
    try:
        client.request(r)
        net_pos = float(r.response['position']['net']['units'])
        avg_price = float(r.response['position']['net']['averagePrice'])
        return net_pos, avg_price
    except Exception:
        return 0, 0


def get_account_balance():
    r = accounts.AccountDetails(accountID=ACCOUNT_ID)
    client.request(r)
    return float(r.response['account']['balance'])


def main_trade_loop():
    symbol_state = {sym: {'in_position': False, 'position_type': None, 'entry_price': None} for sym in
                    PAIR_CONFIG.keys()}
    while True:
        if not is_market_open():
            print("Market closed. Sleeping 60s...")
            time.sleep(60)
            continue

        cash = min(get_account_balance(), 100)
        print(f"Account cash: ${cash:.2f}")

        for symbol, cfg in PAIR_CONFIG.items():
            bars = get_price_data(symbol, lookback=cfg.get('lookback', 100), granularity=cfg.get('granularity', "M5"))
            if bars.empty:
                print(f"[{symbol}] No bars received.")
                continue

            state = symbol_state[symbol]
            close_price = bars.iloc[-1]['Close']

            pos_units, pos_price = get_position(symbol)
            has_position = pos_units != 0

            if has_position and not state['in_position']:
                state.update({'in_position': True, 'position_type': 'long' if pos_units > 0 else 'short',
                              'entry_price': pos_price})
            elif not has_position:
                state.update({'in_position': False, 'position_type': None, 'entry_price': None})

            if not state['in_position']:
                entry_signal = strat.generate_entry_signal(bars, -1, symbol)
                qty = cfg['position_size']

                if entry_signal == "BUY":
                    print(f"[{symbol}] BUY {qty} @ {close_price}")
                    submit_order(symbol, qty, "MARKET")
                    state.update({'in_position': True, 'position_type': 'long', 'entry_price': close_price})
                    log_trade("ENTRY", symbol, qty, close_price, "Long Entry Signal")

                elif entry_signal == "SELL":
                    print(f"[{symbol}] SELL {qty} @ {close_price}")
                    submit_order(symbol, -qty, "MARKET")
                    state.update({'in_position': True, 'position_type': 'short', 'entry_price': close_price})
                    log_trade("ENTRY", symbol, -qty, close_price, "Short Entry Signal")
                else:
                    print(f"[{symbol}] HOLD - no entry signal")

            else:
                exit_trade, reason = strat.generate_exit_signal(bars, -1, state['position_type'], symbol)
                entry_price = state['entry_price']
                sl = cfg['sl_pct']
                tp = cfg['tp_pct']

                if not exit_trade:
                    if state['position_type'] == "long" and (
                            close_price <= entry_price * (1 - sl) or close_price >= entry_price * (1 + tp)):
                        exit_trade, reason = True, "Stop Loss or Take Profit"
                    elif state['position_type'] == "short" and (
                            close_price >= entry_price * (1 + sl) or close_price <= entry_price * (1 - tp)):
                        exit_trade, reason = True, "Stop Loss or Take Profit"

                if exit_trade:
                    qty = abs(int(pos_units))
                    if state['position_type'] == "long":
                        print(f"[{symbol}] SELL {qty} @ {close_price} ({reason})")
                        submit_order(symbol, -qty, "MARKET")
                        log_trade("EXIT", symbol, -qty, close_price, f"{reason} (closing LONG)")
                    else:
                        print(f"[{symbol}] BUY to cover {qty} @ {close_price} ({reason})")
                        submit_order(symbol, qty, "MARKET")
                        log_trade("EXIT", symbol, qty, close_price, f"{reason} (closing SHORT)")

                    state.update({'in_position': False, 'position_type': None, 'entry_price': None})
                else:
                    print(f"[{symbol}] HOLDING {state['position_type']}")

        print("Sleeping for 5 minutes...")
        time.sleep(300)


if __name__ == "__main__":
    main_trade_loop()
