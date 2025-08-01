PAIR_CONFIG = {
    'EUR_USD': {
        'rsi_period': 10,
        'rsi_up': 65,
        'rsi_down': 40,
        'ema_short': 12,
        'ema_long': 26,
        'sl_pct': 0.02,
        'tp_pct': 0.015,
        'position_size': 1000,
        'lookback': 100,  # number of bars needed to calculate indicators reliably
        'granularity': 'M5',  # 5-minute candles
        'trail_tp_enabled': True,
        'trail_tp_start': 0.015,  # Start trailing at 1% profit
        'trail_tp_step': 0.01,  # Each step = +0.5% profit
        'trail_tp_decay': 0.7,  # Step size shrinks to 0.25%, 0.125%, etc.

    },
    'GBP_USD': {
        'rsi_period': 14,
        'rsi_up': 65,
        'rsi_down': 35,
        'ema_short': 10,
        'ema_long': 30,
        'sl_pct': 0.01,
        'tp_pct': 0.02,
        'position_size': 800,
        'lookback': 120,
        'granularity': 'M5',
        'trail_tp_enabled': True,
        'trail_tp_start': 0.01,
        'trail_tp_step': 0.01,
        'trail_tp_decay': 0.5,

    },
    'USD_CAD': {
        'rsi_period': 20,
        'rsi_up': 65,
        'rsi_down': 35,
        'ema_short': 12,
        'ema_long': 26,
        'sl_pct': 0.01,
        'tp_pct': 0.01,
        'position_size': 800,
        'lookback': 150,
        'granularity': 'M5',
        'trail_tp_enabled': True,
        'trail_tp_start': 0.01,
        'trail_tp_step': 0.01,
        'trail_tp_decay': 0.5,

    }
}

API = {
    'TOKEN': 'b654eae60b05858a0198cbff433c855a-a70533bc6613d836b83cbab3a8ea88af',
    'ACCOUNT_ID': '101-001-28401144-001'
}

TIME = {
    'START': "8:00",
    'END': "18:00"
}
