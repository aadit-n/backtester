import streamlit as st
import pandas as pd
from data_fetcher import fetch_data
from indicator_engine import get_indicators
from backtest_engine import backtest
from visualisation import plot_equity_curve, plot_all_indicators, plot_pnl_histogram
from indicator_config import indicators_list as indicators_config
from optimiser import bayesian_optimiser
import uuid



def build_strategy_conditions(df, key_prefix):
    st.markdown("Add Conditions:")

    if f"{key_prefix}_conditions" not in st.session_state:
        st.session_state[f"{key_prefix}_conditions"] = []

    if f"{key_prefix}_add_flag" not in st.session_state:
        st.session_state[f"{key_prefix}_add_flag"] = False

    if st.button(f"➕ Add Condition", key=f"add_btn_{key_prefix}"):
        st.session_state[f"{key_prefix}_conditions"].append({"left": df.columns[0], "op": ">", "right": "0"})

    conditions = st.session_state[f"{key_prefix}_conditions"]
    new_conditions = []

    for i, cond in enumerate(conditions):
        col1, col2, col3, col4 = st.columns([4, 2, 4, 1])
        with col1:
            left = st.selectbox("Left", df.columns, index=df.columns.get_loc(cond["left"]) if cond["left"] in df.columns else 0, key=f"{key_prefix}_left_{i}")
        with col2:
            op = st.selectbox(
                "Operator",
                [">", "<", ">=", "<=", "==", "!="],
                index=[">", "<", ">=", "<=", "==", "!="].index(cond["op"]) if cond["op"] in [">", "<", ">=", "<=", "==", "!="] else 0,
                key=f"{key_prefix}_op_{i}"
            )
        with col3:
            right = st.text_input("Right (value or column)", value=cond["right"], key=f"{key_prefix}_right_{i}")
        with col4:
            if st.button("❌", key=f"remove_{key_prefix}_{i}"):
                continue  
        new_conditions.append({"left": left, "op": op, "right": right})

    st.session_state[f"{key_prefix}_conditions"] = new_conditions

    expressions = []
    for cond in new_conditions:
        right_expr = f"df['{cond['right']}']" if cond['right'] in df.columns else cond['right']
        expressions.append(f"(df['{cond['left']}'] {cond['op']} {right_expr})")

    if expressions:
        return " & ".join(expressions)
    else:
        return "pd.Series([False] * len(df), index=df.index)"


st.set_page_config(layout="wide")
st.title("Drag-and-Drop Backtesting Framework")

st.sidebar.header("Market & Data Settings")
ticker = st.sidebar.text_input("Ticker", value="AAPL")
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d"], index=4)
period = st.sidebar.selectbox("Period", ["7d", "30d", "90d", "1y", "2y", "5y", "10y"], index=5)

st.sidebar.markdown("---")

st.sidebar.header("Indicators")

if "selected_indicators" not in st.session_state:
    st.session_state.selected_indicators = []

indicator_names = [ind["name"] for ind in indicators_config]
selected_name = st.sidebar.selectbox("Choose Indicator", indicator_names)

base_config = next(ind for ind in indicators_config if ind["name"] == selected_name)

user_params = {
    param: float(st.sidebar.number_input(f"{selected_name.upper()} - {param}", value=float(default)))
    for param, default in base_config["params"].items()
}

if st.sidebar.button("Add Indicator"):
    st.session_state.selected_indicators.append({
        "name": base_config["name"],
        "inputs": base_config["inputs"],
        "params": user_params,
        "param_grid": base_config.get("param_grid", {})
    })

st.sidebar.markdown("### Selected Indicators")
remaining = []
for i, config in enumerate(st.session_state.selected_indicators):
    col1, col2 = st.sidebar.columns([5, 1])
    with col1:
        st.write(f"{i+1}. {config['name'].upper()} - {config['params']}")
    with col2:
        if st.button("❌", key=f"remove_{i}"):
            continue
    remaining.append(config)
st.session_state.selected_indicators = remaining

if st.button("Fetch Data & Run Backtest"):
    df = fetch_data(ticker, period, interval)

    for config in st.session_state.selected_indicators:
        outputs = get_indicators(df, config)
        for col, series in outputs.items():
            df[col] = series

    st.session_state.df = df

