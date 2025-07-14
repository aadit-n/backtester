import plotly.graph_objects as go
import plotly.express as px


def plot_equity_curve(equity_curve):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=equity_curve.index, y=equity_curve, mode='lines', name='Equity'))
    fig.update_layout(
        title='Equity Curve',
        xaxis_title='Date',
        yaxis_title='Portfolio Value',
        template='plotly_white'
    )
    return fig


def plot_all_indicators(df, trades=None):
    fig = go.Figure()

    if 'Close' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close', line=dict(color='blue')))

    for col in df.columns:
        if col not in ['Open', 'High', 'Low', 'Close', 'Volume']:
            fig.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col))

    if trades is not None and not trades.empty:
        for _, row in trades.iterrows():
            color = 'green' if row['Type'] == 'Long' else 'red'
            fig.add_vline(x=row['Entry Time'], line=dict(color=color, width=1, dash='dot'))
            fig.add_vline(x=row['Exit Time'], line=dict(color='gray', width=1, dash='dot'))

    fig.update_layout(
        title='Close Price & Indicators with Trade Markers',
        xaxis_title='Date',
        yaxis_title='Value',
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )

    return fig


def plot_pnl_histogram(trades_df):
    if trades_df.empty:
        return None

    fig = px.histogram(trades_df, x='PnL', nbins=20, title='PnL Histogram')
    fig.update_layout(
        xaxis_title='Profit / Loss per Trade',
        yaxis_title='Frequency',
        template='plotly_white'
    )
    return fig
