import asyncio
from src.chain.agent_chain import run_chain

asyncio.run(run_chain(
    watchlist_path="data/input/watchlist.csv",
    output_path="data/output/briefing.md"
))
