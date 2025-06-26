# Yfin: Stock Data Pipeline (Main Branch - Streamlit App)

This branch of Yfin features a Streamlit web application that provides a user-friendly interface for managing stock data. It allows users to authenticate, track stock tickers, run the data pipeline, and visualize historical stock data, all through a web browser.

## Features

*   **Interactive Web UI:** A Streamlit-based application for easy interaction.
*   **User Authentication:** Secure login via Google OAuth or email/password (powered by Supabase).
*   **Personalized Ticker Management:** Users can add, view, and manage their own list of stock tickers.
*   **On-Demand Data Sync:** Trigger the data pipeline directly from the web interface to fetch and update stock data.
*   **Data Visualization:** View historical stock data for tracked tickers within the application.
*   **PostgreSQL Integration:** Stores all fetched data in a structured PostgreSQL database.

## Setup

### Prerequisites

*   Python 3.x
*   PostgreSQL database server
*   Supabase project (for authentication and database)

### Supabase and Database Setup

1.  **Create a Supabase Project:**
    Sign up for Supabase and create a new project. Note down your project URL and `anon` public key.

2.  **Configure Supabase Authentication:**
    Enable Google authentication in your Supabase project settings if you plan to use it.

3.  **Database Setup:**
    The Streamlit app connects to a PostgreSQL database. You can use the default PostgreSQL database provided by Supabase or configure your own.

    Ensure your database has a `public.user_tickers` table for storing user-specific tickers. The `postgre.py` script handles table creation for stock data.

4.  **Configure Streamlit Secrets:**
    Create a `.streamlit` directory in your project root if it doesn't exist. Inside, create a `secrets.toml` file with your Supabase credentials and database URL:

    ```toml
    # .streamlit/secrets.toml
    [supabase]
    url = "YOUR_SUPABASE_URL"
    key = "YOUR_SUPABASE_ANON_KEY"
    db_url = "postgresql://postgres:YOUR_DB_PASSWORD@db.YOUR_SUPABASE_PROJECT_REF.supabase.co:5432/postgres"
    ```
    Replace placeholders with your actual Supabase project details and database credentials.

### Install Dependencies

Navigate to the project root directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

To run the Streamlit application:

```bash
streamlit run streamlit_app.py
```

This will open the application in your web browser, typically at `http://localhost:8501`.

## Deployment

This Streamlit application can be deployed to Streamlit Community Cloud or other platforms that support Streamlit applications. Ensure your `secrets.toml` is correctly configured for the deployment environment.
