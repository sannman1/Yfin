import yfinance as yf
import pandas as pd

def get_stock_data(tickers=None, period="5y"):
    if tickers is None:
        tickers = ["RELIANCE.NS", "TCS.NS"]

    data = yf.download(tickers, period=period, interval="1d", group_by='ticker', auto_adjust=False)

    # If single ticker, convert to multi-index manually
    if not isinstance(data.columns, pd.MultiIndex):
        # data.columns: Index(['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'], dtype='object')
        data.columns = pd.MultiIndex.from_product([data.columns, tickers])

    frames = []
    for ticker in tickers:
        df = data[ticker].copy()
        df["Date"] = df.index
        df["Ticker"] = ticker
        frames.append(df.reset_index(drop=True))

    final_df = pd.concat(frames)
    final_df = final_df[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
    return final_df
