from mcp.server.fastmcp import FastMCP
import yfinance as yf
from src.utils.logger import get_logger
from dotenv import load_dotenv
import os
load_dotenv()

HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("STOCK_PRICE_PORT", 8001))

logger = get_logger("StockPriceTool")
mcp = FastMCP("Stock Price Tool", host=HOST, port=PORT)

@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """
    Returns the current stock price for a given ticker symbol.
    """
    logger.info(f"Fetching current stock price for ticker: {ticker}")
    try:
        price = yf.Ticker(ticker).fast_info['last_price']
        logger.info(f"Retrieved price for {ticker}: {price:.2f}")
        return f"{price:.2f}"
    except Exception as e:
        logger.error(f"Error fetching price for {ticker}: {str(e)}")
        return f"Error fetching price for {ticker}: {str(e)}"

if __name__ == "__main__":
    logger.info(f"Starting the Stock Price Tool MCP Server on http://{HOST}:{PORT}/sse...")
    mcp.run(transport="sse")
