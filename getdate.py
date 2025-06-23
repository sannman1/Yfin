import pandas as pd
from postgre import get_existing_dates

def find_missing_dates(ticker: str, start_date: str, end_date: str) -> list:
    """
    Determines which dates are missing from the DB for a given date range.
    This is the core logic of the left box in the diagram.
    The return value is what the 'will think what to here' box represents.
    """
    # 1. Get a full list of business days for the desired range
    all_business_days = pd.bdate_range(start=start_date, end=end_date)
    all_business_days_str = {d.strftime('%Y-%m-%d') for d in all_business_days}

    # 2. Get the set of dates we already have in our database
    existing_dates_in_db = get_existing_dates(ticker)

    # 3. Find the difference
    missing_dates = sorted(list(all_business_days_str - existing_dates_in_db))
    
    print(f"[{ticker}] Total business days in range: {len(all_business_days_str)}")
    print(f"[{ticker}] Existing records in DB: {len(existing_dates_in_db)}")
    print(f"[{ticker}] Missing dates to fetch: {len(missing_dates)}")

    return missing_dates