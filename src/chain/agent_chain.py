from langchain_mistralai import ChatMistralAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import date
import asyncio
import os
from dotenv import load_dotenv
from src.utils.logger import get_logger


load_dotenv()
logger = get_logger("AgentOrchestrator")

llm = ChatMistralAI(
    model="mistral-small-latest",  # free tier model
    temperature=0,
    api_key=os.environ.get("MISTRAL_API_KEY"),
)

# we connect to all three mcp servers here
# each server runs independently on its own port
# the chain just talks to them over sse, it doesn't care what's inside each tool
async def build_client():
    client = MultiServerMCPClient({
        "watchlist": {
            "url": f"http://127.0.0.1:{os.environ.get('WATCHLIST_PORT', 8000)}/sse",  # ← changed
            "transport": "sse",
        },
        "stock_price": {
            "url": f"http://127.0.0.1:{os.environ.get('STOCK_PRICE_PORT', 8001)}/sse",  # ← changed
            "transport": "sse",
        },
        "news": {
            "url": f"http://127.0.0.1:{os.environ.get('NEWS_PORT', 8002)}/sse",  # ← changed
            "transport": "sse",
        },
    })
    return client

async def run_chain(watchlist_path: str, output_path: str):
    # connect to all three mcp servers and grab their tools
    logger.info("Starting the Autonomous Financial Researcher pipeline...")
    try:

        client = await build_client()
        tools = await client.get_tools()

        # we need to find each tool by name so we can call them manually
        # the tool names come from what each mcp server registers
        try:
            watchlist_tool = next(t for t in tools if t.name == "read_watchlist")
            price_tool     = next(t for t in tools if t.name == "get_stock_price")
            news_tool      = next(t for t in tools if t.name == "get_news")
        except StopIteration:
            logger.error("Could not find one or more of the required MCP tools.")
            return

        # step 1: read the watchlist to get the list of tickers
        logger.info(f"Reading watchlist from {watchlist_path}...")
        tickers = await watchlist_tool.ainvoke({"file_path": watchlist_path})

        if not tickers:
            logger.error("No watchlist found, aborting the pipeline.")
            return
            
        logger.info(f"Found {len(tickers)} tickers: {tickers}")

        # step 2: for each ticker, fetch price and news in parallel
        # no point doing them one by one when we can do them all at once
        ticker_data = {}

        for raw_t in tickers:
            if isinstance(raw_t, dict) and "text" in raw_t:
                # extract the string and strip any list formatting if it was stringified
                ticker = raw_t["text"]
            else:
                ticker = str(raw_t)

            logger.info(f"Fetching price and news data for {ticker}...")

            try:
                # we run price and news fetch at the same time for each ticker
                price, news = await asyncio.gather(
                    price_tool.ainvoke({"ticker": ticker}),
                    news_tool.ainvoke({"ticker": ticker}),
                )

                ticker_data[ticker] = {
                    "price": price,
                    "news": news,
                }
            except Exception as e:
                logger.error(f"Failed to fetch data for {ticker}. Skipping. Error: {str(e)}")
                continue

        # step 3: format all the raw data into a single prompt for the llm
        # we just dump everything in a readable way and let the llm structure it
        logger.info("Structuring raw data for the LLM prompt...")
        raw_data_block = ""
        for ticker, data in ticker_data.items():
            raw_data_block += f"\n{ticker}:\n"
            raw_data_block += f"  Price: {data['price']}\n"
            raw_data_block += f"  News: {data['news']}\n"

        today = date.today().strftime("%B %d, %Y")

        # step 4: send everything to the llm and ask it to write the briefing
        logger.info("Connecting to LLM to generate the briefing...")

        messages = [
            SystemMessage(content=(
                "You are a financial research assistant. "
                "You receive raw stock price and news data and write a clean, concise daily briefing. "
                "For each stock write a short paragraph covering the current price and what the news says. "
                "Do not add any information that was not provided to you. Keep the tone neutral and factual."
            )),
            HumanMessage(content=(
                f"Today is {today}. Here is the raw data for each stock in the watchlist:\n"
                f"{raw_data_block}\n\n"
                "Please write the daily briefing."
            )),
        ]

        logger.info("Generating briefing...")
        response = await llm.ainvoke(messages)
        briefing = response.content

        # step 5: write the output to a markdown file
        # this is the final output the user reads
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write(f"# Daily Financial Briefing — {today}\n\n")
            f.write(briefing)

        logger.info(f"Briefing successfully written to {output_path}")

    except Exception as e:
        logger.error(f"A critical error occurred in the orchestration pipeline: {str(e)}")