import yfinance as yf
import pandas as pd

def get_stock_data(tickers=None, period="30d"):
    if tickers is None:
        tickers = ["RELIANCE.NS","TCS.NS"]
    
    data = yf.download(tickers, period=period, interval="1d", group_by="ticker")

    # Flatten the DataFrame
    flat_df = (
        data.stack(level=1)
        .reset_index()
        .rename(columns={"level_1": "Ticker"})
    )
    
    return flat_df
