# PharmaWatch: Dev-Focused Cloud-Native Infrastructure Design (2.4)

## Objective
To design a containerized, reproducible, and scalable local development stack that integrates the Ingestion, Storage, and Orchestration layers. This "glue" allows developers to spin up the entire PharmaWatch ecosystem with a single command.

## Core Principles
1. **Environment Parity:** Use Docker to ensure all developers work in an environment identical to the CI/CD and (eventually) production staging.
2. **Speed & Efficiency:** Leverage `uv` for Python dependency management and `bun` for Node.js/TypeScript tasks.
3. **Observability First:** Integrate the LiteLLM proxy as the central gateway for all LLM interactions to track costs, latency, and performance.
4. **Decoupled Services:** Each layer (Ingestion, Storage, Orchestration) runs in its own container, communicating via standard protocols (REST, gRPC, or Message Queues).

## Component Stack

### 1. Orchestration & Runtime
* **Docker Compose:** The primary tool for managing the multi-container development environment.
* **Container Registry:** Local registry or Docker Hub for storing custom images (e.g., our custom Harvester images).

### 2. The Service Layers (Containerized)
* **Ingestion Layer (The "Harvesters"):**
    * Managed by `uv` within custom Python Docker images.
    * Communicates with the task queue (Redis).
* **Storage Layer:**
    * **PostgreSQL:** Containerized database for structured metadata and signal storage.
    * **Redis:** Containerized message broker for Celery/task distribution.
* **Intelligence Orchestration Layer:**
    * A Python-based service managing the 4-stage pipeline.
    * Uses LiteLLM as the LLM gateway.

### 3. Observability & Tooling
* **LiteLLM Proxy:** Centralized container for all LLM requests.
* **Logging:** Centralized container logging (e.g., ELK stack or a lighter alternative like Loki/Grafana for dev).
* **Database Management:** Adminer or pgAdmin container for easy PostgreSQL inspection.

## Development Workflow (The "One-Command" Setup)

1. **`docker-compose up -d`**: Launches the entire stack.
2. **`uv run ...`**: For running local Python development tasks or testing specific harvesters.
3. **`bun run ...`**: For running any Node.js/TypeScript utility or dashboard.

## Implementation Roadmap (Infrastructure)

* **Step 1: Base Images:** Create optimized Dockerfiles for the Python Harvesters and Orchestration services using `uv`.
* **Step 2: Compose Orchestration:** Write the `docker-compose.yml` defining networks, volumes, and service dependencies.
* **Step 3: LiteLLM Integration:** Configure the LiteLLM proxy container and ensure all services route through it.
* **Step 4: Network & Volume Config:** Set up persistent volumes for PostgreSQL and Redis to ensure data survives container restarts.
* **Step 5: Health Checks:** Implement Docker health checks to ensure services start in the correct order (e.g., wait for Postgres before starting the Orchestrator).

---
*Status: Draft Design*
*Author: Hermes (on behalf of Archie)*
