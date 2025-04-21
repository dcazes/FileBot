# main.py
import threading
import asyncio
import uvicorn
from graphiti_setup import setup_graphiti, start_watcher, scan_initial_files
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    try:
        graphiti = await setup_graphiti()
        await scan_initial_files(graphiti)
        watcher_thread = threading.Thread(target=start_watcher, args=(graphiti,))
        watcher_thread.start()
        uvicorn.run("server:app", host="0.0.0.0", port=8000)
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())