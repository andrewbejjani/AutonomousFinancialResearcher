from mcp.server.fastmcp import FastMCP
import yfinance as yf

mcp = FastMCP("Stock Price Tool", host="127.0.0.1", port=8001)

@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """
    Returns the current stock price for a given ticker symbol.
    """
    try:
        price = yf.Ticker(ticker).fast_info['last_price']
        return f"{price:.2f}"
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
