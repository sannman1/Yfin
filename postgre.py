import pandas as pd
from sqlalchemy import (create_engine, inspect, MetaData, Table, Column, 
                        Integer, String, Float, Date, select)

# --- Database Configuration ---
DB_URL = "postgresql://postgres:prabhu@localhost:5432/stocksdb"
engine = create_engine(DB_URL)
metadata = MetaData()

# --- Table Definition ---
# --- THE ONLY CHANGE IS HERE ---
# Increased String length from 10 to 20 to accommodate longer tickers.
stock_data_table = Table('stock_data', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('ticker', String(20), nullable=False, index=True), #<-- INCREASED SIZE
    Column('date', Date, nullable=False, index=True),
    Column('open', Float, nullable=False),
    Column('high', Float, nullable=False),
    Column('low', Float, nullable=False),
    Column('close', Float, nullable=False),
    Column('adj_close', Float, nullable=False),
    Column('volume', Integer, nullable=False)
)

def create_table_if_not_exists():
    """Checks if the stock_data table exists and creates it if it doesn't."""
    inspector = inspect(engine)
    if not inspector.has_table(stock_data_table.name):
        print(f"Table '{stock_data_table.name}' not found. Creating it...")
        metadata.create_all(engine)
        print("Table created successfully.")
    else:
        print(f"Table '{stock_data_table.name}' already exists.")

def get_existing_dates(ticker: str) -> set:
    """
    Gets all dates for a given ticker that already exist in the database.
    This corresponds to the 'send requests for date' -> 'gets requested data' loop.
    """
    query = select(stock_data_table.c.date).where(stock_data_table.c.ticker == ticker)
    with engine.connect() as connection:
        result = connection.execute(query)
        # Convert date objects to string for easier comparison later
        existing_dates = {row.date.strftime('%Y-%m-%d') for row in result}
    return existing_dates

def save_data(data_df: pd.DataFrame):
    """
    Saves a pandas DataFrame with stock data to the database.
    This is called by main.py after yfindata.py fetches new data.
    """
    if data_df.empty:
        print("No new data to save.")
        return

    # Use pandas to_sql for efficient bulk insertion
    data_df.to_sql(
        stock_data_table.name,
        con=engine,
        if_exists='append',
        index=False
    )
    print(f"Successfully saved {len(data_df)} new records to the database.")
