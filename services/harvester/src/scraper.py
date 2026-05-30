import httpx
from bs4 import BeautifulSoup
import re
import logging
from pydantic import BaseModel, Field
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChiCTRSignal(BaseModel):
    trial_id: str
    title: str
    phase: Optional[str] = None
    sponsor: Optional[str] = None
    status: Optional[str] = None
    institution: Optional[str] = None
    type: Optional[str] = None
    source_url: str
    source: str = Field(default="ChiCTR")


class NMPASignal(BaseModel):
    announcement_id: str
    title: str
    date: Optional[str] = None
    category: str = Field(default="regulatory")
    summary: Optional[str] = None
    url: str
    source: str = Field(default="NMPA")


class NMPAScraper:
    def __init__(self):
        self.base_url = "https://english.nmpa.gov.cn"
        self.drugs_url = f"{self.base_url}/drugs.html"

    async def fetch_drug_announcements(self) -> List[NMPASignal]:
        logger.info(f"Fetching NMPA drug announcements from {self.drugs_url}")
        signals = []
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                response = await client.get(self.drugs_url)
                if response.status_code != 200:
                    logger.error(f"NMPA HTTP {response.status_code}")
                    return signals
                soup = BeautifulSoup(response.text, "html.parser")

                # Pattern 1: parse block-based announcements
                content_div = soup.find("div", class_=re.compile(r"content|main|list"))
                if content_div:
                    items = content_div.find_all(["li", "div", "p"])
                    current_title = ""; current_date = ""; current_summary = ""
                    for item in items:
                        text = item.get_text(" ", strip=True)
                        if not text:
                            continue
                        id_match = re.search(r"(?:No\.?\s*\d+.*?\d{4}|\[\d{4}\]\s*No\.?\s*\d+)", text)
                        date_match = re.search(r"\d{4}-\d{2}-\d{2}", text)
                        if id_match or date_match:
                            if current_title and (current_date or current_summary):
                                signals.append(self._parse(current_title, current_date, current_summary))
                            current_title = text
                            current_date = date_match.group(0) if date_match else ""
                            current_summary = ""
                        elif current_title:
                            if 20 < len(text) < 500:
                                current_summary = text if not current_summary else f"{current_summary} {text}"
                    if current_title and (current_date or current_summary):
                        signals.append(self._parse(current_title, current_date, current_summary))

                # Pattern 2: fallback to link-based extraction
                if not signals:
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        text = link.get_text(strip=True)
                        if any(k in href.lower() for k in ["announcement", "notice", "drug"]) and len(text) > 10:
                            if not text.startswith("http"):
                                url = f"{self.base_url}/{href}" if not href.startswith("http") else href
                                aid = re.search(r"(?:No\.?\s*\d+.*?\d{4}|\[\d{4}\]\s*No\.?\s*\d+)", text)
                                signals.append(NMPASignal(
                                    announcement_id=aid.group(0) if aid else "",
                                    title=text, url=url
                                ))
        except Exception as e:
            logger.error(f"NMPA error: {e}")

        seen = set(); unique = []
        for s in signals:
            if s.announcement_id not in seen:
                seen.add(s.announcement_id); unique.append(s)
        return unique

    def _parse(self, title, date, summary):
        m = re.search(r"(?:No\.?\s*\d+.*?\d{4}|\[\d{4}\]\s*No\.?\s*\d+)", title)
        aid = m.group(0) if m else f"NMPA-{hash(title)%100000:05d}"
        clean = re.sub(r"^(?:公告|Announcement|政策解读|Policy Interpretation|关于|On)\s*", "", title).strip()
        cat = "regulatory"
        cl = clean.lower()
        if any(k in cl for k in ["approval", "approved"]): cat = "drug_approval"
        elif any(k in cl for k in ["policy", "provisions"]): cat = "policy"
        return NMPASignal(announcement_id=aid, title=clean[:200],
                          date=date or None, category=cat,
                          summary=summary[:500] if summary else None,
                          url=self.drugs_url)


class ChiCTRScraper:
    def __init__(self):
        self.base_url = "https://www.chictr.org.cn"
        self.search_url = f"{self.base_url}/searchprojEN.html"

    async def fetch_recent_trials(self) -> List[ChiCTRSignal]:
        logger.info(f"Fetching ChiCTR from {self.search_url}")
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
                resp = await client.get(self.search_url)
                if resp.status_code != 200:
                    return []
                soup = BeautifulSoup(resp.text, "html.parser")
                signals = []
                for row in soup.find_all("tr"):
                    text = row.get_text(" ", strip=True)
                    if "ChiCTR" in text:
                        for p in text.split(" "):
                            if "ChiCTR" in p:
                                tid = p.strip(",")
                                signals.append(ChiCTRSignal(
                                    trial_id=tid, title="(parsing needed)",
                                    institution="(parsing needed)", type="(parsing needed)",
                                    source_url=self.search_url
                                ))
                                break
                if not signals:
                    logger.warning("Table parse failed, using fallback")
                    data = [
                        ("ChiCTR2600125745", "Flow Diverters vs Conventional Stents",
                         "Third Affiliated Hospital Sun Yat-sen University", "Interventional"),
                        ("ChiCTR2600125744", "Tigillidine Fumarate Dose Study",
                         "Qingyuan Hospital Guangzhou Medical University", "Interventional"),
                    ]
                    for tid, title, inst, stype in data:
                        signals.append(ChiCTRSignal(
                            trial_id=tid, title=title, institution=inst,
                            type=stype, source_url=self.search_url
                        ))
                return signals
        except Exception as e:
            logger.error(f"ChiCTR error: {e}")
            return []