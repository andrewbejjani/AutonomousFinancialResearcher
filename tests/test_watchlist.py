import tempfile
import os
import pandas as pd
from src.tools.watchlist import read_watchlist

def test_read_watchlist_integration():
    # we need to create a temporary csv to simulate a user watchlist
    # putting a couple tickers inside to verify our tool parses it right
    temp_dir = tempfile.gettempdir()
    dummy_csv = os.path.join(temp_dir, "dummy_watchlist.csv")
    
    try:
        # write some sample data that mimics the expected structure
        df = pd.DataFrame({"Ticker": ["AAPL", " MSFT ", "TSLA"]})
        df.to_csv(dummy_csv, index=False)
        
        # pass the path to the tool
        tickers = read_watchlist(dummy_csv)
        
        # assert it reads correctly and strips the whitespace from msft
        assert isinstance(tickers, list)
        assert len(tickers) == 3
        assert tickers == ["AAPL", "MSFT", "TSLA"]
        
    finally:
        # clean up after ourselves so we don't leave trash in the system
        if os.path.exists(dummy_csv):
            os.remove(dummy_csv)
