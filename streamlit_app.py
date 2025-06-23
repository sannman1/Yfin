# streamlit_app.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import io
import sys
from contextlib import redirect_stdout
from supabase import create_client, Client

# Import your other project files
from main import run_pipeline
from postgre import init_db_engine, create_table_if_not_exists

st.set_page_config(page_title="Stock Data Pipeline", layout="wide")

# --- Supabase & DB Initialization ---
@st.cache_resource
def init_supabase_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_supabase_client()

try:
    db_url = st.secrets["supabase"]["db_url"]
    init_db_engine(db_url)
    engine = create_engine(db_url)
except Exception as e:
    st.error(f"Could not configure the database. Please check your secrets: {e}")
    st.stop()

# --- CORRECTED Authentication Functions ---

def google_login():
    """
    Triggers the Google OAuth flow by getting the URL from Supabase
    and then using JavaScript to redirect the user's browser.
    """
    # 1. Get the sign-in URL from the Supabase client
    data = supabase.auth.sign_in_with_oauth({"provider": "google"})
    
    # 2. Use st.html to inject JavaScript that performs the redirect
    #    This command tells the user's browser to navigate to the URL.
    st.html(f'<script>window.location.href = "{data.url}";</script>')


def email_login(email, password):
    """Logs in the user via email/password."""
    try:
        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        st.session_state['user'] = session.user
        st.rerun()
    except Exception as e:
        st.error(f"Login failed: {e}")

def email_signup(email, password):
    """Signs up a new user via email/password."""
    try:
        supabase.auth.sign_up({"email": email, "password": password})
        st.success("Signup successful! Please check your email to confirm your account, then log in.")
    except Exception as e:
        st.error(f"Sign up failed: {e}")

def logout():
    """Logs out the user by clearing the session state."""
    if 'user' in st.session_state:
        del st.session_state['user']
    st.rerun()

# --- User-Specific Ticker Management (No changes needed) ---
def load_user_tickers(user_id):
    query = text("SELECT ticker FROM public.user_tickers WHERE user_id = :user_id ORDER BY ticker")
    with engine.connect() as connection:
        result = connection.execute(query, {'user_id': str(user_id)})
        tickers = [row[0] for row in result]
    return tickers

def add_user_ticker(user_id, ticker_to_add):
    clean_ticker = ticker_to_add.strip().upper()
    if not clean_ticker: return False
    query = text("INSERT INTO public.user_tickers (user_id, ticker) VALUES (:user_id, :ticker) ON CONFLICT (user_id, ticker) DO NOTHING")
    try:
        with engine.connect() as connection:
            connection.execute(query, {'user_id': str(user_id), 'ticker': clean_ticker})
            connection.commit()
        return True
    except Exception as e:
        st.error(f"Failed to add ticker: {e}")
        return False

# --- MAIN APP LOGIC (No changes needed below this line) ---

if 'user' not in st.session_state:
    try:
        session = supabase.auth.get_session()
        if session and session.user:
            st.session_state['user'] = session.user
            st.rerun()
    except Exception:
        pass

if 'user' not in st.session_state:
    st.title("Welcome to the Stock Data Pipeline")
    st.write("Please sign in or sign up to continue.")
    signin_tab, signup_tab = st.tabs(["Sign In", "Sign Up"])
    with signin_tab:
        st.button("Sign In with Google", on_click=google_login, use_container_width=True)
        st.divider()
        with st.form("email_login_form"):
            st.write("Or sign in with your email:")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign In")
            if submitted:
                email_login(email, password)
    with signup_tab:
        with st.form("email_signup_form"):
            st.write("Create a new account with your email:")
            email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", key="signup_password")
            submitted = st.form_submit_button("Sign Up")
            if submitted:
                email_signup(email, password)
else:
    user = st.session_state['user']
    st.title(f"📈 Stock Data Pipeline")
    st.sidebar.write(f"Logged in as: **{user.email}**")
    st.sidebar.button("Logout", on_click=logout)
    pipeline_tickers = load_user_tickers(user.id)
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
                if add_user_ticker(user.id, new_ticker):
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