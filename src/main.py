import asyncio
import os
import sys
from src.chain.agent_chain import run_chain
from src.utils.logger import get_logger

logger = get_logger("MainLauncher")

async def wait_for_port(port: int, host: str = "127.0.0.1", timeout: int = 20):
    """
    Poller mechanism which makes sure all services are up and running before orchestration begins.
    """
    loop = asyncio.get_running_loop()
    start_time = loop.time()
    
    while (loop.time() - start_time) < timeout:
        try:
            # we check if the connection is open to make sure that an HTTP server is accepting traffic
            _, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return True
        except (ConnectionRefusedError, OSError):
            # else we sleep and retry again until the timeout is reached
            await asyncio.sleep(1)
    return False

async def wait_for_port_close(port: int, host: str = "127.0.0.1", timeout: int = 10):
    """
    Poller mechanism which makes sure all services are closed and cleaned before shutdown.
    """
    loop = asyncio.get_running_loop()
    start_time = loop.time()
    
    while (loop.time() - start_time) < timeout:
        try:
            _, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            # if we are still here it means the connection is still alive
            await asyncio.sleep(1)
        except (ConnectionRefusedError, OSError):
            # if we reached this step it means that we close the connection
            return True
    return False

async def start_server(module_path: str):
    """
    Function used to start each MCP server as a background process.
    """
    logger.info(f"Starting background server: {module_path}")
    
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", module_path,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    return process

async def main():

    tool_config = {
        "src.tools.watchlist": int(os.environ.get('WATCHLIST_PORT', 8000)),
        "src.tools.stock_price": int(os.environ.get('STOCK_PRICE_PORT', 8001)),
        "src.tools.news": int(os.environ.get('NEWS_PORT', 8002))
    }
    
    processes = []
    
    try:
        # start each of the mcp tools here
        for module in tool_config:
            proc = await start_server(module)
            processes.append(proc)
            
        # start the polling mechanism for each of the tools
        logger.info("Polling server ports for health checks...")
        checks = [wait_for_port(port) for port in tool_config.values()]
        results = await asyncio.gather(*checks)
        
        if not all(results):
            logger.error("One or more servers timed out during startup.")
            return

        logger.info("All MCP servers are online.")
        
        # after making sure all mcp servers are online, we start the agentic chain
        logger.info("Starting the financial research chain...")
        await run_chain(
            watchlist_path="data/input/watchlist.csv",
            output_path="data/output/briefing.md"
        )
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        
    finally:
        # cleanup to avoid memory leaks and zombie servers
        logger.info("Cleaning up: Sending shutdown signals to MCP servers...")
        for proc in processes:
            try:
                proc.terminate()
            except ProcessLookupError:
                pass
                
        logger.info("Verifying MCP servers have released their ports...")
        shutdown_checks = [wait_for_port_close(port) for port in tool_config.values()]
        shutdown_results = await asyncio.gather(*shutdown_checks)
        
        if not all(shutdown_results):
            logger.warning("Some ports did not close cleanly. Manual termination and checks may be required.")
        else:
            logger.info("All ports successfully released.")
            
        logger.info("All systems offline.")

if __name__ == "__main__":
    asyncio.run(main())

# to run the entire system, you can run from the terminal python -m src.main which will execute everything