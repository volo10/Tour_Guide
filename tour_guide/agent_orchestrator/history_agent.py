"""
History Agent - Finds historical facts using Wikipedia API.
"""

import logging
import random
import re
import requests
from typing import List, Optional

from ..route_fetcher.models import Junction
from .models import AgentResult, AgentType
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class HistoryAgent(BaseAgent):
    """
    Agent that finds historical facts about a junction using Wikipedia API.
    Uses creative query building to find related historical content.
    """

    WIKI_USER_AGENT = "TourGuideApp/1.0 (https://github.com/tour-guide; tour@guide.com)"

    def __init__(self):
        super().__init__(AgentType.HISTORY, "History Finder")

    def process(self, junction: Junction) -> AgentResult:
        """Find historical facts about the junction using Wikipedia API."""
        street = junction.street_name
        address = junction.address or ""

        result = self._search_wikipedia(street, address, junction)
        if result:
            return result

        return self._create_error_result(junction, "No historical information found")

    def _search_wikipedia(self, street: str, address: str, junction: Junction) -> Optional[AgentResult]:
        """Search Wikipedia for historical information."""
        try:
            search_terms = self._get_search_terms(street, address)
            best_result = None
            best_score = 0

            headers = {"User-Agent": self.WIKI_USER_AGENT}

            for term in search_terms:
                wiki_url = "https://en.wikipedia.org/w/api.php"
                params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": term,
                    "format": "json",
                    "srlimit": 3,
                    "srprop": "snippet|titlesnippet",
                }

                response = requests.get(wiki_url, params=params, headers=headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    if "query" in data and "search" in data["query"]:
                        for item in data["query"]["search"]:
                            title = item.get("title", "")
                            snippet = self._clean_html(item.get("snippet", ""))
                            score = self._score_result(title, snippet, street)

                            if score > best_score:
                                best_score = score
                                page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
                                best_result = {
                                    "title": title,
                                    "snippet": snippet,
                                    "url": page_url,
                                    "score": score,
                                }

            if best_result and best_score > 20:
                extract = self._get_page_extract(best_result["title"])
                description = extract if extract else best_result["snippet"]

                return self._create_result(
                    junction=junction,
                    title=best_result["title"],
                    description=description[:300] + "..." if len(description) > 300 else description,
                    url=best_result["url"],
                    relevance_score=min(95, best_score),
                    quality_score=random.uniform(80, 95),
                    confidence=random.uniform(75, 92),
                    raw_data=best_result,
                )

        except requests.exceptions.RequestException as e:
            logger.error(f"Wikipedia API request error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in Wikipedia search: {e}")

        return None

    def _get_search_terms(self, street: str, address: str) -> List[str]:
        """Generate search terms for Wikipedia."""
        terms = []

        clean_street = self._clean_street_name(street)
        city = self._extract_city(address)

        # Check Israeli street name mappings
        terms.extend(self._get_israeli_figure_terms(clean_street))

        if clean_street and len(clean_street) > 2:
            if city:
                terms.append(f"{clean_street} {city}")
            terms.append(clean_street)

        if city:
            terms.append(f"{city} history")
            terms.append(city)

        terms.append("Israel history")
        terms.append("Tel Aviv history")

        return self._dedupe(terms, max_count=8)

    def _clean_street_name(self, street: str) -> str:
        """Clean navigation instructions from street name."""
        clean = street
        for suffix in [" St", " Street", " Ave", " Avenue", " Blvd", " Road",
                      "Go through", "roundabout", "Turn", "Continue", "Slight",
                      "Keep", "Merge", "Take", "exit"]:
            clean = clean.replace(suffix, "").strip()
        return clean.strip(" ,.-0123456789")

    def _extract_city(self, address: str) -> str:
        """Extract city from address."""
        address_lower = address.lower()
        if "tel aviv" in address_lower:
            return "Tel Aviv"
        elif "jerusalem" in address_lower:
            return "Jerusalem"
        elif "haifa" in address_lower:
            return "Haifa"
        return ""

    def _get_israeli_figure_terms(self, street: str) -> List[str]:
        """Map Israeli street names to historical figures."""
        israeli_figures = {
            "jabotinsky": "Ze'ev Jabotinsky",
            "herzl": "Theodor Herzl",
            "ben gurion": "David Ben-Gurion",
            "rothschild": "Rothschild Boulevard Tel Aviv",
            "dizengoff": "Dizengoff Street",
            "allenby": "Edmund Allenby",
            "rabin": "Yitzhak Rabin",
        }

        terms = []
        street_lower = street.lower()
        for key, wiki_term in israeli_figures.items():
            if key in street_lower:
                terms.append(wiki_term)
        return terms

    def _get_page_extract(self, title: str) -> Optional[str]:
        """Get a short extract from a Wikipedia page."""
        try:
            wiki_url = "https://en.wikipedia.org/w/api.php"
            headers = {"User-Agent": self.WIKI_USER_AGENT}
            params = {
                "action": "query",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "format": "json",
                "exsentences": 3,
            }

            response = requests.get(wiki_url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                pages = data.get("query", {}).get("pages", {})

                for page_id, page_data in pages.items():
                    if page_id != "-1":
                        return page_data.get("extract", "")

        except Exception as e:
            logger.debug(f"Wikipedia page extract error: {e}")

        return None

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        clean = re.sub(r'<[^>]+>', '', text)
        return clean.replace("&quot;", '"').replace("&amp;", "&")

    def _score_result(self, title: str, snippet: str, street: str) -> float:
        """Score a Wikipedia result based on relevance."""
        score = 30.0
        title_lower = title.lower()
        snippet_lower = snippet.lower()

        # Direct street name match
        for word in street.lower().split():
            if len(word) > 3 and word in title_lower:
                score += 25
                break

        # Historical keywords
        keywords = ["history", "founded", "established", "tel aviv", "israel"]
        for keyword in keywords:
            if keyword in title_lower or keyword in snippet_lower:
                score += 8

        return min(100, score)

    def _dedupe(self, items: List[str], max_count: int) -> List[str]:
        """Remove duplicates and limit count."""
        seen = set()
        unique = []
        for item in items:
            if item.lower() not in seen and item.strip():
                seen.add(item.lower())
                unique.append(item)
        return unique[:max_count]

    def _create_error_result(self, junction: Junction, error_msg: str) -> AgentResult:
        """Create an error result."""
        return self._create_result(
            junction=junction,
            title="History search failed",
            description=error_msg,
            url="",
            relevance_score=0,
            quality_score=0,
            confidence=0,
        )
