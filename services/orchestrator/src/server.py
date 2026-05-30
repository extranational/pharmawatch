"""
PharmaWatch Orchestrator Server – FastAPI
Provides health check and signal retrieval endpoints for the dashboard.
"""

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
from datetime import datetime

app = FastAPI(title="PharmaWatch Orchestrator API", version="1.0.0")

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/app/output")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/1")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "orchestrator-api", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/api/signals")
async def get_signals(limit: int = 50, source: str = None, category: str = None):
    signals = []
    if not os.path.exists(OUTPUT_DIR):
        return JSONResponse(content={"signals": [], "count": 0})
    for fname in sorted(os.listdir(OUTPUT_DIR), reverse=True):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(OUTPUT_DIR, fname)) as f:
                s = json.load(f)
            if source and s.get("source") != source:
                continue
            if category and s.get("category") != category:
                continue
            signals.append(s)
        except (json.JSONDecodeError, KeyError):
            continue
        if len(signals) >= limit:
            break
    return JSONResponse(content={"signals": signals, "count": len(signals)})


@app.get("/api/signals/stats")
async def get_stats():
    stats = {"total": 0, "by_source": {}, "by_category": {}, "avg_confidence": 0.0}
    if not os.path.exists(OUTPUT_DIR):
        return JSONResponse(content=stats)
    confidences = []
    for fname in os.listdir(OUTPUT_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(OUTPUT_DIR, fname)) as f:
                s = json.load(f)
            stats["total"] += 1
            src = s.get("source", "unknown")
            cat = s.get("category", "unknown")
            stats["by_source"][src] = stats["by_source"].get(src, 0) + 1
            stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            confidences.append(s.get("confidence", 0.5))
        except (json.JSONDecodeError, KeyError):
            continue
    stats["avg_confidence"] = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
    return JSONResponse(content=stats)