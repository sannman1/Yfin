import yfinance as yf
import pandas as pd
import datetime

tickers = ["RELIANCE.NS", "TATAMOTORS.NS"]

end = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
start = end - datetime.timedelta(days=30)

for symbol in tickers:
    df = yf.Ticker(symbol).history(start=start, end=end, interval='1d')
    print(f"\n{symbol} data:\n", df)
    
    csv_filename = f"{symbol.replace('.NS', '')}_price_data.csv"
    df.to_csv(csv_filename, index=True)  # keep index (date)
    print(f"Saved to {csv_filename}")

