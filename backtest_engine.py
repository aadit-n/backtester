import pandas as pd
import numpy as np

def backtest(data, long_signal, short_signal, exit_signal, initial_capital=10000, position_size=0.95):
    ini_cap = initial_capital
    capital = initial_capital
    position = 0
    shares = 0
    entry_price = 0
    equity = []
    trade_pnls = []
    trades = []

    for i in range(len(data)):
        current_price = data['Close'].iloc[i]
        date = data.index[i]

        if long_signal.iloc[i] and position == 0:
            shares = int((capital * position_size) / current_price)
            capital -= shares * current_price
            entry_price = current_price
            entry_index = date
            position = 1

        elif short_signal.iloc[i] and position == 0:
            shares = int((capital * position_size) / current_price)
            capital += shares * current_price  
            entry_price = current_price
            entry_index = date
            position = -1

        elif exit_signal.iloc[i] and position != 0:
            if position == 1:
                capital += shares * current_price
                pnl = (current_price - entry_price) * shares
                trade_pnls.append(pnl)
            elif position == -1:
                capital -= shares * current_price
                pnl = (entry_price - current_price) * shares
                trade_pnls.append(pnl)

            trades.append({
                "Entry Time": entry_index,
                "Exit Time": date,
                "Type": "Long" if position == 1 else "Short",
                "Entry Price": entry_price,
                "Exit Price": current_price,
                "PnL": pnl
            })

            position = 0
            shares = 0
            entry_price = 0

        if position == 1:
            portfolio_value = capital + (shares * current_price)
        elif position == -1:
            portfolio_value = capital - (shares * current_price)
        else:
            portfolio_value = capital

        equity.append(portfolio_value)

    equity_series = pd.Series(equity, index=data.index)
    returns = equity_series.pct_change().dropna()
    sharpe = returns.mean() / returns.std() * (252) if not returns.empty else 0
    cagr = ((equity[-1] / ini_cap) ** (252 / len(equity))) - 1 if len(equity) > 1 else 0
    max_dd, drawdown_series = calculate_max_drawdown(equity_series)
    sortino_ratio = calculate_sortino_ratio(returns)    
    calmar_ratio = cagr / abs(max_dd) if max_dd != 0 else 0

    wins = sum(pnl > 0 for pnl in trade_pnls)
    total_trades = len(trade_pnls)
    win_percentage = (wins / total_trades * 100) if total_trades > 0 else 0

    trades_df = pd.DataFrame(trades)

    return {
        'equity': equity_series,
        'total_return': equity[-1] - ini_cap,
        'CAGR': cagr,
        'sharpe_ratio': sharpe,
        'num_trades': total_trades,
        'win_percentage': win_percentage,
        'trade_pnls': trade_pnls, 
        'trades': trades_df,
        'drawdown': drawdown_series,
        'max_drawdown': max_dd,
        'sortino': sortino_ratio,
        'calmar': calmar_ratio
    }


def calculate_max_drawdown(equity):
    cumulative_max = equity.cummax()
    drawdown = (equity - cumulative_max) / cumulative_max
    return drawdown.min(), drawdown

def calculate_sortino_ratio(returns, target=0):
    downside_returns = returns[returns < target]
    expected_return = returns.mean() - target
    downside_std = downside_returns.std()
    return expected_return / downside_std if downside_std != 0 else 0