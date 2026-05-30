# Technical Feasibility Audit (REQ-1.3) - PharmaWatch

**Date:** May 27, 2026  
**Project:** PharmaWatch (Automated Monitoring for Chinese Biopharma)  
**Status:** Completed  

## 1. Executive Summary
This audit evaluates the technical viability of the four primary data source categories identified for the PharmaWatch platform. While regulatory and news sources present a high degree of feasibility via web scraping, social and professional platforms (specifically WeChat) present significant technical and operational hurdles. Academic repositories represent a middle ground, requiring sophisticated scraping and bypass strategies.

---

## 2. Detailed Source Analysis

### 2.1 Academic & Research Repositories (e.g., CNKI, Wanfang, arXiv)
*   **Primary Method:** Web Scraping (Secondary: Proprietary/Academic APIs).
*   **Feasibility:** **Moderate to Hard**
*   **Analysis:**
    *   **API Availability:** CNKI and Wanfang do not provide open, easy-to-use APIs for general research. While specialized search APIs exist (e.g., MagicCNKI), they are often undocumented or restricted.
    *   **Scraping Complexity:** High. These platforms employ advanced anti-bot mechanisms, including session management and behavioral analysis.
    *   **Technical Blockers:** Aggressive IP blocking and data protection regulations (e.g., China's data security laws) that target automated extraction of large-scale intellectual property.
    *   **Standardization:** Highly structured data (authors, titles, abstracts) makes post-extraction normalization straightforward.

### 2.2 Chinese Professional & Social Platforms (e.g., WeChat, Zhihu, DXY)
*   **Primary Method:** Specialized Scraping (Mobile Emulation/Headless Browsers).
*   **Feasibility:** **Hard**
*   **Analysis:**
    *   **API Availability:** Extremely low. WeChat is a closed ecosystem with no public API for content extraction.
    *   **Scraping Complexity:** Very High. Scraping WeChat requires navigating a mobile-first environment, often necessitating headless browsers (Playwright/Puppeteer) or mobile app emulation.
    *   **Technical Blockers:** 
        *   **CAPTCHAs:** Frequent and complex.
        *   **Account Requirements:** Many professional discussions require authenticated accounts, risking "account death" if automated behavior is detected.
        *   **Anti-Bot:** Advanced device fingerprinting and real-time behavioral monitoring.
    *   **Standardization:** Low. Content is unstructured (text, images, video, forum threads), requiring advanced LLM-based parsing to convert to "Signal" entities.

### 2.3 Regulatory & News Sources (e.g., NMPA, ChiCTR, Industry News)
*   **Primary Method:** Web Scraping & RSS/News APIs.
*   **Feasibility:** **Moderate to Easy**
*   **Analysis:**
    *   **API Availability:** NMPA and ChiCTR lack robust public APIs for real-time monitoring. News aggregators and major industry portals often provide RSS or limited API access.
    *   **Scraping Complexity:** Moderate. The primary challenge is handling complex HTML structures and frequent site updates.
    *   **Technical Blockers:** Periodic updates to site DOM and potential rate-limiting. Regulatory data protection measures (e.g., for CMC/clinical data) may restrict access to certain document types.
    *   **Standardization:** High. Clinical trials (ChiCTR) and regulatory filings (NMPA) follow standardized formats, facilitating high-confidence data extraction.

### 2.4 Subscription-based & Private Databases
*   **Primary Method:** API Integration.
*   **Feasibility:** **Easy (Budget Dependent)**
*   **Analysis:**
    *   **API Availability:** High. Most commercial intelligence providers offer structured APIs for authenticated subscribers.
    *   **Scraping Complexity:** Low (Prefer API over scraping to maintain reliability).
    *   **Technical Blockers:** API rate limits and the high cost of multi-provider subscriptions.
    *   **Standardization:** Very High. Data is delivered in structured formats (JSON/XML), minimizing normalization overhead.

---

## 3. Cross-Cutting Technical Challenges

### 3.1 Language & Localization
*   **Requirement:** Full support for Mandarin (Simplified Chinese).
*   **Challenges:**
    *   **NLP Complexity:** Requirement for high-performance LLMs capable of understanding nuanced Chinese pharmaceutical terminology.
    *   **OCR Requirements:** Extensive use of OCR will be necessary for data embedded in images (e.g., screenshots of social posts or scanned regulatory documents).
    *   **Encoding:** Handling various character encodings common in older Chinese web structures.

### 3.2 Infrastructure & Anti-Bot Mitigation
*   **Proxy Management:** Necessity of a robust proxy rotation strategy using **Chinese residential proxies** to avoid detection and regional IP blocking.
*   **Browser Fingerprinting:** Implementation of advanced browser fingerprinting evasion (e.g., using  plugins for Playwright/Puppeteer).
*   **CAPTCHA Solving:** Integration of automated CAPTCHA solving services for high-traffic/high-security endpoints.

---

## 4. Data Standardization Strategy
To achieve the goal of a unified "Signal" entity, the following pipeline is proposed:
1.  **Ingestion Layer:** Collects raw HTML/JSON/PDFs.
2.  **Extraction Layer:** Uses LLMs + Regex to pull key attributes (Drug, Company, Trial Phase, Molecule, etc.).
3.  **Normalization Layer:** Maps extracted attributes to a unified schema using a centralized Knowledge Graph (Entity Linking).
4.  **Validation Layer:** Cross-references signals (e.g., linking an NMPA filing to a ChiCTR trial) to increase confidence scores.

## 5. Summary Table

| Source Category | Feasibility | Primary Method | Main Blocker |
| :--- | :--- | :--- | :--- |
| **Academic** | Moderate | Scraping | Data Protection Laws |
| **Social/Prof.** | Hard | Mobile Emulation | Walled Garden / Accounts |
| **Regulatory** | Moderate/Easy | Scraping | Site Structure Changes |
| **Subscription**| Easy | API | Cost / Rate Limits |
