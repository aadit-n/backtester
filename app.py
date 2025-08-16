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
st.title("Backtesting Framework")
st.markdown("""
DISCLAIMER: NONE OF THE DATA OR RESULTS PROVIDED BY THIS WEBSITE/APP IS FINANCIAL ADVICE. ALL FINANCIAL DECISIONS MADE BY THE USER ARE INDEPENDENT OF THE RESULTS SHOWN HERE.
""")
st.markdown(""" 
This tool allows you to visually build, test, and optimize trading strategies using technical indicators.
""")
with st.expander("How does this backtesting engine work?"):
    st.markdown("""
    1. **You define strategy logic** using technical indicators and conditional rules.
    2. **The system fetches price data** using Yahoo Finance.
    3. **Indicators are computed** with Tulipy.
    4. **Trade signals** are generated using your logic (e.g., if RSI < 30 → Buy).
    5. **The backtest simulates trades** over historical data and calculates performance metrics.
    6. **You can optimize your strategy** using Bayesian optimization to find the best parameters.
    """)

with st.expander("What do all the indicators mean and whats the math behind them?"):
    indicator_docs = {
    # Overlays & Moving Averages
    "AVGPRICE": "Average Price: (Open + High + Low + Close) / 4.",
    "SMA": "Simple Moving Average: arithmetic mean of closing prices over N periods.\n\nFormula:\n$$SMA_t = \\frac{1}{N} \\sum_{i=0}^{N-1} P_{t-i}$$",
    "EMA": "Exponential Moving Average: gives more weight to recent prices.\n\nFormula:\n$$EMA_t = \\alpha P_t + (1 - \\alpha) EMA_{t-1}, \\quad \\alpha = \\frac{2}{N+1}$$",
    "DEMA": "Double EMA: reduces lag by combining two EMAs.\n\nFormula:\n$$DEMA = 2·EMA - EMA(EMA)$$",
    "TEMA": "Triple EMA: further reduces lag.\n\nFormula:\n$$TEMA = 3·EMA - 3·EMA(EMA) + EMA(EMA(EMA))$$",
    "TRIMA": "Triangular MA: double-smoothed moving average with triangular weighting.",
    "ZLEMA": "Zero-Lag EMA: adjusts EMA for lag using price difference.",
    "VWMA": "Volume Weighted MA: prices weighted by volume.\n\nFormula:\n$$VWMA_t = \\frac{\\sum P_i·V_i}{\\sum V_i}$$",
    "VWM A": "Volume Weighted Moving Average (duplicate).",
    "KAMA": "Kaufman Adaptive MA: adapts smoothing based on market volatility / noise.",
    "HMA": "Hull MA: weighted MA designed to reduce lag and improve smoothness.",
    "LINREG": "Linear Regression MA: fits a line over recent prices, uses its value at current bar.",
    "MEDPRICE": "Median Price: (High + Low) / 2.",
    "TYPPRICE": "Typical Price: (High + Low + Close) / 3.",
    "WCPRICE": "Weighted Close Price: (High + Low + Close + Close) / 4.",
    "WCLPRICE": "Weighted Close Price (duplicate).",
    "TSF": "The Time Series Forecast is a smoothing functions that works by preforming linear least squares regression over a moving window. It then uses the linear model to predict the value for the next bar.",
    "VIDYA": "The Variable Index Dynamic Average indicator modifies the Exponential Moving Average by varying the smoothness based on recent volatility.",
    "WILDERS": "Wilder's smoothing is a type of exponential moving average. It takes one parameter, the period n, a positive integer. Larger values for n will have a greater smoothing effect on the input data but will also create more lag.",
    "DPO": "The Detrended Price Oscillator helps identify cycles.",
    "DX": "The Directional Movement Index can help determine trend strength.",
    "MARKETFI": "The Market Facilitation Index compares volume and price change.",
    "MSW": "The Mesa Sine Wave helps identify cycles.",
    "NATR": "Normalized Average True Range is a measure of volatility. Because Normalized Average True Range is normalized, it can be more useful than Average True Range when comparing across different price levels.",
    "TRIX": "The Trix is a momentum indicator. It takes one parameter, the period n. It is calculated as a rate of change of a Exponential Moving Average applied three times.",
    # Volatility & Bands
    "BBANDS": "Bollinger Bands consist of a middle SMA and upper/lower bands = SMA ± (stddev × n).",
    "PSAR": "Parabolic SAR: places dots above/below price using acceleration factor to signal trend and reversals.",
    "ATR": "Average True Range: measures volatility using the averaged True Range:\nTR = max(H-L, H-PC, L-PC)",
    # Trend Strength & Momentum
    "ADX": "Average Directional Index: measures trend strength (not direction).",
    "ADXR": "Smoothed ADX: averages current and previous ADX values to smooth trend strength signal.",
    "CCI": "Commodity Channel Index: deviation of price from its moving average:\n$$CCI = \\frac{TP - \\text{MA}(TP)}{0.015 × \text{MeanDev}}$$",
    "AROON": "Measures time since highest high and lowest low to detect trend direction and strength.",
    "AROONOSC": "Oscillator: Aroon Up − Aroon Down, ranges from −100 to +100.",
    "DI": "Directional Indicator: part of ADX system showing +DI / −DI trends.",
    "DM": "Directional Movement: raw components (+DM, –DM) of trend direction.",
    "TRANGE": "True Range: the maximum of (H−L, H−PC, L−PC).",
    # Oscillators & Momentum
    "RSI": "Relative Strength Index: momentum oscillator between 0–100.\n\nFormula:\n$$RSI = 100 - \\frac{100}{1 + RS}, \\quad RS = \\frac{AvgGain}{AvgLoss}$$",
    "STOCH": "Stochastic Oscillator: compares close to recent high-low range. %K and %D lines.",
    "STOCHRSI": "Stochastic RSI: stochastic applied to RSI values.",
    "MOM": "Momentum: difference between current price and price N periods ago.",
    "ROC": "Rate of Change: (P_t − P_{t−N}) / P_{t−N} × 100.",
    "ROCP": "Price Rate of Change in percentage.",
    "ROCR": "Rate of Change Ratio: P_t / P_{t−N}.",
    "ROCR100": "Rate of Change Ratio × 100.",
    "CMO": "Chande Momentum Oscillator: measures momentum considering sum of gains vs losses over period.",
    "FOSC": "Falling Oscillator: variation on oscillator measuring falling momentum.",
    "AO": "Awesome Oscillator: difference between SMA(5) and SMA(34) of mid-price.",
    "KVO": "Klinger Volume Oscillator: volume-based oscillator using long/short EMAs of the K volume.",
    "MACD": "Moving Average Convergence Divergence: EMA(short) − EMA(long), Signal = EMA(signal_period) of MACD.",
    "PPO": "Percentage Price Oscillator: MACD expressed in percentage terms.",
    "APO": "Absolute Price Oscillator: similar to MACD but absolute difference (no signal line).",
    "ULTOSC": "Ultimate Oscillator: weighted average of 3 time‑frame Fibonacci‑scaled oscillators.",
    "FISHER": "Fisher Transform: converts prices into a Gaussian-like distribution:\n$$Y = 0.5 \\ln\\frac{1 + X}{1 - X}$$ where X is normalized price.",
    "CVI": "Chaikin Volatility Index: measures volatility change via difference between high-low spreads.",
    "EMV": "Ease of Movement: volume-weighted indicator of price movement and volume.",
    "MFI": "Money Flow Index: uses price and volume to measure trading pressure (0–100 range).",
    "VOSC": "Volume Oscillator: difference between two EMAs of volume.",
    # Volume & Accumulation
    "AD": "Accumulation/Distribution Line: cumulative money flow based on volume and price direction.",
    "ADOSC": "Accumulation/Distribution Oscillator: short-term minus long-term EMA of AD line.",
    "OBV": "On-Balance Volume: adds/subtracts today's volume based on whether price went up/down.",
    "NVI": "Negative Volume Index: tracks price moves on days when volume decreases.",
    "PVI": "Positive Volume Index: tracks price moves on days when volume increases.",
    "WAD": "Williams Accumulation/Distribution: money flow oscillator similar to AD.",
    "BOP": "Balance of Power: measures strength of buyers vs sellers.",
    # Price Channels & Envelopes
    "CMO": "Chande Momentum Oscillator (duplicate)",
    "VAR": "Variance: statistical measure of price dispersion over a period.",
    "VHF": "Vertical Horizontal Filter: ratio measuring trend vs volatility.",
    "WILLR": "Williams %R: gives overbought/oversold status based on close relative to recent high-low."}
    for name, desc in indicator_docs.items():
        st.markdown(f"**{name}**: {desc}")

