import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import io
import sys
from contextlib import redirect_stdout
from supabase import create_client, Client

# Import your existing pipeline and database functions
from main import run_pipeline
from postgre import init_db_engine, create_table_if_not_exists

st.set_page_config(page_title="Stock Data Pipeline", layout="wide")

# --- Supabase & DB Initialization ---
@st.cache_resource
def init_supabase_client():
    """Initializes and returns the Supabase client."""
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_supabase_client()

# Initialize the database engine for PostgreSQL operations
try:
    db_url = st.secrets["supabase"]["db_url"]
    init_db_engine(db_url)
    engine = create_engine(db_url)
except Exception as e:
    st.error("Could not configure the database. Please check your secrets.toml file.")
    st.stop()

# --- Authentication Functions ---
def login(email, password):
    """Logs in the user and stores the session in st.session_state."""
    try:
        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state['user'] = session.user
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

def signup(email, password):
    """Signs up a new user and logs them in."""
    try:
        session = supabase.auth.sign_up({"email": email, "password": password})
        st.session_state['user'] = supabase.auth.get_user().user # Get user after sign up
        st.success("Signup successful! You are now logged in.")
        st.rerun()
    except Exception as e:
        st.error(f"Sign up failed: {e}")

def logout():
    """Logs out the user by clearing the session state."""
    if 'user' in st.session_state:
        del st.session_state['user']
    st.rerun()

# --- User-Specific Ticker Management ---
def load_user_tickers(user_id):
    """Loads tickers for a specific user from the user_tickers table."""
    query = text("SELECT ticker FROM public.user_tickers WHERE user_id = :user_id ORDER BY ticker")
    with engine.connect() as connection:
        result = connection.execute(query, {'user_id': str(user_id)})
        tickers = [row[0] for row in result]
    return tickers

def add_user_ticker(user_id, ticker_to_add):
    """Adds a new ticker for a specific user."""
    clean_ticker = ticker_to_add.strip().upper()
    if not clean_ticker:
        return False
    
    query = text("INSERT INTO public.user_tickers (user_id, ticker) VALUES (:user_id, :ticker) ON CONFLICT (user_id, ticker) DO NOTHING")
    try:
        with engine.connect() as connection:
            connection.execute(query, {'user_id': str(user_id), 'ticker': clean_ticker})
            connection.commit() # Important for INSERT statements
        return True
    except Exception as e:
        st.error(f"Failed to add ticker: {e}")
        return False

# --- MAIN APP LOGIC ---

# Check if the user is logged in
if 'user' not in st.session_state:
    # --- Logged Out View ---
    st.title("Welcome to the Stock Data Pipeline")
    st.write("Please log in or sign up to continue.")

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                login(email, password)

    with signup_tab:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            submitted = st.form_submit_button("Sign Up")
            if submitted:
                signup(email, password)
else:
    # --- Logged In View ---
    user = st.session_state['user']
    st.title(f"📈 Stock Data Pipeline")
    st.sidebar.write(f"Logged in as: **{user.email}**")
    st.sidebar.button("Logout", on_click=logout)
    
    pipeline_tickers = load_user_tickers(user.id)

    st.header("1. Synchronize Your Data")

    with st.expander("Add or View Your Tracked Tickers"):
        st.write("**Your Tracked Tickers:**")
        if not pipeline_tickers:
            st.info("You haven't added any tickers yet. Add one below to get started!")
        else:
            cols = st.columns(4)
            for i, ticker in enumerate(pipeline_tickers):
                cols[i % 4].write(f"- {ticker}")
        
        with st.form("add_ticker_form"):
            new_ticker = st.text_input("Enter New Ticker (e.g., sbin.ns)", placeholder="sbin.ns")
            submitted = st.form_submit_button("Add Ticker")
            if submitted:
                if add_user_ticker(user.id, new_ticker):
                    st.success(f"Successfully added {new_ticker.strip().upper()} to your list.")
                    st.rerun()

    if st.button("Run Sync for Your Tracked Tickers"):
        if not pipeline_tickers:
            st.warning("Please add at least one ticker before running the sync.")
        else:
            with st.spinner("Pipeline is running..."):
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
    
    # The dropdown now shows the user's personal list of tickers
    selected_ticker = st.selectbox("Select a Ticker to View", options=pipeline_tickers)
    
    if selected_ticker:
        try:
            query = "SELECT date, open, high, low, close, adj_close, volume FROM stock_data WHERE ticker = :ticker ORDER BY date DESC"
            df = pd.read_sql(text(query), engine, params={'ticker': selected_ticker})
            st.write(f"Displaying latest data for **{selected_ticker}**")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")