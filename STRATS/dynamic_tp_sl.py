def initialize_trailing_state(config):
    # Set initial trailing TP state from config or defaults
    return {
        'locked_profit_pct': 0.0,
        'next_tp_pct': config.get('trail_tp_start', 0.01),  # e.g. 1%
        'tp_step': config.get('trail_tp_step', 0.005)       # e.g. 0.5%
    }

def update_trailing_tp(state, close_price, entry_price, position_type, decay=0.5):
    # Calculate profit % (invert for shorts)
    profit_pct = (close_price - entry_price) / entry_price
    if position_type == "short":
        profit_pct = -profit_pct

    # Lock profit and move next TP target if profit crosses threshold
    if profit_pct >= state['next_tp_pct']:
        state['locked_profit_pct'] = state['next_tp_pct']
        state['next_tp_pct'] += state['tp_step']
        state['tp_step'] *= decay
        print(f"[TrailingTP] Locked {state['locked_profit_pct']*100:.2f}%, next target {state['next_tp_pct']*100:.2f}%, step {state['tp_step']*100:.2f}%")

    # Calculate trailing stop price depending on position
    sl_price = entry_price * (1 + state['locked_profit_pct'] * (1 if position_type == "long" else -1))
    triggered = (close_price < sl_price) if position_type == "long" else (close_price > sl_price)

    if triggered:
        print(f"[TrailingTP] Triggered at {close_price}, stop loss at {sl_price}")
        return True, f"Trailing TP hit ({state['locked_profit_pct']*100:.2f}%)"

    return False, ""