st.sidebar.header("Market & Data Settings")
st.sidebar.caption("Select the stock ticker, timeframe, and historical period to fetch data for backtesting.")
ticker = st.sidebar.text_input("Ticker", value="AAPL")
interval = st.sidebar.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d"], index=4)
period = st.sidebar.selectbox("Period", ["7d", "30d", "60d", "90d", "1y", "2y", "5y", "10y"], index=6)

st.sidebar.markdown("---")

st.sidebar.header("Indicators")
st.sidebar.caption("Choose indicators from the dropdown, customize parameters, and add them to your strategy.")

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
st.sidebar.caption("These are the indicators currently included in your strategy. You can remove any of them.")
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

st.markdown("Once your market settings and indicators are ready, click the button below to fetch data and run your strategy.")
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
    st.caption("Here's the historical market data along with your selected indicators.")
    st.dataframe(df.iloc[::-1])

    st.subheader("Strategy Logic")
    st.markdown("Define the logic for when to enter or exit trades using your chosen indicators. If you want to compare two columns, you can copy the name of the column from the 'Available Columns' section")

    st.markdown("### Available Columns")
    st.code(", ".join(df.columns))

    st.markdown("#### Long Entry Conditions")
    st.caption("Long Entry: When should we buy?")
    long_entry_expr = build_strategy_conditions(df, "long")

    st.markdown("#### Short Entry Conditions")
    st.caption("Short Entry: When should we short?")
    short_entry_expr = build_strategy_conditions(df, "short")

    st.markdown("#### Exit Conditions")
    st.caption("Exit: When should we close any open position?")
    exit_expr = build_strategy_conditions(df, "exit")

    st.markdown("### Risk Management")
    st.caption("Set your stop loss and take profit levels (as '%' from entry price) to control risk.")
    stop_loss_pct = st.number_input("Stop Loss (%)", value=0.0, min_value=0.0, format="%.2f")
    take_profit_pct = st.number_input("Take Profit (%)", value=0.0, min_value=0.0, format="%.2f")
    st.caption("""
    **Stop Loss**: Automatically exits a trade if it drops more than X percent from the entry.  
    **Take Profit**: Automatically exits a trade once it gains more than Y percent from the entry.
    """)

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
        st.caption("Your strategy signals were generated successfully. Here's how the strategy performed:")


        st.subheader("Indicator Charts")
        st.caption("Visualize all selected indicators on top of the price chart.")


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
        st.caption("This shows how your portfolio would have grown over time.")
        st.plotly_chart(plot_equity_curve(result['equity']), key="equity_curve")

        st.subheader("Backtest Results")
        st.dataframe(result["equity"])

        st.subheader("Metrics")
        st.caption("Key performance metrics of your strategy:")
        st.metric("Total Return", f"${result['total_return']:.2f}")
        st.metric("CAGR", f"{result['CAGR']*100:.2f}%")
        st.metric("Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
        st.metric("Max Drawdown", f"{result['max_drawdown']:.2f}%")
        st.metric("Calmar Ratio", f"{result['calmar']:.2f}")
        st.metric("Sortino Ratio", f"{result['sortino']:.2f}")
        st.metric("Win %", f"{result['win_percentage']:.2f}%")
        st.metric("Number of Trades", result['num_trades'])

        with st.expander("How are these metrics calculated?"):
            st.markdown("""
            **Total Return** = Final portfolio value − Initial capital  
            **CAGR (Compounded Annual Growth Rate)** =  
            $$
            \\left(\\frac{\\text{Final Value}}{\\text{Initial Capital}}\\right)^{\\frac{252}{\\text{# of periods}}} - 1
            $$

            **Sharpe Ratio** =  
            $$
            \\frac{\\text{Average Daily Return}}{\\text{Standard Deviation of Daily Returns}} \\times \\sqrt{252}
            $$

            **Sortino Ratio** =  
            $$
            \\frac{\\text{Average Daily Return}}{\\text{Standard Deviation of Negative Returns}} \\times \\sqrt{252}
            $$

            **Max Drawdown** =  
            $$
            \\text{Minimum of } \\left(\\frac{\\text{Equity} - \\text{Running Max}}{\\text{Running Max}}\\right)
            $$

            **Calmar Ratio** =  
            $$
            \\frac{\\text{CAGR}}{\\left|\\text{Max Drawdown}\\right|}
            $$

            **Win %** =  
            $$
            \\frac{\\text{Number of Winning Trades}}{\\text{Total Trades}} \\times 100
            $$
            """)


        if not result['trades'].empty:
            st.subheader("Trade Log")
            st.caption("Details of each trade executed by the strategy.")
            st.dataframe(result['trades'].style.format({
                "Entry Price": "{:.2f}",
                "Exit Price": "{:.2f}",
                "PnL": "{:.2f}"
            }))

        st.subheader("PnL Histogram")
        st.caption("Distribution of profits and losses from all trades.")
        st.plotly_chart(plot_pnl_histogram(result['trades']), key="pnl_histogram")
        

        st.sidebar.markdown('---')

        n_trials = st.sidebar.number_input("Number of Trials", min_value=1, max_value=1000, value=50)
        optimise = st.sidebar.button("Optimise Indicators")
        st.sidebar.caption("Tune indicator parameters using Bayesian Optimization to maximize strategy returns.")
        if optimise:
            st.info("Running parameter optimization...")
            with st.expander("How does Bayesian Optimization work?"):
                st.markdown("""
                **Bayesian Optimization** is a method to efficiently search for the best indicator parameters by modeling the performance landscape as a probabilistic function.

                It builds a **surrogate model** (usually a Gaussian Process or Tree-structured Parzen Estimator) of the objective function and chooses the next set of parameters by balancing **exploration** and **exploitation** using an **acquisition function** like Expected Improvement (EI).

                In your case, the objective function is:
                $$
                f(\text{params}) = \text{Total Return from Backtest}
                $$

                And the optimizer tries different combinations of indicator parameters (like `period`, `stddev`, etc.) to find the maximum return.

                You can control how many combinations are tested with the **Number of Trials** slider in the sidebar.
                """)
            result, best_config = bayesian_optimiser(df, st.session_state.selected_indicators, long_entry_expr, short_entry_expr, exit_expr, n_trials)

        if result:
            st.success("Best parameters and results after optimization:")
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


