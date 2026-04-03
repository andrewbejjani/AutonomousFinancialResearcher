from mcp.server.fastmcp import FastMCP
import pandas as pd
from src.utils.logger import get_logger
from dotenv import load_dotenv
import os
load_dotenv()

HOST = "127.0.0.1"
PORT = int(os.environ.get("WATCHLIST_PORT", 8000))

logger = get_logger("WatchlistTool")
mcp = FastMCP("Watchlist Tool", host=HOST, port=PORT)

@mcp.tool()
def read_watchlist(file_path):
    """
    from a local CSV file with a 'Ticker' column this function returns a list of stock ticker symbols.
    for the implementation of the mcq wrapper with FastMCP, we relied on
    https://gofastmcp.com/getting-started/quickstart for examples 
    """
    logger.info(f"Attempting to read watchlist from: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        
        # here we're assuming that the tickers are present in the csv
        # under a collumn named 'Ticker', that's why we need to make sure this
        # exists to avoid any errors being thrown
        if 'Ticker' not in df.columns:
            logger.error(f"The CSV at '{file_path}' is missing the required 'Ticker' column")
            return []
    
        raw_tickers = df['Ticker'].dropna().tolist()
        
        # in case the user wrote the tickers with extra spaces, this ensures
        # that we will get them cleaned before passing them to the LLM
        clean_tickers = [str(ticker).strip() for ticker in raw_tickers if str(ticker).strip()]

        logger.info(f"Successfully loaded {len(clean_tickers)} tickers from the watchlist")
        return clean_tickers
    
    except FileNotFoundError:
        logger.error(f"Could not find the file at '{file_path}'. Please check the path.")
        return []
        
    except pd.errors.EmptyDataError:
        logger.error(f"The file at '{file_path}' is completely empty.")
        return []
        
    # this is for generic errors that we couldn't pinpoint their main reason
    except Exception as e:
        logger.error(f"An unexpected error occurred while reading the watchlist: {str(e)}")
        return []
    

if __name__ == "__main__":
    logger.info(f"Starting the Watchlist Tool MCP Server on http://{HOST}:{PORT} (SSE)...")
    mcp.run(transport="sse")


# to test it on mcp:
# run: python -m src.tools.watchlist
# then open a new terminal and run: npx @modelcontextprotocol/inspector (node.js needs to be installed for this)
# open the mcp window opened in the browser, put the url http://127.0.0.1:8000 and the transport sse
# then you can test the tool read_watchlist by providing the path data/input/watchlist.csv