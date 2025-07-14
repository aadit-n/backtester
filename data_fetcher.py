import yfinance as yf
import pandas as pd
import numpy as np


def fetch_data(ticker, period='60d', interval='1d'):
    try:
        data = yf.download(ticker, period=period, interval=interval, multi_level_index=False)
        return data
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")