# PharmaWatch: Distributed Ingestion Layer Design (v1.0)

## **1. Overview**
The Distributed Ingestion Layer is responsible for the automated acquisition of raw data from disparate Chinese biopharmaceutical sources (ChiCTR, NMPA, WeChat, etc.). This layer must be highly scalable, resilient to anti-bot measures, and capable of handling both structured APIs and unstructured web content.

In the **development environment**, this layer will be implemented as a fleet of specialized, containerized Python microservices.

---

## **2. Technical Stack**

| Component | Tool | Purpose |
| :--- | :--- | :--- |
| **Runtime** | Python 3.13+ | Primary language for all ingestion logic. |
| **Package Management** | `uv` | High-performance dependency management and virtual environments. |
| **Task Orchestration** | Celery + Redis | Distributed task queue to manage scraping jobs and retries. |
| **Browser Automation** | Playwright | Handling dynamic JS rendering and complex anti-bot workflows. |
| **Containerization** | Docker | Packaging each scraper/collector as an independent, reproducible unit. |
| **Network/Proxy** | Residential Proxy Integration | Routing requests through China-based IPs to bypass geo-blocking. |

---

## **3. Architecture: The "Collector-Worker" Pattern**

We will utilize a distributed task-queue architecture to ensure that failure in one scraper does not impact the entire system.

### **3.1 Components**

1.  **Ingestion Scheduler (The "Brain"):**
    *   A lightweight service that dispatches tasks to the queue based on predefined schedules (e.g., "Scrape NMPA every 6 hours", "Monitor WeChat accounts every 30 minutes").
    *   Uses Celery Beat for periodic task scheduling.

2.  **Task Queue (The "Backbone"):**
    *   **Redis:** Acts as the message broker, holding the pending ingestion tasks.

3.  **Specialized Worker Fleet (The "Hands"):**
    *   Each worker is a Docker container running a specific `uv`-managed Python environment.
    *   **Scraper Workers:** (e.g., `worker-chictr`, `worker-nmpa`, `worker-wechat`). These are heavy-weight containers running Playwright to handle JS rendering and anti-bot challenges.
    *   **API Workers:** (e.g., `worker-cnipa`). These are lightweight containers designed for high-speed, direct API calls.

4.  **Result Backend:**
    *   Once a worker completes a task, it pushes the raw data (or a pointer to the raw data in the Data Lake) and the extraction metadata to the next stage in the pipeline.

---

## **4. Detailed Component Design**

### **4.1 The Scraper Workflow**
To handle the "Extremely High" complexity of sources like WeChat and CNKI, each scraper follows this lifecycle:
1.  **Task Acquisition:** Worker pulls a task from Redis.
2.  **Proxy Assignment:** Worker selects a China-based residential proxy from the pool.
3.  **Execution:**
    *   **Headless Browser Session:** Playwright initializes a browser instance.
    *   **Interaction:** Navigates to the target, handles cookies/sessions, and performs necessary searches.
    *   **Data Extraction:** Captigures HTML or parses the DOM for required data attributes.
4.  **Error Handling & Retry:**
    *   **Transient Errors:** (e.g., Timeout, 429 Rate Limit) $\rightarrow$ Exponential backoff retry via Celery.
    *   **Critical Errors:** (e.g., CAPTCHA encountered, Account Banned) $\rightarrow$ Task is moved to a "Dead Letter Queue" for manual investigation.
5.  **Data Handoff:** Raw payload is uploaded to the Raw Data Lake (Object Storage) and a metadata event is emitted.

### **4.2 Managing Dependencies with `uv`**
Each worker container will include a `pyproject.toml` managed by `uv`. This ensures:
*   **Lightning Fast Builds:** `uv` significantly reduces Docker image build times.
*   **Strict Versioning:** Ensures that a scraper developed on a local machine behaves identically in the container.

---

## **5. Development Environment Setup (Local)**

The entire ingestion layer will be orchestrated using **Docker Compose**.

**`docker-compose.yml` Structure:**
*   `redis`: Message broker.
*   `celery-beat`: The scheduler.
*   `worker-api`: Lightweight worker for direct API sources.
*   `worker-browser`: Heavyweight worker with Playwright/Browser dependencies.
*   `ingestion-monitor`: A small service to log worker health and task success/failure rates.

---

## **6. Future Considerations (Scale)**
While this design is optimized for the development environment, it is architecturally ready to scale to **Kubernetes (K8s)** in production, where the "Worker Fleet" can be dynamically scaled based on the depth of the Redis queue.
