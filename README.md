# Autonomous Financial Researcher

A Python-based agent that generates a daily financial briefing for a configurable stock watchlist. It reads a list of tickers, fetches current prices, retrieves relevant news, and writes a structured markdown report — without any manual steps.

Built using MCP (Model Context Protocol) as the interface between the LLM chain and its tools.


## Goal

- **Input:** `data/input/watchlist.csv` — a list of stock tickers
- **Output:** `data/output/briefing.md` — a structured daily briefing with prices and news per ticker


## Repository Layout

```
src/
  main.py               # Entry point — runs the full chain
  chain/
    agent_chain.py      # LLM chain: wires tools together and drives the run
  tools/
    watchlist.py        # MCP tool: reads the ticker list from CSV
    stock_price.py      # MCP tool: fetches current price for a ticker
    news.py             # MCP tool: fetches headlines and summaries for a ticker
data/
  input/
    watchlist.csv       # Your stock watchlist (one ticker per line)
  output/               # Generated briefings written here
tests/
  test_watchlist.py
  test_stock_price.py
  test_news.py
  test_chain.py
deployment/
  Dockerfile
  docker-compose.yml
```


## How to Run

### 1. Install

```bash
pip install -r requirements.txt
```

### 2. Configure

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

### 3. Edit your watchlist

Add tickers to `data/input/watchlist.csv`, one per line:

```
AAPL
MSFT
NVDA
```

### 4. Run

```bash
python src/main.py
```

The briefing is written to `data/output/briefing.md`.


## Run with Docker

```bash
docker compose up
```

---

## Tests

```bash
pytest tests/
```


## Environment Variables

| Variable | Description |
|---|---|
| `LLM_API_KEY` | API key for the language model |
| `STOCK_API_KEY` | API key for the stock price data source |
| `NEWS_API_KEY` | API key for the news data source |


## Team

| Member |
|---|
| Sanchay Bhutani | 
| Andrew Bejjani | 
| Vishakh Shah | 
| Sagar Vishishta |