from mcp.server.fastmcp import FastMCP
import requests
import os

# Using port 8002 to avoid conflicts with watchlist (8000) and stock_price (8001)
mcp = FastMCP("News Tool", host="127.0.0.1", port=8002)

# Recommended: Load from environment variables instead of hardcoding
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "YOUR_API_KEY_HERE")
NEWS_API_URL = "https://newsapi.org/v2/everything"

@mcp.tool()
def fetch_news(ticker: str, max_articles: int = 3) -> list[dict]:
    """
    Fetches the latest news headlines and summaries for a given stock ticker.
    Filters by relevance into a structured return format.
    """
    print(f"Fetching news for {ticker}...")
    
    # -------------------------------------------------------------
    # OPTION A: REAL API CALL (uncomment and use when ready)
    # -------------------------------------------------------------
    # try:
    #     params = {
    #         "q": ticker,
    #         "apiKey": NEWS_API_KEY,
    #         "language": "en",
    #         "sortBy": "publishedAt",
    #         "pageSize": max_articles
    #     }
    #     response = requests.get(NEWS_API_URL, params=params)
    #     response.raise_for_status()
    #     data = response.json()
    #     
    #     articles = []
    #     for item in data.get("articles", []):
    #         articles.append({
    #             "headline": item.get("title"),
    #             "summary": item.get("description"),
    #             "url": item.get("url"),
    #             "published_at": item.get("publishedAt")
    #         })
    #     return articles
    # except Exception as e:
    #     print(f"Error fetching news for {ticker}: {e}")
    #     return []

    # -------------------------------------------------------------
    # OPTION B: MOCK RESPONSE FOR INITIAL TESTING
    # -------------------------------------------------------------
    mock_news = [
        {
            "headline": f"{ticker} Expected to Outperform Market Estimates",
            "summary": f"Analysts suggest {ticker} will see solid growth over the coming quarter following recent restructuring.",
            "url": f"https://finance.yahoo.com/quote/{ticker}/news",
            "published_at": "2026-03-28T09:00:00Z"
        },
        {
            "headline": f"New Sector Regulations Might Impact {ticker}",
            "summary": f"Government officials announced new guidelines that could affect {ticker}'s operations going forward.",
            "url": f"https://example.com/news/{ticker.lower()}-regulations",
            "published_at": "2026-03-28T08:30:00Z"
        }
    ]
    
    # Return limited number of articles
    return mock_news[:max_articles]

if __name__ == "__main__":
    # Run the server using Server-Sent Events (SSE) transport
    mcp.run(transport="sse")

# To test this tool on MCP:
# 1. Run: python3 src/tools/news.py
# 2. Open a new terminal and run: npx @modelcontextprotocol/inspector
# 3. Enter URL http://127.0.0.1:8002 and transport type SSE
# 4. You can then test the tool `fetch_news` by providing a ticker like "AAPL"
