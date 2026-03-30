from mcp.server.fastmcp import FastMCP
import yfinance as yf

# using port 8002 here to avoid conflicts with watchlist and stock_price tools
mcp = FastMCP("News Tool", host="127.0.0.1", port=8002)

@mcp.tool()
def fetch_news(ticker: str, max_articles: int = 3) -> list[dict]:
    """
    Returns the latest news headlines and summaries for a given ticker symbol.
    """
    
    try:
        stock = yf.Ticker(ticker)
        raw_news = stock.news
        
        if not raw_news:
            return []
            
        articles = []
        for item in raw_news:
            if len(articles) >= max_articles:
                break
                
            # yfinance sometimes nests the data under 'content', so handle both ways just in case
            content = item.get('content', item)
            
            title = content.get('title', '')
            summary = content.get('summary', '') or content.get('description', '')
            
            # simple filter to make sure the ticker actually shows up in the title or summary somewhere
            if ticker.upper() in title.upper() or ticker.upper() in summary.upper():
                
                # grab nested provider object safely if it exists
                provider = content.get('provider')
                source_name = provider.get('displayName') if isinstance(provider, dict) else "Yahoo Finance"
                
                articles.append({
                    "headline": title,
                    "summary": summary,
                    "url": content.get('canonicalUrl', content.get('link', '')),
                    "published_at": content.get('pubDate', content.get('providerPublishTime', '')),
                    "source": source_name
                })
        
        # fallback: if the filter was too strict and dropped everything, just revert 
        # to grabbing whatever top results yahoo gave us so we dont crash the chain
        if not articles:
            for item in raw_news[:max_articles]:
                content = item.get('content', item)
                provider = content.get('provider')
                source_name = provider.get('displayName') if isinstance(provider, dict) else "Yahoo Finance"
                
                articles.append({
                    "headline": content.get('title', ''),
                    "summary": content.get('summary', '') or content.get('description', ''),
                    "url": content.get('canonicalUrl', content.get('link', '')),
                    "published_at": content.get('pubDate', content.get('providerPublishTime', '')),
                    "source": source_name
                })
                
        return articles
        
    except Exception as e:
        return []

if __name__ == "__main__":
    mcp.run(transport="sse")

# to test it on mcp:
# run: python3 src/tools/news.py
# then open a new terminal and run: npx @modelcontextprotocol/inspector (make sure node.js is installed)
# open the mcp inspector in browser, put the url http://127.0.0.1:8002/sse and the transport sse
# then you can test the tool fetch_news by providing a ticker like "AAPL"
