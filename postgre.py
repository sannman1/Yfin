import pandas as pd
from sqlalchemy import (create_engine, inspect, MetaData, Table, Column,
                        Integer, String, Float, Date, select)

# --- REFACTORED DATABASE CONNECTION ---
# The engine is now initialized as None. It will be set by the main app.
engine = None
metadata = MetaData()

def init_db_engine(db_url: str):
    """Initializes the database engine for the entire application."""
    global engine
    engine = create_engine(db_url)
    # Associate the metadata with the new engine so create_all knows where to create tables
    metadata.bind = engine

# --- Table Definition ---
stock_data_table = Table('stock_data', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('ticker', String(20), nullable=False, index=True),
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
    if engine is None:
        raise Exception("Database engine not initialized. Call init_db_engine() first.")
    
    inspector = inspect(engine)
    if not inspector.has_table(stock_data_table.name):
        print(f"Table '{stock_data_table.name}' not found. Creating it...")
        # create_all knows which engine to use because we bound the metadata
        metadata.create_all(engine)
        print("Table created successfully.")
    else:
        print(f"Table '{stock_data_table.name}' already exists.")

def get_existing_dates(ticker: str) -> set:
    """Gets all dates for a given ticker that already exist in the database."""
    if engine is None:
        raise Exception("Database engine not initialized.")
    
    query = select(stock_data_table.c.date).where(stock_data_table.c.ticker == ticker)
    with engine.connect() as connection:
        result = connection.execute(query)
        existing_dates = {row.date.strftime('%Y-%m-%d') for row in result}
    return existing_dates

def save_data(data_df: pd.DataFrame):
    """Saves a pandas DataFrame with stock data to the database."""
    if engine is None:
        raise Exception("Database engine not initialized.")
    
    if data_df.empty:
        print("No new data to save.")
        return
        
    data_df.to_sql(
        stock_data_table.name,
        con=engine,
        if_exists='append',
        index=False
    )
    print(f"Successfully saved {len(data_df)} new records to the database.")
