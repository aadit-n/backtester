import pandas as pd
import numpy as np

def backtest(data, long_signal, short_signal, exit_signal, initial_capital=10000, position_size=0.95, stop_loss_pct=0.0, take_profit_pct=0.0):
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

        if position == 0:
            if long_signal.iloc[i]:
                shares = int((capital * position_size) / current_price)
                if shares > 0:  
                    capital -= shares * current_price
                    entry_price = current_price
                    entry_index = date
                    position = 1

            elif short_signal.iloc[i]:
                shares = int((capital * position_size) / current_price)
                if shares > 0: 
                    capital += shares * current_price
                    entry_price = current_price
                    entry_index = date
                    position = -1

        elif position != 0:
            price_change = (current_price - entry_price) / entry_price if position == 1 else (entry_price - current_price) / entry_price
            hit_stop_loss = stop_loss_pct > 0 and price_change <= -stop_loss_pct / 100
            hit_take_profit = take_profit_pct > 0 and price_change >= take_profit_pct / 100

            if exit_signal.iloc[i] or hit_stop_loss or hit_take_profit:
                if position == 1:
                    capital += shares * current_price
                    pnl = (current_price - entry_price) * shares
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
    
    sharpe = returns.mean() / returns.std() * np.sqrt(252) if not returns.empty and returns.std() != 0 else 0
    
    if len(equity) > 1:
        start_date = data.index[0]
        end_date = data.index[-1]
        years = (end_date - start_date).days / 365.25
        cagr = ((equity[-1] / ini_cap) ** (1 / years)) - 1 if years > 0 else 0
    else:
        cagr = 0
    
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
    sortino = (expected_return / downside_std * np.sqrt(252)) if downside_std != 0 else 0
    return sortino
