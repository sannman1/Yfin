from getdate import find_missing_dates
from yfindata import fetch_stock_data
from postgre import save_data, create_table_if_not_exists
import pandas as pd
import os

# --- THIS IS THE ERRONEOUS LINE THAT MUST BE REMOVED ---
# from main import run_pipeline  <-- DELETE THIS LINE

# The rest of the file is correct.

def run_pipeline(tickers_to_process: list):
    """
    Main function to execute the data pipeline for a given list of tickers.
    """
    print("--- Starting Data Pipeline ---")
    
    create_table_if_not_exists()
    
    if not tickers_to_process:
        print("Ticker list is empty. Exiting.")
        return

    START_DATE = '2023-01-01'
    END_DATE = pd.to_datetime('today').strftime('%Y-%m-%d')

    for ticker in tickers_to_process:
        print(f"\n{'='*20} Processing: {ticker} {'='*20}")
        
        missing_dates = find_missing_dates(ticker, START_DATE, END_DATE)
        
        if missing_dates:
            fetch_start = missing_dates[0]
            fetch_end = missing_dates[-1]
            fetch_end_inclusive = (pd.to_datetime(fetch_end) + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            
            new_data_df = fetch_stock_data(ticker, fetch_start, fetch_end_inclusive)
            
            if not new_data_df.empty:
                new_data_df['date_str'] = new_data_df['date'].dt.strftime('%Y-%m-%d')
                final_data_to_save = new_data_df[new_data_df['date_str'].isin(missing_dates)].copy()
                final_data_to_save.drop(columns=['date_str'], inplace=True)
                save_data(final_data_to_save)
        else:
            print(f"[{ticker}] Data is already up-to-date. No action needed.")

    print("\n--- Data Pipeline Finished ---")

if __name__ == "__main__":
    TICKERS_FILE = 'tickers.txt'
    
    if not os.path.exists(TICKERS_FILE):
        print(f"Error: {TICKERS_FILE} not found. Please run the Streamlit app first to create it.")
    else:
        with open(TICKERS_FILE, 'r') as f:
            tickers_from_file = [line.strip() for line in f.readlines() if line.strip()]
        
        if tickers_from_file:
            print(f"Running pipeline for tickers found in {TICKERS_FILE}...")
            # The run_pipeline function is already available in this file's scope.
            run_pipeline(tickers_from_file)
        else:
            print("No tickers found in tickers.txt. Exiting.")