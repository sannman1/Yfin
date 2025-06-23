from getdate import find_missing_dates
from yfindata import fetch_stock_data
from postgre import save_data, create_table_if_not_exists
import pandas as pd

def run_pipeline():
    """
    Main function to execute the data pipeline.
    This corresponds to the 'main.py' boxes in your diagram.
    """
    # --- Configuration ---
    # The condition 'if tickers exists' is handled here.
    # The script will only run if this list is not empty.
    TICKERS = ['TCS.NS','RELIANCE.NS','HDFCBANK.NS','INFY.NS','WIPRO.NS','TECHM.NS','LTIM.NS']
    START_DATE = '2023-01-01'
    END_DATE = pd.to_datetime('today').strftime('%Y-%m-%d') # Use today's date as end
    
    print("--- Starting Data Pipeline ---")
    
    # Ensure the database table exists before we begin
    create_table_if_not_exists()
    
    if not TICKERS:
        print("Ticker list is empty. Exiting.")
        return

    # Process each ticker individually
    for ticker in TICKERS:
        print(f"\n{'='*20} Processing: {ticker} {'='*20}")
        
        # 1. Call getdate.py logic to find what's missing
        missing_dates = find_missing_dates(ticker, START_DATE, END_DATE)
        
        # 2. If there are missing dates, proceed to fetch and save
        if missing_dates:
            # For efficiency, fetch the entire range of missing dates at once
            fetch_start = missing_dates[0]
            fetch_end = missing_dates[-1]
            
            # Add one day to fetch_end because yfinance is exclusive of the end date
            fetch_end_inclusive = (pd.to_datetime(fetch_end) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            
            # 3. Call yfindata.py to get data from the external API
            new_data_df = fetch_stock_data(ticker, fetch_start, fetch_end_inclusive)
            
            if not new_data_df.empty:
                # Filter the fetched data to only include the specific dates we were missing
                # This removes weekends and holidays that yf.download might return data for within a range.
                new_data_df['date_str'] = new_data_df['date'].dt.strftime('%Y-%m-%d')
                final_data_to_save = new_data_df[new_data_df['date_str'].isin(missing_dates)].copy()
                final_data_to_save.drop(columns=['date_str'], inplace=True)

                # 4. Call postgre.py to save the new, filtered data
                save_data(final_data_to_save)
        else:
            print(f"[{ticker}] Data is already up-to-date. No action needed.")

    print("\n--- Data Pipeline Finished ---")


if __name__ == "__main__":
    run_pipeline()

