"""
PharmaWatch Orchestrator – 4-Stage Intelligence Pipeline
Normalizes → Enriches → Synthesizes → Outputs pharmaceutical signals.
"""

import os
import json
import logging
from datetime import datetime

from celery import Celery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── Celery App ────────────────────────────────────────

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:***@redis:6379/1")
LITELLM_URL = os.getenv("LITELLM_URL", "http://litellm:4000")

app = Celery("orchestrator", broker=REDIS_URL, backend="redis://redis:6379/1")

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

app.conf.task_routes = {
    "orchestrator.normalize": {"queue": "orchestrator"},
    "orchestrator.enrich": {"queue": "orchestrator"},
    "orchestrator.synthesize": {"queue": "orchestrator"},
    "orchestrator.output": {"queue": "orchestrator"},
    "orchestrator.health": {"queue": "orchestrator"},
}


# ─── Stage 1: Normalization ───────────────────────────

@app.task(name="orchestrator.normalize", bind=True)
def normalize_task(self, raw_signal: dict) -> dict:
    """Normalize a raw signal into a standard format."""
    source = raw_signal.get("source", "unknown")

    if source == "ChiCTR":
        return {
            "id": raw_signal.get("trial_id", f"CHI-{hash(str(raw_signal))}"),
            "source": "ChiCTR",
            "title": raw_signal.get("title", "Untitled"),
            "category": "clinical_trial",
            "date": raw_signal.get("date"),
            "institution": raw_signal.get("institution"),
            "type": raw_signal.get("type"),
            "raw_text": json.dumps(raw_signal, default=str),
        }
    elif source == "NMPA":
        return {
            "id": raw_signal.get("announcement_id", f"NMPA-{hash(str(raw_signal))}"),
            "source": "NMPA",
            "title": raw_signal.get("title", "Untitled"),
            "category": raw_signal.get("category", "regulatory"),
            "date": raw_signal.get("date"),
            "institution": None,
            "type": raw_signal.get("category"),
            "raw_text": json.dumps(raw_signal, default=str),
        }
    else:
        return {
            "id": f"UNK-{hash(str(raw_signal))}",
            "source": source,
            "title": raw_signal.get("title", "Untitled"),
            "category": "unknown",
            "raw_text": json.dumps(raw_signal, default=str),
        }


# ─── Stage 2: Enrichment ──────────────────────────────

@app.task(name="orchestrator.enrich", bind=True)
def enrich_task(self, normalized_signal: dict) -> dict:
    """Enrich a normalized signal with metadata and context."""
    signal_id = normalized_signal.get("id")
    title = normalized_signal.get("title", "")
    category = normalized_signal.get("category", "unknown")

    priority_map = {
        "clinical_trial": "high",
        "drug_approval": "high",
        "regulatory": "medium",
        "policy": "medium",
        "unknown": "low",
    }
    priority = priority_map.get(category, "low")

    keywords = []
    keywords_lower = title.lower()
    for kw in ["oncology", "diabetes", "cardiovascular", "covid", "vaccine",
               "gene therapy", "immunotherapy", "biosimilar", "generic", "novel"]:
        if kw in keywords_lower:
            keywords.append(kw)

    enrichment = {
        "priority": priority,
        "keywords": keywords,
        "country": "China",
        "language": "en",
        "enrichment_version": "1.0.0",
    }

    return {
        **normalized_signal,
        "enrichment": enrichment,
    }


# ─── Stage 3: Synthesis (LLM) ────────────────────────

@app.task(name="orchestrator.synthesize", bind=True)
def synthesize_task(self, enriched_signal: dict) -> dict:
    """Generate LLM synthesis of the enriched signal."""
    import httpx

    signal_id = enriched_signal.get("id")
    title = enriched_signal.get("title", "")
    category = enriched_signal.get("category", "")
    priority = enriched_signal.get("enrichment", {}).get("priority", "low")
    keywords = enriched_signal.get("enrichment", {}).get("keywords", [])

    prompt = f"""You are a pharmaceutical intelligence analyst. Summarize the following
signal in 2-3 sentences. Identify key insights and assign a confidence score (0.0-1.0).

Signal: {title}
Category: {category}
Priority: {priority}
Keywords: {keywords}

Return JSON with keys: "summary", "key_insights" (list of 2-3 strings), and "confidence" (float)."""

    try:
        async def call_llm():
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    f"{LITELLM_URL}/v1/chat/completions",
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "You are a pharmaceutical intelligence analyst."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                    },
                )
                return resp.json()

        import asyncio
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(call_llm())
        loop.close()

        choice = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        parsed = json.loads(choice)

        return {
            "id": signal_id,
            "source": enriched_signal.get("source", "unknown"),
            "title": title,
            "category": category,
            "summary": parsed.get("summary", title),
            "key_insights": parsed.get("key_insights", []),
            "confidence": parsed.get("confidence", 0.5),
            "enriched_at": enriched_signal.get("enriched_at"),
        }

    except Exception as e:
        logger.error(f"LLM synthesis failed for {signal_id}: {e}")
        return {
            "id": signal_id,
            "source": enriched_signal.get("source", "unknown"),
            "title": title,
            "category": category,
            "summary": f"[Auto-generated] {title}",
            "key_insights": [category, f"Priority: {priority}"] + keywords[:2],
            "confidence": 0.3,
            "enriched_at": enriched_signal.get("enriched_at"),
        }


# ─── Stage 4: Output / Storage ───────────────────────

@app.task(name="orchestrator.output", bind=True)
def output_task(self, synthesized: dict) -> dict:
    """Save synthesized signal and forward to dashboard."""
    import os
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)

    signal_id = synthesized.get("id", f"OUT-{hash(str(synthesized))}")
    output_path = os.path.join(output_dir, f"{signal_id}.json")

    synthesized["pipeline_version"] = "1.0.0"
    synthesized["created_at"] = datetime.utcnow().isoformat() + "Z"

    with open(output_path, "w") as f:
        json.dump(synthesized, f, indent=2, default=str)

    logger.info(f"Signal {signal_id} saved -> {output_path}")
    return {"status": "ok", "signal_id": signal_id, "file": output_path}


# ─── Pipeline Orchestration ───────────────────────────

@app.task(name="orchestrator.ingest_signals", bind=True)
def ingest_signals(self, signals_json: str) -> dict:
    """Orchestrate the full 4-stage pipeline for a batch of signals."""
    signals = json.loads(signals_json)
    results = []

    for raw in signals:
        try:
            normalized = self.send_task("orchestrator.normalize", args=[raw]).get()
            enriched = self.send_task("orchestrator.enrich", args=[normalized]).get()
            synthesized = self.send_task("orchestrator.synthesize", args=[enriched]).get()
            output = self.send_task("orchestrator.output", args=[synthesized]).get()
            results.append({"id": raw.get("trial_id", raw.get("announcement_id")), "status": "ok"})
        except Exception as e:
            logger.error(f"Pipeline failed for signal: {e}")
            results.append({"id": raw.get("trial_id", raw.get("announcement_id")), "status": "error", "error": str(e)})

    return {"status": "ok", "processed": len(results), "results": results}


@app.task(name="orchestrator.health")
def health_check() -> dict:
    return {"status": "healthy", "service": "orchestrator", "liteLLM": LITELLM_URL}


if __name__ == "__main__":
    app.start()