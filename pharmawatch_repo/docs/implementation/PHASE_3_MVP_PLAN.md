# PharmaWatch: MVP Development Implementation Plan (Phase 3)

## Objective
Deliver a functional, end-to-end signal pipeline for the two highest-priority sources: **ChiCTR (Clinical Trials)** and **NMPA/NHSA (Regulatory Announcements)**.

---

## 1. Phase 3 Breakdown

### 3.1 Target Source Implementation (The "Harvesters")
**Goal:** Build reliable, automated collectors for the core sources.

* **Task 3.1.1: ChiCTR Collector (Python/uv)**
    * Implement a scraper/API client for the Chinese Clinical Trial Registry.
    * Focus on: Trial ID, Drug/Compound Name, Phase, Sponsor, and Status.
    * Strategy: Handle pagination and potential rate-limiting.
* **Task 3.1.2: NMPA/NHSA Collector (Python/uv)**
    * Implement a scraper for National Medical Products Administration announcements.
    * Focus on: Approval numbers, Drug Name, Manufacturer, and Date.
    * Strategy: Navigate dynamic content (if necessary) and robust error handling for structural changes.

### 3.2 End-to-End Pipeline Execution
**Goal:** Connect the collectors to the storage and intelligence layers.

* **Task 3.2.1: Ingestion & Storage Flow**
    * Connect Harvesters to the Redis task queue.
    * Implement the worker logic to save raw data to the "Data Lake" (simulated via local directory for MVP) and structured metadata to PostgreSQL.
* **Task 3.2.2: Intelligence Synthesis (LLM Pipeline)**
    * Implement the 4-stage orchestration pipeline (Normalization $\rightarrow$ Enrichment $\rightarrow$ Synthesis $\rightarrow$ Output).
    * Integrate the **LiteLLM Proxy** for all LLM calls.
    * Output synthesized summaries into the PostgreSQL `signals` table.

### 3.3 Minimal Viable Interface (The Dashboard)
**Goal:** Provide a way to view the results.

* **Task 3.3.1: FastAPI Backend**
    * Create endpoints to serve the latest synthesized signals from PostgreSQL.
* **Task 3.3.2: Simple Web UI (Bun/React/Tailwind)**
    * A clean, searchable dashboard showing a feed of clinical and regulatory signals.

### 3.4 Accuracy & Validation Loop
**Goal:** Ensure the intelligence is trustworthy.

* **Task 3.4.1: Verification Framework**
    * Create a simple mechanism to compare LLM-generated summaries against the raw source text.
    * Log "confidence scores" or manual "correct/incorrect" flags.

---

## 2. Technical Stack (MVP)

| Component | Technology |
| :--- | :--- |
| **Language (Backend/Scrapers)** | Python 3.11+ (managed via `uv`) |
| **Language (Frontend/UI)** | TypeScript (managed via `bun`) |
| **Task Queue** | Celery + Redis |
| **Database** | PostgreSQL |
| **LLM Gateway** | LiteLLM Proxy |
| **Containerization** | Docker + Docker Compose |
| **API Framework** | FastAPI |

---

## 3. Immediate Execution Order

1.  **Setup Dev Environment:** Create the `docker-compose.yml` and base Dockerfiles.
2.  **Build Harvesters (3.1):** Start with ChiCTR.
3.  **Build Pipeline (3.2):** Connect the dots.

---
*Status: Implementation Plan Ready*
*Author: Hermes*
