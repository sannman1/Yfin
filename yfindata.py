import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetches stock data from Yahoo Finance for a given ticker and date range.
    """
    print(f"Fetching data for {ticker} from {start_date} to {end_date}...")
    
    # --- THIS LINE IS NOW FIXED ---
    data = yf.download(
        ticker, 
        start=start_date, 
        end=end_date, # Correct variable name is end_date
        progress=False, 
        auto_adjust=True
    )
    
    if data.empty:
        print(f"No data returned from Yahoo Finance for {ticker}.")
        return pd.DataFrame()

    data.reset_index(inplace=True)

    # We use .squeeze() on each column to ensure it is 1-dimensional.
    df_cleaned = pd.DataFrame({
        'ticker': ticker,
        'date': pd.to_datetime(data['Date'].squeeze()),
        'open': data['Open'].squeeze(),
        'high': data['High'].squeeze(),
        'low': data['Low'].squeeze(),
        'close': data['Close'].squeeze(),
        'adj_close': data['Close'].squeeze(),  # Close is already adjusted
        'volume': data['Volume'].squeeze().astype(int)
    })
    
    print(f"Successfully fetched {len(df_cleaned)} records for {ticker}.")
    return df_cleaned