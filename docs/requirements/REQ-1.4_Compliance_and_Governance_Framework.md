# PharmaWatch: Compliance & Governance Framework

**Version:** 1.0  
**Status:** Draft / Project Requirement  
**Jurisdiction Focus:** People's Republic of China (PRC)  
**Last Updated:** May 28, 2026  

---

## 1. Introduction

### 1.1 Purpose
This framework establishes the legal, ethical, and technical boundaries for the PharmaWatch platform's data collection, processing, and utilization activities. As PharmaWatch relies on large-scale data ingestion within the Chinese jurisdiction to monitor biopharmaceutical trends, this document ensures alignment with national laws and ethical standards to mitigate legal, reputational, and operational risks.

### 1.2 Scope
This framework applies to all data acquisition activities, including web scraping, API integration, and database access, as well as the subsequent application of AI/ML models to the ingested data.

---

## 2. Legal Landscape (China)

All operations must comply with the "Three Pillars" of China's data regulation:

1.  **Cybersecurity Law (CSL):** Focuses on network security, critical information infrastructure (CII), and the protection of national security.
2.  **Data Security Law (DSL):** Regulates data processing activities, categorizes data based on importance (e.g., "Important Data"), and governs cross-border data transfers.
3.  **Personal Information Protection Law (PIPL):** Regulates the collection, processing, and use of personal information (PI), emphasizing user consent and individual rights.

---

## 3. Data Collection & Scraping Strategy

### 3.1 Social Media (WeChat Official Accounts, Zhihu)
*Social media data often contains Personal Information (PI) and is protected by platform Terms of Service (ToS).*

* **Legal Boundaries:**
    * **Unfair Competition:** Avoid scraping activities that disrupt the normal operation of the target platform or compete directly with their business model (e.g., mass-downloading content to replicate a service).
    * **ToS Compliance:** Respect `robots.txt` and platform-specific restrictions. Where possible, prioritize official APIs (e.g., WeChat Open Platform) over aggressive scraping.
    * **Anonymization:** Any data ingested from social media that contains identifiable individuals (usernames, profile pictures, personal opinions) must be immediately anonymized or pseudonymized to comply with PIPL.
* **Technical Constraints:**
    * Implement rate-limiting to prevent Denial of Service (DoS) patterns.
    * Avoid techniques that bypass security controls (e.g., CAPTCHA solving or credential stuffing), as these may trigger criminal liability under anti-hacking provisions.

### 3.2 Academic & Regulatory Databases (NMPA, CNKI, Wanfang, ChiCTR)
*These databases contain highly structured, proprietary, and copyright-protected information.*

* **Copyright & Database Rights:**
    * **Copyright Compliance:** Recognize that database structures and compiled academic works are protected under Chinese Copyright Law.
    * **Commercial vs. Public Access:** Distinguish between public regulatory filings (NMPA) and subscription-based academic repositories (CNKI, Wanfang).
    * **Access Methodology:** Prefer official API access or bulk-purchase agreements for commercial-grade data. If scraping is used, it must be limited to "fair use" scenarios (e.g., indexing metadata) rather than reproducing entire databases.
* **Regulatory Integrity:**
    * Ensure that data from official sources (NMPA, ChiCTR) is stored in its original, unaltered state to maintain a "Source of Truth" audit trail.

---

## 4. Data Privacy & Security

### 4.1 Data Residency & Cross-Border Transfer
*China has strict controls on the movement of data outside its borders.*

* **Localization Requirement:** Any data classified as "Important Data" or involving large volumes of "Personal Information" must be stored on servers located within the People's Republic of China.
* **Cross-Border Assessment:** Before transferring any data to international headquarters or cloud regions outside China, a mandatory **Data Export Security Assessment** must be conducted to ensure compliance with DSL and PIPL requirements.

### 4.2 Data Security Measures
* **Encryption:** Implement end-to-end encryption for data at rest (AES-256) and data in transit (TLS 1.3).
* **Access Control:** Employ the Principle of Least Privilege (PoLP). Access to sensitive biopharmaceutical datasets must be logged and audited.
* **Data Minimization:** Collect only the data necessary for the specific analytical purpose of PharmaWatch.

---

## 5. Ethical AI & Data Governance

### 5.1 Algorithmic Integrity
*Using LLMs to synthesize sensitive biopharmaceutical data carries unique risks.*

* **Mitigating Market Influence:** AI models must be tuned to provide factual synthesis rather than speculative sentiment. PharmaWatch must avoid generating content that could be construed as market manipulation or the spreading of "false information" under Chinese cybersecurity regulations.
* **Bias Detection:** Regularly audit LLM outputs for biases related to specific pharmaceutical companies, drugs, or regulatory bodies.
* **Transparency:** When AI-generated summaries are presented to users, they must be clearly labeled as "AI-Synthesized Content."

### 5.2 Human-in-the-Loop (HITL)
* High-impact insights (e.g., regulatory changes, clinical trial outcomes) must undergo human verification by subject matter experts before being disseminated via the platform.

---

## 6. Compliance Checklist

| Category | Requirement | Status | Responsible Party |
| :--- | :--- | :--- | :--- |
| **Scraping** | Respect `robots.txt` & Platform ToS | [ ] | Data Engineering |
| **Privacy** | Anonymize PII from Social Media | [ ] | Data Engineering / Legal |
| **Residency** | Confirm Data Localization in China | [ ] | DevOps / Infrastructure |
| **Copyright** | Verify Commercial Rights for CNKI/Wanfang | [ ] | Legal / Procurement |
| **AI Ethics** | Implement AI-Generated Content Disclaimers | [ ] | Product / AI Research |
| **Security** | Conduct Annual Data Security Audit | [ ] | Security/Compliance |
