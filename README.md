# backtester
Drag-and-Drop Backtesting Framework built with Streamlit for easy strategy creation and evaluation. Supports custom technical indicators, user-defined entry/exit rules, and features parameter optimization via grid or random search to find the best trading strategy configurations efficiently.

# Drag-and-Drop Backtesting Framework

A Streamlit-powered platform that enables anyone to backtest trading strategies with zero coding. Define your logic visually, select from 80+ technical indicators, and run strategy optimizations to discover the most profitable configurations using grid or random search.

---

## Features

- **No-code Strategy Builder**: Use dropdowns and condition blocks to define entry/exit logic.
- **80+ Technical Indicators**: Includes overlays and oscillators like SMA, RSI, MACD, Bollinger Bands, etc.
- **Custom Parameter Tuning**: Fine-tune indicator parameters via the sidebar.
- **Backtest Engine**: Run strategy simulations and view metrics like:
  - Total Return
  - CAGR
  - Sharpe, Sortino, and Calmar Ratios
  - Win % and Max Drawdown
- **Optimization Module**: Run Grid or Random Search to find the best indicator parameters.
- **Trade Logs & PnL Histograms**: Detailed logs of all trades and distribution of profits.

---

## Installation

```bash
git clone https://github.com/aadit-n/backtester.git
cd backtester
pip install -r requirements.txt

```

## Usage
```bash
streamlit run app.py
```
1. Select a stock ticker and time frame in the sidebar.
2. Add indicators and customize their parameters.
3. Visually build your Long/Short/Exit logic using dropdowns.
4. Press "Fetch Data & Run Backtest" to view performance.
5. Click "🔍 Optimize Indicators" to run param search.

## ⭐️ Star This Repo
If you found this project useful, give it a ⭐️! It motivates future enhancements and helps others discover it too.
