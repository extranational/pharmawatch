"""
PharmaWatch Harvester – Celery Worker
Connects ChiCTR + NMPA scrapers to Redis queue for downstream orchestration.
"""

import os
import json
import asyncio
import logging

from celery import Celery
from src.scraper import (
    ChiCTRScraper, ChiCTRSignal,
    NMPAScraper, NMPASignal,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
app = Celery("harvester", broker=REDIS_URL, backend="redis://redis:6379/1")

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@app.task(name="harvester.scrape_chictr", bind=True, max_retries=3)
def scrape_chictr_task(self) -> dict:
    """Scrape ChiCTR and push signals to the raw queue."""
    logger.info("🔬 Starting ChiCTR scrape task")
    scraper = ChiCTRScraper()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(scraper.fetch_recent_trials())
        loop.close()

        if results:
            signals = [s.model_dump() for s in results]
            app.send_task(
                "orchestrator.ingest_signals",
                args=[json.dumps(signals, default=str)],
                queue="orchestrator",
            )
            logger.info(f"ChiCTR: scraped {len(signals)} signals → queued for orchestration")
            return {"status": "ok", "count": len(signals), "source": "ChiCTR"}
        else:
            logger.warning("ChiCTR: no signals found")
            return {"status": "no_signals", "count": 0}

    except Exception as exc:
        logger.error(f"ChiCTR scrape failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@app.task(name="harvester.scrape_nmpa", bind=True, max_retries=3)
def scrape_nmpa_task(self) -> dict:
    """Scrape NMPA and push signals to the raw queue."""
    logger.info("🏛️ Starting NMPA scrape task")
    scraper = NMPAScraper()

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(scraper.fetch_drug_announcements())
        loop.close()

        if results:
            signals = [s.model_dump() for s in results]
            app.send_task(
                "orchestrator.ingest_signals",
                args=[json.dumps(signals, default=str)],
                queue="orchestrator",
            )
            logger.info(f"NMPA: scraped {len(signals)} signals → queued for orchestration")
            return {"status": "ok", "count": len(signals), "source": "NMPA"}
        else:
            logger.warning("NMPA: no signals found")
            return {"status": "no_signals", "count": 0}

    except Exception as exc:
        logger.error(f"NMPA scrape failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


@app.task(name="harvester.health")
def health_check() -> dict:
    return {"status": "healthy", "service": "harvester"}


if __name__ == "__main__":
    app.start()