"""
PharmaWatch Harvester Server – FastAPI
Exposes health check and scraping trigger endpoints.
"""

import os
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="PharmaWatch Harvester", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "harvester", "timestamp": datetime.utcnow().isoformat() + "Z"}

@app.get("/harvest")
async def run_harvest():
    """Trigger both scrapers (only works if Celery is running)."""
    try:
        from src.worker import scrape_chictr_task, scrape_nmpa_task
        r1 = scrape_chictr_task.delay()
        r2 = scrape_nmpa_task.delay()
        return JSONResponse(content={
            "status": "tasks_dispatched",
            "chictr_id": r1.id,
            "nmpa_id": r2.id,
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)