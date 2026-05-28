# REQ-1.1: Functional Requirements Mapping

## 1. Introduction
This document defines the functional requirements for the PharmaWatch platform, focusing on the definition of "Signals," their associated data attributes, and the core functionalities required to monitor, analyze, and alert users on developments in the Chinese biopharmaceutical sector.

## 2. Signal Definitions
A "Signal" is a discrete, actionable event or piece of information extracted from a monitored source that indicates a change or development in the biopharmaceutical landscape.

| Signal Type | Description | Example |
| :--- | :--- | :--- |
| **Clinical Trial Signal** | Updates to clinical trial status, phase changes, or new registrations. | "Trial for [Drug X] moved from Phase I to Phase II on ChiCTR." |
| **Regulatory Signal** | Official announcements from NMPA or NHSA regarding approvals, warnings, or policy changes. | "NMPA grants marketing authorization for [Drug Y]." |
| **IP/Patent Signal** | New patent filings, grants, or expirations involving pharmaceutical entities. | "New patent filed by [Company Z] for [Molecule A] in CNIPA." |
| **Academic/Scientific Signal** | Breakthrough findings, new studies, or pre-prints from academic databases. | "New study published in [Journal] regarding [Target B]." |
| **Market/Social Signal** | Trends, sentiment, or high-engagement discussions on professional/social platforms. | "Rising discussion on DXY regarding [Drug C] side effects." |

## 3. Core Data Entity: The "Signal"
Every detected Signal must be normalized into a common schema to allow for cross-source correlation and analysis.

### 3.1 Common Attributes
| Attribute | Type | Description |
| :--- | :--- | :--- |
| \`signal_id\` | UUID | Unique identifier for the signal. |
| \`signal_type\` | Enum | One of: Clinical, Regulatory, IP, Academic, Social. |
| \`event_timestamp\` | DateTime | The date/time the event occurred (extracted from source). |
| \`ingestion_timestamp\` | DateTime | The date/time the signal was ingested by PharmaWatch. |
| \`source_name\` | String | The origin of the signal (e.g., "ChiCTR", "NMPA", "CNIPA"). |
| \`source_url\` | URL | Direct link to the original evidence/source. |
| \`confidence_score\` | Float | 0.0 to 1.0; based on source reliability and LLM extraction accuracy. |
| \`summary\` | Text | A concise, LLM-generated summary of the signal. |
| \`raw_content_ref\` | String | Reference/Path to the raw data in the Data Lake. |

### 3.2 Entity-Specific Attributes
To enable deep analysis, signals must capture domain-specific entities.

| Entity Category | Attributes |
| :--- | :--- |
| **Drug/Molecule** | \`drug_name\`, \`molecule_id\`, \`mechanism_of_action\`, \`target_protein\`, \`indication\` |
| **Organization** | \`company_name\`, \`role\` (Sponsor/Assignee/Manufacturer), \`hq_location\` |
| **Clinical Trial** | \`trial_id\`, \`phase\`, \`recruitment_status\`, \`study_design\`, \`completion_date\` |
| **Intellectual Property**| \`patent_number\`, \`patent_class\`, \`filing_date\`, \`grant_date\` |

## 4. Functional Requirements

### 4.1 Data Ingestion & Processing
- **REQ-F1.1: Automated Multi-Source Ingestion:** The system shall automatically poll or scrape prioritized sources (ChiCTR, NMPA, CNIPA, etc.) at configurable intervals.
- **REQ-F1.2: Semantic Entity Extraction:** The system shall use LLMs to extract structured entities (Drugs, Companies, Targets) from unstructured text.
- **REQ-F1.3: Cross-Source Correlation:** The system shall identify when multiple signals from different sources refer to the same underlying event (e.g., a patent filing followed by a clinical trial registration).

### 4.2 User Interfaces & Analytics
- **REQ-F2.1: Real-time Signal Feed:** A dashboard providing a searchable, chronological feed of all validated signals.
- **REQ-F2.2: Historical Trend Analysis:** Visualizations of signal volume and activity trends (e.g., "Number of Phase III trials per quarter").
- **REQ-F2.3: Semantic Search Interface:** Users shall be able to perform natural language queries (e.g., "Show me all recent PD-1 inhibitor developments in China").
- **REQ-F2.4: Entity Deep-Dive:** A dedicated view for specific entities (e.g., a "Company Profile" showing all related signals).

### 4.3 Alerting & Notifications
- **REQ-F3.1: Custom Signal Thresholds:** Users shall be able to define personalized alert triggers (e.g., "Alert me if [Company X] has a new Phase III trial").
- **REQ-F3.2: Multi-Channel Notification:** The system shall support delivery via Slack, Email, and Webhooks.
- **REQ-F3.3: Intelligence Digests:** The system shall generate periodic (Daily/Weekly) summary reports containing high-confidence, high-impact signals.