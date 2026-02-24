import plotly.graph_objects as go
from utils.query import get_price
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from plotly.subplots import make_subplots


today = datetime.today()
last_year = today - timedelta(days=365)

start_date = last_year.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

def plot_chart(symbol, start_date=start_date, end_date=end_date):
    data = get_price(symbol, start_date, end_date)
    df_data = pd.DataFrame(data)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"Biểu đồ Nến: {symbol}", "RSI (14)")
    )

    # Candlestick plot
    fig.add_trace(go.Candlestick(
        x=df_data["time"],
        open=df_data["open"],
        high=df_data["high"],
        low=df_data["low"],
        close=df_data["close"],
        name="Giá"), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(
        x=df_data["time"],
        y=df_data["rsi14"],
        mode='lines',
        name="RSI 14",
        line=dict(color="orange")), row=2, col=1)

    fig.add_hline(y=70, line=dict(color='red', dash='dash'), row=2, col=1)
    fig.add_hline(y=30, line=dict(color='green', dash='dash'), row=2, col=1)

    # Quá mua (RSI > 70)
    fig.add_shape(type="rect",
                  xref="x", yref="y2",
                  x0=df_data["time"].iloc[0], y0=70,
                  x1=df_data["time"].iloc[-1], y1=100,
                  fillcolor="rgba(255, 0, 0, 0.1)", line_width=0,
                  row=2, col=1)

    # Quá bán (RSI < 30)
    fig.add_shape(type="rect",
                  xref="x", yref="y2",
                  x0=df_data["time"].iloc[0], y0=0,
                  x1=df_data["time"].iloc[-1], y1=30,
                  fillcolor="rgba(0, 255, 0, 0.1)", line_width=0,
                  row=2, col=1)

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False,
        showlegend=False,
        title=f"Biểu đồ Candlestick và RSI - {symbol}"
    )

    st.plotly_chart(fig, width="stretch")