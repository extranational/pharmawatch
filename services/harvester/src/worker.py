import os
from celery import Celery
from src.scraper import ChiCTRScraper, ChiCTRSignal
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery('harvester', broker=REDIS_URL)

@app.task(name="harvester.scrape_chictr")
def scrape_chictr_task():
    logger.info("Starting ChiCTR scrape task...")
    scraper = ChiCTRScraper()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Simulation for MVP
    signal = loop.run_until_complete(scraper.scrape_trial_details("https://www.chictr.org.cn/indexEN.html"))
    
    if signal:
        logger.info(f"Successfully scraped signal: {signal.trial_id}")
        return signal.model_dump()
    
    return {"error": "No signals found"}

if __name__ == "__main__":
    app.start()