# Yfin: Stock Data Pipeline (Main Branch)

This branch of Yfin provides an automated pipeline to fetch historical stock data from Yahoo Finance and store it in a PostgreSQL database. It is designed for continuous data collection based on a predefined list of tickers.

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
    In the project root directory, create a file named `tickers.txt`. Add one stock ticker symbol per line (e.g., `AAPL`, `MSFT`, `GOOGL`).

    ```
    SBIN.NS
    RELIANCE.NS
    ```

2.  **Run the Pipeline:**
    Execute the `main.py` script to start the data fetching and storage process:

    ```bash
    python main.py
    ```