# Yfin: Stock Data Pipeline (Local DB Feature Branch)

This branch of Yfin focuses on the automated pipeline for fetching historical stock data from Yahoo Finance and storing it in a PostgreSQL database. It operates by reading stock tickers from a `tickers.txt` file, similar to the `main` branch.

## Features

*   **Automated Data Fetching:** Automatically retrieves historical stock data for tickers listed in `tickers.txt`.
*   **Efficient Data Updates:** Identifies and fetches only missing historical data, preventing redundant downloads.
*   **PostgreSQL Integration:** Stores all fetched data in a structured PostgreSQL database.

## Setup

### Prerequisites

*   Python 3.x
*   PostgreSQL database server

### Database Setup

1.  **Create a PostgreSQL Database:**
    Create a new database named `stocksdb` (or your preferred name) in your PostgreSQL server.

    ```sql
    CREATE DATABASE stocksdb;
    ```

2.  **Configure Database Connection:**
    Open `postgre.py` and update the `DB_URL` variable with your PostgreSQL connection string. Ensure the username, password, host, port, and database name are correct.

    ```python
    DB_URL = "postgresql://your_username:your_password@your_host:your_port/stocksdb"
    ```

### Install Dependencies

Navigate to the project root directory and install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

1.  **Create `tickers.txt`:**
    In the project root directory, create a file named `tickers.txt`. Add one stock ticker symbol per line (e.g., `AAPL`, `MSFT`, `GOOGL`). This file is managed by the Streamlit app.

    ```
    SBIN.NS
    RELIANCE.NS
    ```

2.  **Run the Streamlit Application (Recommended):**
    The `streamlit_app.py` provides a user-friendly interface to manage tickers, run the data synchronization pipeline, and view the fetched stock data.

    To run the Streamlit app:

    ```bash
    streamlit run streamlit_app.py
    ```

    Once the app is running, you can:
    *   Add or remove stock tickers.
    *   Manually trigger the data synchronization process.
    *   View the historical stock data stored in your PostgreSQL database.

3.  **Run the Pipeline (CLI Only):**
    If you prefer to run the data fetching and storage process directly from the command line without the Streamlit interface, execute the `main.py` script:

    ```bash
    python main.py
    ```
