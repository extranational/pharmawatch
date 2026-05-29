# PharmaWatch: Multi-Tiered Storage Design Specification (v2.2)

## **1. Overview**
The PharmaWatch Multi-Tiered Storage Layer is designed to ingest, store, and query highly heterogeneous biopharmaceutical signals. The architecture bridges the gap between rigid relational requirements (for entity management and auditability) and the fluid, polymorphic nature of modern data sources (regulatory filings, social media, news).

By leveraging **PostgreSQL** with a **"Core + Extended Metadata"** strategy, we ensure high data integrity for core entities while providing the flexibility of a document store via `JSONB` for source-specific payloads.

---

## **2. Technology Stack**
- **Primary Database:** PostgreSQL 15+ (optimized for JSONB performance).
- **Orchestration:** Docker & Docker Compose (for rapid developer environment setup).
- **Data Format:** Relational (SQL) for structured fields; `JSONB` for polymorphic payloads.

---

## **3. Data Model Architecture**

The schema is split into three logical tiers: **The Signal Tier** (atomic events), **The Entity Tier** (normalized intelligence), and **The Source Tier** (provenance and technical metadata).

### **3.1. Tier 1: The Signal Tier (The Atomic Unit)**
The `signals` table acts as the entry point for all ingested data.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `signal_timestamp` | `TIMESTAMPTZ` | The actual time the event occurred. |
| `created_at` | `TIMESTAMPTZ` | Ingestion timestamp (audit). |
| `source_id` | `UUID` | Foreign Key to `sources`. |
| `language` | `VARCHAR(10)` | ISO language code. |
| `confidence` | `NUMERIC(3,2)` | Model-generated confidence score (0.00 - 1.00). |
| `raw_payload` | `JSONB` | **Polymorphic Layer:** Stores source-specific data (e.g., WeChat text vs. ClinicalTrials.gov XML structure). |

### **3.2. Tier 2: The Entity Tier (Normalized Intelligence)**
To avoid data silos, extracted intelligence is normalized into distinct entities.

#### `entities` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `entity_type` | `ENUM` | `DRUG`, `COMPANY`, `TARGET`, `LOCATION`, `DISEASE`. |
| `name` | `TEXT` | Normalized name (e.g., \"Pembrolizumab\"). |
| `external_id` | `TEXT` | Cross-reference ID (e.g., RxNorm, UniProt, or Wikidata ID). |

#### `signal_entities` Table (The Link)
This junction table links signals to entities, allowing for many-to-many relationships and contextual metadata.
| Column | Type | Description |
| :--- | :--- | :--- |
| `signal_id` | `UUID` | FK to `signals`. |
| `entity_id` | `UUID` | FK to `entities`. |
| `context_snippet` | `TEXT` | The text fragment where the entity was found. |
| `relationship` | `TEXT` | Semantic relation (e.g., \"inhibits\", \"manufactures\"). |

### **3.3. Tier 3: The Source Tier (Provenance)**
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `UUID` | Primary Key. |
| `source_name` | `TEXT` | (e.g., \"Twitter\", \"FDA_EDGAR\"). |
| `source_type` | `VARCHAR(10)` | (e.g., \"social\", \"regulatory\", \"news\"). |
| `technical_metadata`| `JSONB` | API endpoints, scraping credentials, or rate-limit info. |

---

## **4. Implementation Details**

### **4.1. Polymorphic Query Strategy**
By using `JSONB`, we can index specific fields within the polymorphic payload without altering the schema.

**Example: Querying all Clinical Trials in \"Phase III\" within the raw payload:**
```sql
SELECT id, signal_timestamp 
FROM signals 
WHERE raw_payload @> '{\"phase\": \"III\"}';
```

### **4.2. Indexing Strategy**
To maintain performance as the dataset grows:
1.  **GIN Index:** Applied to `signals.raw_payload` to enable fast searching within JSON structures.
2.  **B-Tree Index:** Applied to `signals.signal_timestamp` and `entities.name` for standard relational lookups.
3.  **Composite Index:** `signal_entities(entity_id, signal_id)` to accelerate entity-to-signal discovery.

---

## **5. Developer Environment Setup (Docker)**

The environment is orchestrated via `docker-compose.yml` for one-command deployment.

```yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    container_name: pharmawatch_db
    environment:
      POSTGRES_USER: dev_user
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: pharmawatch
    ports:
      - \"5432:5432\"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db:/docker-entrypoint-initdb.d # Contains schema.sql

volumes:
  postgres_data:
```

---

## **6. Scalability & Future Proofing**
- **Vertical Scaling:** PostgreSQL handles massive JSONB workloads well on high-memory instances.
- **Horizontal Scaling:** For future production needs, the `signals` table can be partitioned by `signal_timestamp` (Time-series partitioning).
- **Integrity:** The use of UUIDs ensures that data merged from different ingestion pipelines remains unique and avoids ID collisions.