if "df" in st.session_state:
    df = st.session_state.df

    st.subheader(f"Fetched Data for **{ticker}** | Interval: `{interval}`, Period: `{period}`")
    st.dataframe(df)

    st.subheader("Strategy Logic")

    st.markdown("### Available Columns")
    st.code(", ".join(df.columns))

    st.markdown("#### Long Entry Conditions")
    long_entry_expr = build_strategy_conditions(df, "long")

    st.markdown("#### Short Entry Conditions")
    short_entry_expr = build_strategy_conditions(df, "short")

    st.markdown("#### Exit Conditions")
    exit_expr = build_strategy_conditions(df, "exit")

    st.markdown("### Risk Management")
    stop_loss_pct = st.number_input("Stop Loss (%)", value=0.0, min_value=0.0, format="%.2f")
    take_profit_pct = st.number_input("Take Profit (%)", value=0.0, min_value=0.0, format="%.2f")

    try:
        safe_globals = {
            "df": df,
            "pd": pd,
            "len": len,
            "__builtins__": {}
        }

        long_signal = eval(long_entry_expr, safe_globals)
        short_signal = eval(short_entry_expr, safe_globals)
        exit_signal = eval(exit_expr, safe_globals)

        st.success("Strategy logic compiled and executed.")

        st.subheader("Indicator Charts")

        indicator_cols = [col for col in df.columns if col not in ['Open', 'High', 'Low', 'Volume']]
        if indicator_cols:
            st.plotly_chart(plot_all_indicators(df[indicator_cols]), key="all_indicators")
        else:
            st.info("No indicators to display.")


        result = backtest(
            df,
            long_signal,
            short_signal,
            exit_signal,
            stop_loss_pct=stop_loss_pct,
            take_profit_pct=take_profit_pct
        )
    


        st.subheader("Equity Curve")
        st.plotly_chart(plot_equity_curve(result['equity']), key="equity_curve")

        st.subheader("Backtest Results")
        st.dataframe(result["equity"])

        st.subheader("Metrics")
        st.metric("Total Return", f"${result['total_return']:.2f}")
        st.metric("CAGR", f"{result['CAGR']*100:.2f}%")
        st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
        st.metric("Max Drawdown", f"{result['max_drawdown']:.2f}%")
        st.metric("Calmar Ratio", f"{result['calmar']:.2f}")
        st.metric("Sortino Ratio", f"{result['sortino']:.2f}")
        st.metric("Win %", f"{result['win_percentage']:.2f}%")
        st.metric("Number of Trades", result['num_trades'])

        if not result['trades'].empty:
            st.subheader("Trade Log")
            st.dataframe(result['trades'].style.format({
                "Entry Price": "{:.2f}",
                "Exit Price": "{:.2f}",
                "PnL": "{:.2f}"
            }))

        st.subheader("PnL Histogram")
        st.plotly_chart(plot_pnl_histogram(result['trades']), key="pnl_histogram")
        

        st.sidebar.markdown('---')

        n_trials = st.sidebar.number_input("Number of Trials", min_value=1, max_value=1000, value=50)
        optimise = st.sidebar.button("Optimise Indicators")
        if optimise:
            st.info("Running parameter grid optimization...")
            result, best_config = bayesian_optimiser(df, st.session_state.selected_indicators, long_entry_expr, short_entry_expr, exit_expr, n_trials)

        if result:
            st.success("Best results from parameter optimization:")
            for cfg in best_config:
                st.write(f"• {cfg['name'].upper()} → {cfg['params']}")

                st.plotly_chart(plot_equity_curve(result['equity']), key=f"equity_curve_opt_{uuid.uuid4()}")
                st.metric("Total Return", f"${result['total_return']:.2f}")
                st.metric("CAGR", f"{result['CAGR']*100:.2f}%")
                st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
            else:
                st.error("No valid parameter combinations found.")
    except Exception as e:
        st.error(f"Error in strategy logic: {e}")

else:
    st.info("Please fetch data and run backtest first.")
