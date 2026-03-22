from mcp.server.fastmcp import FastMCP
import pandas as pd

mcp = FastMCP("Watchlist Tool", host="127.0.0.1", port=8000)

@mcp.tool()
def read_watchlist(file_path):

    df = pd.read_csv(file_path)
    
    # here we're assuming that the tickers are present in the csv
    # under a collumn named 'Ticker', that's why we need to make sure this
    # exists to avoid any errors being thrown
    if 'Ticker' not in df.columns:
        print("Error: The CSV is missing the required 'Ticker' column.")
        return []
        
    raw_tickers = df['Ticker'].dropna().tolist()
    
    # in case the user wrote the tickers with extra spaces, this ensures
    # that we will get them cleaned before passing them to the LLM
    clean_tickers = [str(ticker).strip() for ticker in raw_tickers if str(ticker).strip()]
    
    return clean_tickers

if __name__ == "__main__":
    mcp.run(transport="sse")

# to test it on mcp:
# run: python3 src/tools/watchlist.py
# then open a new terminal and run: npx @modelcontectprotocol/inspector (node.js needs to be installed for this)
# open the mcp window opened in the browser, put the url http://127.0.0.1:8000 and the transport sse
# then you can test the tool read_watchlist by providing the path data/input/watchlist.csv