# PharmaWatch: Data Schema Design Specification (v1.0)

## **1. Overview**
The goal of this schema is to provide a unified, scalable, and normalized data model for heterogeneous biopharmaceutical signals collected from diverse Chinese data sources (ChiCTR, NMPA, CNIPA, WeChat, etc.). 

The schema follows a **Core + Extended Metadata** pattern to accommodate both highly structured regulatory data and unstructured social/news signals.

---

## **2. Core Entity: The "Signal"**
All collected information is transformed into a "Signal" entity. This is the atomic unit of the PharmaWatch platform.

### **2.1 Common Metadata (Structured)**
These fields are mandatory for every signal to ensure cross-source correlation.

| Field Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `signal_id` | `UUID` | Primary Key | `550e8400-e29b-41d4-a716-446655440000` |
| `source_id` | `String` | Identifier for the origin source | `CHICTR`, `NMPA`, `WECHAT_OFFICIAL` |
| `source_url` | `String` | Original source link (if available) | `https://chictr.org.cn/ccr/register...` |
| `timestamp_raw` | `DateTime` | The original timestamp from the source | `2026-05-28T10:00:00Z` |
| `timestamp_ingested`| `DateTime` | When the signal entered our system | `2026-05-28T10:05:00Z` |
| `language` | `String` | Primary language of the source content | `zh-CN`, `en-US` |
| `confidence_score` | `Float` | LLM-assigned confidence in extraction | `0.95` |

### **2.2 The "Unified Entities" (Normalized)**
To enable cross-source intelligence (e.g., linking a patent to a clinical trial), we perform **Named Entity Recognition (NER)** during ingestion to populate these core fields.

| Field Name | Data Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `entities.drugs` | `Array[String]` | Standardized drug/molecule names | `["Imatinib", "格列卫"]` |
| `entities.companies`| `Array[String]` | Standardized company/sponsor names | `["Novartis", "诺华"]` |
| `entities.targets`  | `Array[String]` | Biological targets (e.g., proteins, receptors)| `["EGFR"]` |
| `entities.locations`| `Array[String]` | Clinical/Regulatory geography | `["Shanghai", "上海"]` |

### **2.3 Source-Specific Payload (Flexible)**
To capture the unique depth of each source (as identified in the Technical Feasibility Audit), we use a `payload` object (PostgreSQL `JSONB`).

#### **Example: ChiCTR Payload**
```json
{
  "trial_phase": "Phase III",
  "study_design": "Randomized, Double-Blind",
  "recruitment_status": "Recruiting",
  "primary_outcome": "Progression-free survival"
}
```

#### **Example: NMPA Payload**
```json
{
  "approval_number": "NMPA-2026-XXXX",
  "indication": "Non-small cell lung cancer",
  "dosage_form": "Oral Tablet"
}
```

#### **Example: WeChat/Unstructured Payload**
```json
{
  "content_summary": "Brief summary of the article...",
  "author_handle": "@BiopharmaNews",
  "engagement": {
    "likes": 1250,
    "shares": 300
  }
}
```

---

## **3. Relationship Mapping (The "Intelligence" Layer)**
The schema supports a `related_signals` table to facilitate manual or AI-driven correlation.

| Field Name | Data Type | Description |
| :--- | :--- | :--- |
| `relation_id` | `UUID` | Primary Key |
| `signal_a_id` | `UUID` | First Signal |
| `signal_b_id` | `UUID` | Second Signal |
| `relation_type` | `String` | Type of link (e.g., `PATENT_TO_TRIAL`, `NEWS_TO_APPROVAL`) |
| `evidence` | `Text` | LLM-generated reasoning for the link |

---

## **4. Implementation Notes**
* **Database Choice:** PostgreSQL is recommended due to its robust `JSONB` support for the flexible payload.
* **Language Strategy:** All entity names will follow the **Bilingual Rule** (English + Mandarin in brackets) to ensure searchability and precision.
* **Normalization:** A dedicated "Entity Master" table should eventually be used to resolve synonyms (e.g., mapping "Novartis" and "诺华" to a single ID).
