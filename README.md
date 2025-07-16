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
- **Optimization Module**: Run Bayesian Optimization using Optuna to find the best indicator parameters.
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


   <img width="358" height="436" alt="image" src="https://github.com/user-attachments/assets/183c2e8f-c33f-4721-85d7-daffefdece39" />


3. Add indicators and customize their parameters.


   <img width="351" height="488" alt="image" src="https://github.com/user-attachments/assets/96040db9-b2b7-4e4a-a248-1da6fdfba2d0" />


4. Visually build your Long/Short/Exit logic using dropdowns.


    <img width="1326" height="883" alt="image" src="https://github.com/user-attachments/assets/e131f11a-9306-41f9-9b79-cdc5d76873ab" />


6. Press "Fetch Data & Run Backtest" to view performance.


   <img width="1361" height="786" alt="image" src="https://github.com/user-attachments/assets/6d0d7b19-661b-49cd-8be8-9c5914a96305" />


   <img width="1408" height="627" alt="image" src="https://github.com/user-attachments/assets/ca9a2c47-1c6b-408b-a78c-ae99ad5cf78b" />


   <img width="1375" height="706" alt="image" src="https://github.com/user-attachments/assets/744ec006-e461-49ad-83eb-eb16f3db6b90" />


   <img width="1391" height="642" alt="image" src="https://github.com/user-attachments/assets/ee311e32-0245-4204-aa34-a0624bf0a73a" />


   <img width="1259" height="887" alt="image" src="https://github.com/user-attachments/assets/6a3c90c0-d367-4ca7-8b13-c9f4fb6f7a30" />


   <img width="1366" height="595" alt="image" src="https://github.com/user-attachments/assets/893add08-90e4-44ae-8dc7-710335bc05d3" />


   <img width="1414" height="659" alt="image" src="https://github.com/user-attachments/assets/308ac0dd-388a-40fd-a359-dec12e248c62" />


8. Click "🔍 Optimize Indicators" to run optimization.


   <img width="342" height="219" alt="image" src="https://github.com/user-attachments/assets/25ddac70-aadd-4e86-8a71-df25e63c7807" />


   <img width="1398" height="814" alt="image" src="https://github.com/user-attachments/assets/2c46c35b-9908-4faf-a8b6-024504383cbd" />


