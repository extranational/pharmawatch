# PharmaWatch: Intelligence Orchestration Design Specification (v2.3)

## **1. Executive Summary**
The Intelligence Orchestration Layer (2.3) serves as the cognitive core of the PharmaWatch platform. It transitions raw ingested data into actionable biopharmaceutical intelligence through a structured, multi-stage processing pipeline. By utilizing a **LiteLLM Proxy**, we decouple the orchestration logic from specific LLM providers, ensuring observability, cost control, and model agility. The engine is specifically tuned to handle the complexities of biopharmaceutical data, including cross-lingual (English/Mandarin) synthesis and strict entity-linking requirements.

---

## **2. System Architecture Overview**

The architecture follows a "Mediated Pipeline" pattern:

1.  **Data Trigger:** The Ingestion Layer (2.1) populates the PostgreSQL database (2.2).
2.  **Orchestration Engine:** A Python-based service (utilizing Celery/FastAPI) monitors the database/message queue and orchestrates the workflow.
3.  **LLM Gateway (LiteLLM Proxy):** All intelligence requests pass through a centralized LiteLLM proxy. This layer provides a single OpenAI-compatible endpoint for all downstream workers.
4.  **Intelligence Pipeline:** A sequence of specialized LLM-driven tasks (NER $\rightarrow$ Linking $\rightarrow$ Synthesis).
5.  **Persistence:** Processed intelligence and structured metadata are written back to the PostgreSQL Storage Layer (2.2).

---

## **3. LiteLLM Proxy Integration**

To ensure production-grade reliability and observability, LiteLLM is integrated as the mandatory gateway for all LLM interactions.

### **3.1 Capabilities & Implementation**
* **Model Abstraction:** The Orchestration Engine communicates via the OpenAI API format. LiteLLM maps these requests to Google Gemini (for high-context reasoning), Anthropic Claude (for complex synthesis), or OpenAI GPT-4 (for rapid NER).
* **Unified Observability:**
    * **Cost Tracking:** Real-time monitoring of token usage per signal type (e.g., "News Signal" vs. "Clinical Trial Signal").
    * **Latency Metrics:** Tracking Time-To-First-Token (TTFT) and total request latency to optimize pipeline throughput.
    * **Centralized Logging:** Every prompt and completion is logged with unique `request_id`s, enabling full auditability of the "intelligence chain."
* **Fallback & Routing:** If a primary model (e.g., Gemini 1.5 Pro) reaches a rate limit, LiteLLM automatically routes to a fallback model (e.g., Claude 3.5 Sonnet) to prevent pipeline stalls.

### **3.2 Observability Stack**
| Metric | Tooling | Purpose |
| :--- | :--- | :--- |
| **LLM Telemetry** | LiteLLM + Langfuse | Tracking prompt/completion pairs, token costs, and latency. |
| **Pipeline Health** | Prometheus + Grafana | Monitoring Celery worker throughput and task success/failure rates. |
| **System Logs** | ELK Stack / Datadog | Aggregating logs from orchestration workers and the LiteLLM proxy. |

---

## **4. The Intelligence Processing Pipeline**

The pipeline is designed as a directed acyclic graph (DAG) of specialized tasks.

### Stage 1: Normalization & Named Entity Recognition (NER)
* **Objective:** Transform unstructured text into a structured "Semantic Skeleton."
* **Process:** The LLM identifies biopharmaceutical entities:
    * **Entities:** Genes, Proteins, Small Molecules, Biologics, Diseases, Clinical Trial IDs (NCT numbers), and Adverse Events (AEs).
    * **Attributes:** Dosage, frequency, efficacy markers, and patient demographics.
* **Output:** A JSON schema containing extracted entities and their immediate context.

### Stage 2: Semantic Enrichment & Entity Linking
* **Objective:** Ground extracted text in scientific reality.
* **Process:** 
    * **Ontology Mapping:** Entities from Stage 1 are mapped to standard biomedical ontologies (UMLS, MeSH, RxNorm, or Gene Ontology).
    * **Disambiguation:** Resolving whether "TNF" refers to the protein or the specific gene/pathway context within the signal.
* **Output:** Structured entity objects with unique identifiers (CUI/ID).

### Stage 3: Signal Synthesis & Cross-Source Aggregation
* **Objective:** The "Reasoning" step.
* **Process:** 
    * **Temporal Aggregation:** Combining current news with historical clinical trial data.
    * **Conflict Detection:** Identifying discrepancies (e.g., "Source A reports high efficacy; Source B reports significant toxicity").
    * **Synthesis:** Generating a cohesive narrative that explains the *evolution* of the signal.
* **Output:** An "Intelligence Brief" (high-level summary + detailed technical breakdown).

### Stage 4: Final Structured Output
* **Objective:** Write-back to the Storage Layer.
* **Process:** The synthesized intelligence is encapsulated in a polymorphic JSONB payload and saved to the PostgreSQL database, linked to the original raw signal IDs.

---

## **5. LLM Synthesis Engine & The "Bilingual Rule"**

A core requirement is the ability to synthesize signals originating from both English and Mandarin-language sources without loss of nuance.

### 5.1 The Bilingual Strategy
To prevent "Translation Drift" (where scientific nuances are lost in standard translation), the Orchestration Layer implements the following:
1. **Dual-Context Prompting:** When processing Mandarin sources, the LLM is instructed to extract terms in both the original Mandarin and the standardized English scientific equivalent (e.g., `{"entity": "PD-1", "original": "程序性死亡受体-1"}`).
2. **Hybrid Reasoning Space:** The internal "Chain-of-Thought" reasoning occurs in a high-dimensional space where the LLM is explicitly prompted to leverage the semantic overlap between the two languages.
3. **Output Integrity:** The final synthesis produces a primary English report but includes a "Linguistic Nuance" field for critical terms where the Mandarin context implies specific regulatory or clinical implications not captured in standard English translations.

---

## **6. Quality Assurance & Hallucination Detection**

To ensure the reliability of biopharmaceutical intelligence, we implement an **LLM-as-a-Judge** pattern.

* **Hallucination Check:** A secondary, highly-constrained LLM pass compares the *Synthesis* (Stage 3) against the *Raw Signal* (Stage 1). If the synthesis contains clinical claims (e.g., "improved survival by 20%") not present in the source, the task is flagged for human review.
* **Completeness Scoring:** Automated verification that all high-confidence entities identified in Stage 1 are appropriately addressed in the Stage 3 summary.
* **Success Rate Monitoring:** Real-time dashboarding of `Task_Success` vs. `Task_Hallucination_Flagged`.

---

## **7. Technology Stack Summary**

* **Orchestration:** Python, Celery, Redis.
* **LLM Gateway:** LiteLLM Proxy.
* **LLM Models:** Gemini 1.5 Pro (Primary), Claude 3.5 Sonnet (Secondary/Fallback).
* **Observability:** Langfuse (LLM traces), Prometheus/Grafana (Pipeline metrics).
* **Data Storage:** PostgreSQL (JSONB for polymorphic payloads).
