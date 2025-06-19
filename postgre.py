import pandas as pd
from sqlalchemy import create_engine
from yfindata import get_stock_data

# Get stock data in-memory
df = get_stock_data()

# PostgreSQL connection
#                                    username  password   server     db name 
engine = create_engine("postgresql://postgres:prabhu@localhost:5432/stocksdb")

# Push to PostgreSQL
df.to_sql("stock_data", engine, if_exists="replace", index=False)

print("✅ Data pushed to PostgreSQL!")
