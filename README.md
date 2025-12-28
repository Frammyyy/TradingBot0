# Modular Multi-Broker Trading Bot

A fully modular, Python-based trading bot designed for both live trading and backtesting across multiple brokers such as **OANDA**, **Interactive Brokers (IBKR)**, and **Alpaca**.
Built with a focus on **scalability**, **custom strategy integration**, and **dynamic risk management**.

---

##  Features

### Core System

* Modular architecture — Each broker and strategy runs independently.
* Supports live and backtest environments.
* Configurable broker settings stored under `/broker_configs/`.
* Dynamic stop-loss and take-profit system with real-time trailing logic.

### 📈 Strategy Engine

* Pluggable strategies under `/strats/`:

  * EMA Crossover Strategy
  * RSI Strategy
  * MACD Strategy
  * Combined Hybrid Strategy
* Supports future additions like ADX, Bollinger Bands, and Volume Weighted MA.

###  Risk Management

* Dynamic trailing SL/TP based on volatility or momentum.
* Trade logging and backtest analytics.
* Symbol-specific configurations (EUR/USD, GBP/USD, USD/CAD, etc.).

###  Code Structure

```
trading-bot/
├── live.py                # Live trading engine
├── backtest.py            # Backtesting engine
├── broker_configs/        # Modular broker integrations
│   ├── oanda_config.py
│   ├── ibpkr_config.py
│   ├── alpaca_config.py
├── strats/                # Strategy folder
│   ├── ema_strat.py
│   ├── macd_strat.py
│   ├── rsi_strat.py
│   ├── strat.py
│   ├── dynamic_tp_sl.py
├── configs.py             # Global configuration file
├── trade_log.csv          # Trade history and analytics
└── README.md              # Project documentation
```

---

## Future Plans

* Add advanced signal systems (ADX, BBANDS, VWAP, Ichimoku)
* Integrate real-time Discord alerts
* Implement a local web dashboard for trade visualization
* Add matplotlib analytics and performance graphs

---

##  Tech Stack

* **Python 3.10+**
* **ib_insync** (Interactive Brokers API)
* **OANDA v20 REST API**
* **Pandas / NumPy**
* **Matplotlib (planned)**
* **Discord Webhooks**

---

## Example Strategy Logic

```python
if ema_fast > ema_slow and rsi < 70:
    place_buy_order()
elif ema_fast < ema_slow and rsi > 30:
    place_sell_order()
```

---

## License

This project is for **personal and educational use**.
Future monetization includes a **subscription-based trading bot** and **Discord signal bot**.

---

## 📬 Contact

**Developer:** Nasif Hyder
**Portfolio:** [coming soon]
**Discord:** (private development server for subscribers)[coming soon]
