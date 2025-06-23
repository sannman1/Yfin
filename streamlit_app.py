import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import io
import sys
from contextlib import redirect_stdout
import os

# Import your existing pipeline and database functions
from main import run_pipeline
from postgre import create_table_if_not_exists

# --- Configuration ---
TICKERS_FILE = 'tickers.txt'
DEFAULT_TICKERS = ['TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS', 'INFY.NS', 'WIPRO.NS', 'TECHM.NS', 'LTIM.NS']
DB_URL = "postgresql://postgres:prabhu@localhost:5432/stocksdb"
engine = create_engine(DB_URL)

# --- Ticker Management Functions ---

def load_tickers():
    """Loads tickers from the tickers.txt file. Creates the file with defaults if it doesn't exist."""
    if not os.path.exists(TICKERS_FILE):
        with open(TICKERS_FILE, 'w') as f:
            for ticker in DEFAULT_TICKERS:
                f.write(f"{ticker}\n")
    
    with open(TICKERS_FILE, 'r') as f:
        tickers = [line.strip() for line in f.readlines() if line.strip()]
    return sorted(tickers)

def add_ticker(ticker_to_add):
    """Adds a new ticker to the tickers.txt file if it's not already there."""
    current_tickers = load_tickers()
    if ticker_to_add.upper() not in [t.upper() for t in current_tickers]:
        with open(TICKERS_FILE, 'a') as f:
            f.write(f"{ticker_to_add}\n")
        return True
    return False

# --- Streamlit App Layout ---

st.set_page_config(page_title="Stock Data Pipeline", layout="wide")
st.title("📈 Stock Data Pipeline")

# Load the current list of tickers
pipeline_tickers = load_tickers()

# --- Section 1: Synchronize Data ---
st.header("1. Synchronize Data")

# --- Sub-section: Add New Ticker ---
with st.expander("Add or View Tracked Tickers"):
    st.write("**Currently Tracked Tickers:**")
    # Display tickers in columns for better layout
    cols = st.columns(4)
    for i, ticker in enumerate(pipeline_tickers):
        cols[i % 4].write(f"- {ticker}")

    st.write("---")
    
    with st.form("add_ticker_form"):
        new_ticker = st.text_input("Enter New Ticker (e.g., SBIN.NS)", placeholder="SBIN.NS")
        submitted = st.form_submit_button("Add Ticker")

        if submitted and new_ticker:
            if add_ticker(new_ticker):
                st.success(f"Successfully added {new_ticker} to the list.")
                # This will rerun the script to immediately show the new ticker
                st.experimental_rerun()
            else:
                st.warning(f"{new_ticker} is already in the list.")
        elif submitted:
            st.error("Please enter a ticker symbol.")

# --- Sub-section: Run Pipeline ---
st.write("Click the button to synchronize data for all tracked tickers.")

if st.button("Run Sync for All Tracked Tickers"):
    with st.spinner("Pipeline is running... This may take a moment."):
        output_buffer = io.StringIO()
        try:
            with redirect_stdout(output_buffer):
                create_table_if_not_exists()
                run_pipeline(pipeline_tickers) # Use the dynamic list
            st.success("Pipeline finished successfully!")
            with st.expander("View Sync Logs", expanded=True):
                st.text_area("Logs", output_buffer.getvalue(), height=300)
        except Exception as e:
            st.error(f"An error occurred during the pipeline run: {e}")
            with st.expander("View Error Logs", expanded=True):
                st.text_area("Logs", output_buffer.getvalue(), height=300)


# --- Section 2: View Stored Data ---
st.header("2. View Stored Data")

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT DISTINCT ticker FROM stock_data ORDER BY ticker;"))
        db_tickers = [row[0] for row in result]
except Exception as e:
    st.warning("Could not connect to the database to fetch tickers.")
    db_tickers = []

selected_ticker = st.selectbox("Select a Ticker to View", options=db_tickers)

if selected_ticker:
    try:
        query = "SELECT date, open, high, low, close, adj_close, volume FROM stock_data WHERE ticker = :ticker ORDER BY date DESC"
        df = pd.read_sql(text(query), engine, params={'ticker': selected_ticker})
        st.write(f"Displaying latest data for **{selected_ticker}**")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Failed to fetch data for {selected_ticker}: {e}")