# streamlit_app.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import io
import sys
from contextlib import redirect_stdout
import os

# Import your other project files
from main import run_pipeline
from postgre import create_table_if_not_exists, engine

st.set_page_config(page_title="Stock Data Pipeline", layout="wide")

# --- Ticker Management ---
TICKERS_FILE = 'tickers.txt'

def load_tickers():
    if not os.path.exists(TICKERS_FILE):
        return []
    with open(TICKERS_FILE, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_tickers(tickers):
    with open(TICKERS_FILE, 'w') as f:
        for ticker in tickers:
            f.write(f"{ticker}\n")

# --- MAIN APP LOGIC ---
st.title("📈 Stock Data Pipeline")

pipeline_tickers = load_tickers()

st.header("1. Synchronize Your Data")
with st.expander("Add or View Your Tracked Tickers", expanded=True):
    st.write("**Your Tracked Tickers:**")
    if not pipeline_tickers:
        st.info("You haven't added any tickers yet. Add one below to get started!")
    else:
        cols = st.columns(4)
        for i, ticker in enumerate(pipeline_tickers):
            cols[i % 4].write(f"- {ticker}")

    with st.form("add_ticker_form"):
        new_ticker = st.text_input("Enter New Ticker (e.g., SBIN.NS)", placeholder="SBIN.NS")
        submitted = st.form_submit_button("Add Ticker")
        if submitted:
            if new_ticker and new_ticker.strip().upper() not in pipeline_tickers:
                pipeline_tickers.append(new_ticker.strip().upper())
                save_tickers(pipeline_tickers)
                st.success(f"Successfully added {new_ticker.strip().upper()} to your list.")
                st.rerun()

if st.button("Run Sync for Your Tracked Tickers", use_container_width=True):
    if not pipeline_tickers:
        st.warning("Please add at least one ticker before running the sync.")
    else:
        with st.spinner("Pipeline is running... This may take a moment."):
            output_buffer = io.StringIO()
            try:
                with redirect_stdout(output_buffer):
                    create_table_if_not_exists()
                    run_pipeline(pipeline_tickers)
                st.success("Pipeline finished successfully!")
                with st.expander("View Sync Logs", expanded=True):
                    st.text_area("Logs", output_buffer.getvalue(), height=300)
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.header("2. View Your Stored Data")
selected_ticker = st.selectbox("Select a Ticker to View", options=pipeline_tickers)
if selected_ticker:
    try:
        query = "SELECT date, open, high, low, close, adj_close, volume FROM stock_data WHERE ticker = :ticker ORDER BY date DESC"
        df = pd.read_sql(text(query), engine, params={'ticker': selected_ticker})
        st.write(f"Displaying latest data for **{selected_ticker}**")
        st.dataframe(df)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")