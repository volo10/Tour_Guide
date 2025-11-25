"""
Agent Implementations.

Contains the four agents:
- VideoAgent: Finds relevant videos for junctions (YouTube API)
- MusicAgent: Finds music matching junction atmosphere (Spotify API)
- HistoryAgent: Finds historical facts about junctions (Wikipedia API)
- JudgeAgent: Evaluates and picks the winner
"""

import random
import time
import os
import base64
import requests
from typing import List, Optional, Dict, Any

from ..route_fetcher.models import Junction
from .models import AgentResult, AgentType, JudgeDecision
from .base_agent import BaseAgent
from ..config import (
    get_youtube_api_key,
    get_spotify_client_id,
    get_spotify_client_secret
)


class VideoAgent(BaseAgent):
    """
    Agent that finds relevant videos for a junction using YouTube API.

    Searches for street-level videos, walking tours,
    and location-specific content.
    """

    def __init__(self):
        super().__init__(AgentType.VIDEO, "Video Finder")
        self.youtube_api_key: Optional[str] = None

    def initialize(self, api_key: Optional[str] = None):
        """Initialize with optional YouTube API key."""
        super().initialize()
        self.youtube_api_key = api_key or get_youtube_api_key()

    def process(self, junction: Junction) -> AgentResult:
        """
        Find a relevant video for the junction using YouTube API.
        """
        street = junction.street_name
        address = junction.address

        # Try real YouTube API if key is available
        if self.youtube_api_key:
            result = self._search_youtube(street, address, junction)
            if result:
                return result

        # Fallback to simulated if no API key or search failed
        return self._simulated_result(junction)

    def _search_youtube(self, street: str, address: str, junction: Junction) -> Optional[AgentResult]:
        """Search YouTube API for relevant videos."""
        try:
            # Build search query - focus on location-specific content
            search_queries = [
                f"{street} Israel walking tour",
                f"{street} Tel Aviv",
                f"{address} street view",
            ]

            best_video = None
            best_score = 0

            for query in search_queries[:2]:  # Try first 2 queries
                youtube_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "key": self.youtube_api_key,
                    "maxResults": 3,
                    "order": "relevance",
                    "videoEmbeddable": "true",
                    "relevanceLanguage": "en",
                }

                response = requests.get(youtube_url, params=params, timeout=5)

                if response.status_code == 200:
                    data = response.json()

                    if "items" in data and data["items"]:
                        for item in data["items"]:
                            video_id = item["id"].get("videoId")
                            snippet = item["snippet"]
                            title = snippet.get("title", "")
                            description = snippet.get("description", "")
                            channel = snippet.get("channelTitle", "")

                            # Score the video based on relevance
                            score = self._score_video(title, description, street, address)

                            if score > best_score:
                                best_score = score
                                best_video = {
                                    "title": title,
                                    "description": description[:200] + "..." if len(description) > 200 else description,
                                    "url": f"https://www.youtube.com/watch?v={video_id}",
                                    "channel": channel,
                                    "score": score,
                                }

            if best_video:
                return self._create_result(
                    junction=junction,
                    title=best_video["title"],
                    description=f"{best_video['description']} (by {best_video['channel']})",
                    url=best_video["url"],
                    relevance_score=min(95, best_video["score"]),
                    quality_score=random.uniform(75, 90),
                    confidence=random.uniform(80, 95),
                    raw_data=best_video,
                )

        except requests.exceptions.RequestException as e:
            print(f"YouTube API error: {e}")
        except Exception as e:
            print(f"YouTube search error: {e}")

        return None

    def _score_video(self, title: str, description: str, street: str, address: str) -> float:
        """Score a video based on relevance to the location."""
        score = 60.0
        title_lower = title.lower()
        desc_lower = description.lower()
        street_lower = street.lower()

        # Check for street name in title/description
        if street_lower in title_lower:
            score += 20
        elif street_lower in desc_lower:
            score += 10

        # Bonus for relevant keywords
        relevant_keywords = ["walking", "tour", "drive", "street", "israel", "tel aviv",
                           "jerusalem", "guide", "explore", "visit"]
        for keyword in relevant_keywords:
            if keyword in title_lower:
                score += 5
            if keyword in desc_lower:
                score += 2

        return min(100, score)

    def _simulated_result(self, junction: Junction) -> AgentResult:
        """Fallback simulated result when API is unavailable."""
        street = junction.street_name
        return self._create_result(
            junction=junction,
            title=f"{street} - Street View Tour",
            description=f"Exploring {street} area (simulated - no YouTube API key)",
            url=f"https://youtube.com/results?search_query={street.replace(' ', '+')}+Israel",
            relevance_score=random.uniform(65, 80),
            quality_score=random.uniform(60, 75),
            confidence=random.uniform(50, 70),
        )


class MusicAgent(BaseAgent):
    """
    Agent that finds music related to a junction by searching Spotify directly.

    Searches Spotify using the street name and address to find relevant music.
    """

    def __init__(self):
        super().__init__(AgentType.MUSIC, "Music Finder")
        self.spotify_client_id: Optional[str] = None
        self.spotify_client_secret: Optional[str] = None
        self.spotify_token: Optional[str] = None
        self.token_expires_at: float = 0

    def initialize(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize with Spotify client credentials."""
        super().initialize()
        self.spotify_client_id = client_id or get_spotify_client_id()
        self.spotify_client_secret = client_secret or get_spotify_client_secret()

    def _get_spotify_token(self) -> Optional[str]:
        """Get or refresh Spotify access token."""
        if self.spotify_token and time.time() < self.token_expires_at:
            return self.spotify_token

        if not self.spotify_client_id or not self.spotify_client_secret:
            return None

        try:
            auth_url = "https://accounts.spotify.com/api/token"
            credentials = f"{self.spotify_client_id}:{self.spotify_client_secret}"
            encoded = base64.b64encode(credentials.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"grant_type": "client_credentials"}

            response = requests.post(auth_url, headers=headers, data=data, timeout=5)

            if response.status_code == 200:
                token_data = response.json()
                self.spotify_token = token_data["access_token"]
                self.token_expires_at = time.time() + token_data.get("expires_in", 3600) - 300
                return self.spotify_token

        except Exception as e:
            print(f"Spotify auth error: {e}")

        return None

    def process(self, junction: Junction) -> AgentResult:
        """
        Find music related to the junction by searching Spotify directly.
        """
        street = junction.street_name
        address = junction.address or ""

        # Get Spotify token
        token = self._get_spotify_token()
        if not token:
            return self._create_error_result(junction, "Spotify API credentials not configured")

        # Search Spotify using location-based queries
        result = self._search_spotify(junction, street, address)
        if result:
            return result

        return self._create_error_result(junction, "No music found for this location")

    def _search_spotify(self, junction: Junction, street: str, address: str) -> Optional[AgentResult]:
        """Search Spotify directly using the street/address."""
        try:
            # Generate search queries based on the actual address
            search_queries = self._build_search_queries(street, address)

            best_track = None
            best_score = 0

            for query in search_queries:
                spotify_url = "https://api.spotify.com/v1/search"
                headers = {
                    "Authorization": f"Bearer {self.spotify_token}",
                    "Content-Type": "application/json"
                }
                params = {
                    "q": query,
                    "type": "track",
                    "limit": 10,
                    "market": "IL"
                }

                response = requests.get(spotify_url, headers=headers, params=params, timeout=5)

                if response.status_code == 200:
                    data = response.json()

                    if "tracks" in data and "items" in data["tracks"]:
                        for track in data["tracks"]["items"]:
                            if not track:
                                continue

                            artists = ", ".join([a["name"] for a in track.get("artists", [])])
                            track_name = track.get("name", "")
                            popularity = track.get("popularity", 0)
                            track_url = track.get("external_urls", {}).get("spotify", "")
                            album = track.get("album", {}).get("name", "")

                            # Score based on popularity and query relevance
                            score = popularity

                            if score > best_score and track_url:
                                best_score = score
                                best_track = {
                                    "name": track_name,
                                    "artist": artists,
                                    "album": album,
                                    "url": track_url,
                                    "popularity": popularity,
                                    "query": query,
                                }

                # If we found a good track, stop searching
                if best_track and best_score >= 50:
                    break

            if best_track:
                return self._create_result(
                    junction=junction,
                    title=f"{best_track['name']} - {best_track['artist']}",
                    description=f"Found for: '{best_track['query']}'. Album: {best_track['album']}",
                    url=best_track["url"],
                    relevance_score=min(95, best_track["popularity"] + 10),
                    quality_score=best_track["popularity"],
                    confidence=random.uniform(80, 95),
                    raw_data=best_track,
                )

        except requests.exceptions.RequestException as e:
            print(f"Spotify API error: {e}")
        except Exception as e:
            print(f"Spotify search error: {e}")

        return None

    def _build_search_queries(self, street: str, address: str) -> List[str]:
        """
        Build search queries based on the actual street name and address.
        Returns a list of queries to try, most specific first.
        """
        queries = []

        # Clean the street name - remove navigation instructions
        clean_street = street
        for remove in ["Go through", "roundabout", "Turn left", "Turn right",
                       "Continue", "Slight", "Keep", "Merge", "Take exit"]:
            clean_street = clean_street.replace(remove, "").strip()

        # Remove trailing numbers and clean up
        clean_street = clean_street.strip(" ,.-")

        # Extract city from address if present
        city = ""
        address_lower = address.lower()
        if "tel aviv" in address_lower or "תל אביב" in address:
            city = "Tel Aviv"
        elif "jerusalem" in address_lower or "ירושלים" in address:
            city = "Jerusalem"
        elif "haifa" in address_lower or "חיפה" in address:
            city = "Haifa"

        # Query 1: Direct street name search
        if clean_street:
            queries.append(clean_street)

        # Query 2: Street + City
        if clean_street and city:
            queries.append(f"{clean_street} {city}")

        # Query 3: Just the city
        if city:
            queries.append(city)

        # Query 4: Extract meaningful words from street name for person-named streets
        # (e.g., "Jabotinsky" from "Ze'ev Jabotinsky St")
        street_words = clean_street.split()
        for word in street_words:
            if len(word) > 4 and word.isalpha():
                queries.append(word)

        # Query 5: City + music/songs
        if city:
            queries.append(f"{city} music")

        # Query 6: Israel as fallback
        queries.append("Israel")
        queries.append("Israeli music")

        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen and q.strip():
                seen.add(q.lower())
                unique_queries.append(q)

        return unique_queries[:6]  # Limit to 6 queries

    def _create_error_result(self, junction: Junction, error_msg: str) -> AgentResult:
        """Create an error result when Spotify search fails."""
        return self._create_result(
            junction=junction,
            title="Music search failed",
            description=error_msg,
            url="",
            relevance_score=0,
            quality_score=0,
            confidence=0,
        )


class HistoryAgent(BaseAgent):
    """
    Agent that finds historical facts about a junction using Wikipedia API.

    Researches the history of streets, buildings, and events
    at the location.
    """

    def __init__(self):
        super().__init__(AgentType.HISTORY, "History Finder")

    def process(self, junction: Junction) -> AgentResult:
        """
        Find historical facts about the junction using Wikipedia API.
        """
        street = junction.street_name
        address = junction.address

        # Try Wikipedia API search
        result = self._search_wikipedia(street, address, junction)
        if result:
            return result

        # Fallback to known Israeli street facts
        return self._fallback_result(junction)

    def _search_wikipedia(self, street: str, address: str, junction: Junction) -> Optional[AgentResult]:
        """Search Wikipedia for historical information about the location."""
        try:
            # Extract key terms for search
            search_terms = self._get_search_terms(street, address)

            best_result = None
            best_score = 0

            for term in search_terms[:3]:  # Try first 3 search terms
                # Wikipedia API search
                wiki_search_url = "https://en.wikipedia.org/w/api.php"
                search_params = {
                    "action": "query",
                    "list": "search",
                    "srsearch": term,
                    "format": "json",
                    "srlimit": 3,
                    "srprop": "snippet|titlesnippet",
                }

                response = requests.get(wiki_search_url, params=search_params, timeout=5)

                if response.status_code == 200:
                    data = response.json()

                    if "query" in data and "search" in data["query"]:
                        for item in data["query"]["search"]:
                            title = item.get("title", "")
                            snippet = item.get("snippet", "")

                            # Clean up HTML from snippet
                            snippet = self._clean_html(snippet)

                            # Score the result
                            score = self._score_result(title, snippet, street)

                            if score > best_score:
                                best_score = score

                                # Get the page URL
                                page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

                                best_result = {
                                    "title": title,
                                    "snippet": snippet,
                                    "url": page_url,
                                    "score": score,
                                }

            # If we found a good result, get more details
            if best_result and best_score > 40:
                # Try to get extract for more description
                extract = self._get_page_extract(best_result["title"])
                if extract:
                    best_result["description"] = extract
                else:
                    best_result["description"] = best_result["snippet"]

                return self._create_result(
                    junction=junction,
                    title=best_result["title"],
                    description=best_result["description"][:300] + "..." if len(best_result.get("description", "")) > 300 else best_result.get("description", ""),
                    url=best_result["url"],
                    relevance_score=min(95, best_score),
                    quality_score=random.uniform(80, 95),
                    confidence=random.uniform(75, 92),
                    raw_data=best_result,
                )

        except requests.exceptions.RequestException as e:
            print(f"Wikipedia API error: {e}")
        except Exception as e:
            print(f"Wikipedia search error: {e}")

        return None

    def _get_search_terms(self, street: str, address: str) -> List[str]:
        """Generate search terms for Wikipedia based on location."""
        terms = []

        # Clean street name - remove common suffixes and navigation instructions
        clean_street = street
        for suffix in [" St", " Street", " Ave", " Avenue", " Blvd", " Road", " Rd",
                      "Go through", "roundabout", "Turn", "Continue"]:
            clean_street = clean_street.replace(suffix, "").strip()

        # Israeli street name mappings to historical figures
        israeli_figures = {
            "jabotinsky": "Ze'ev Jabotinsky",
            "herzl": "Theodor Herzl",
            "ben gurion": "David Ben-Gurion",
            "weizmann": "Chaim Weizmann",
            "rothschild": "Rothschild Boulevard Tel Aviv",
            "dizengoff": "Dizengoff Street",
            "allenby": "Allenby Street Tel Aviv",
            "king george": "King George Street Tel Aviv",
            "king david": "King David Hotel",
            "ibn gabirol": "Solomon ibn Gabirol",
            "bialik": "Hayim Nahman Bialik",
            "nordau": "Max Nordau",
            "arlozorov": "Haim Arlosoroff",
            "rabin": "Yitzhak Rabin",
            "begin": "Menachem Begin",
            "kaplan": "Eliezer Kaplan",
            "namir": "Mordechai Namir",
        }

        # Check for known Israeli streets
        street_lower = clean_street.lower()
        for key, wiki_term in israeli_figures.items():
            if key in street_lower:
                terms.append(wiki_term)

        # Add location-based searches
        if "tel aviv" in address.lower() or "תל אביב" in address:
            terms.append(f"{clean_street} Tel Aviv")
            terms.append("Tel Aviv history")
        elif "jerusalem" in address.lower() or "ירושלים" in address:
            terms.append(f"{clean_street} Jerusalem")
            terms.append("Jerusalem history")
        elif "haifa" in address.lower() or "חיפה" in address:
            terms.append(f"{clean_street} Haifa")

        # Generic search
        terms.append(clean_street)

        return terms[:5]  # Limit to 5 terms

    def _get_page_extract(self, title: str) -> Optional[str]:
        """Get a short extract from a Wikipedia page."""
        try:
            wiki_url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "titles": title,
                "prop": "extracts",
                "exintro": True,
                "explaintext": True,
                "format": "json",
                "exsentences": 3,
            }

            response = requests.get(wiki_url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                pages = data.get("query", {}).get("pages", {})

                for page_id, page_data in pages.items():
                    if page_id != "-1":  # -1 means page not found
                        return page_data.get("extract", "")

        except Exception:
            pass

        return None

    def _clean_html(self, text: str) -> str:
        """Remove HTML tags from text."""
        import re
        clean = re.sub(r'<[^>]+>', '', text)
        clean = clean.replace("&quot;", '"').replace("&amp;", "&")
        return clean

    def _score_result(self, title: str, snippet: str, street: str) -> float:
        """Score a Wikipedia result based on relevance."""
        score = 30.0
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        street_lower = street.lower()

        # Direct street name match
        street_words = street_lower.split()
        for word in street_words:
            if len(word) > 3 and word in title_lower:
                score += 25
                break

        # Historical keywords
        historical_keywords = ["history", "historical", "founded", "established",
                              "named after", "politician", "leader", "street",
                              "avenue", "boulevard", "tel aviv", "israel"]
        for keyword in historical_keywords:
            if keyword in title_lower or keyword in snippet_lower:
                score += 8

        return min(100, score)

    def _fallback_result(self, junction: Junction) -> AgentResult:
        """Provide a fallback result with known Israeli street facts."""
        street = junction.street_name

        # Known Israeli streets and their history
        known_streets = {
            "jabotinsky": {
                "title": "Ze'ev Jabotinsky",
                "description": "Ze'ev Jabotinsky (1880-1940) was a Revisionist Zionist leader, writer, and founder of the Jewish Self-Defense Organization in Odessa. Streets named after him commemorate his significant role in Jewish history and the establishment of Israel.",
                "url": "https://en.wikipedia.org/wiki/Ze%27ev_Jabotinsky"
            },
            "herzl": {
                "title": "Theodor Herzl",
                "description": "Theodor Herzl (1860-1904) was the father of modern political Zionism and founder of the World Zionist Organization. He authored 'Der Judenstaat' which called for the creation of a Jewish homeland.",
                "url": "https://en.wikipedia.org/wiki/Theodor_Herzl"
            },
            "rothschild": {
                "title": "Rothschild Boulevard",
                "description": "Rothschild Boulevard is one of Tel Aviv's most famous streets, lined with Bauhaus buildings. It's named after the Rothschild family who supported early Jewish settlement in Palestine. The Israeli Declaration of Independence was signed here in 1948.",
                "url": "https://en.wikipedia.org/wiki/Rothschild_Boulevard"
            },
            "dizengoff": {
                "title": "Dizengoff Street",
                "description": "Named after Meir Dizengoff, the first mayor of Tel Aviv (1921-1936). Dizengoff Street became the cultural heart of Tel Aviv and remains one of its most vibrant thoroughfares.",
                "url": "https://en.wikipedia.org/wiki/Dizengoff_Street"
            },
            "ben gurion": {
                "title": "David Ben-Gurion",
                "description": "David Ben-Gurion (1886-1973) was the primary founder and first Prime Minister of Israel. He proclaimed the establishment of the State of Israel on May 14, 1948.",
                "url": "https://en.wikipedia.org/wiki/David_Ben-Gurion"
            },
            "ibn gabirol": {
                "title": "Solomon ibn Gabirol",
                "description": "Solomon ibn Gabirol (c. 1021-1070) was an Andalusian Jewish poet and philosopher. He composed both religious and secular poetry and wrote philosophical works that influenced both Jewish and Christian thought.",
                "url": "https://en.wikipedia.org/wiki/Solomon_ibn_Gabirol"
            },
            "king george": {
                "title": "King George Street",
                "description": "King George Street in Tel Aviv and Jerusalem is named after King George V of the United Kingdom, in recognition of British support for the Balfour Declaration and the establishment of a Jewish homeland.",
                "url": "https://en.wikipedia.org/wiki/King_George_Street_(Tel_Aviv)"
            },
            "allenby": {
                "title": "Allenby Street",
                "description": "Named after Field Marshal Edmund Allenby who led the British forces that captured Palestine from the Ottoman Empire in 1917-1918. The street was one of Tel Aviv's first major commercial thoroughfares.",
                "url": "https://en.wikipedia.org/wiki/Allenby_Street"
            },
            "bialik": {
                "title": "Hayim Nahman Bialik",
                "description": "Bialik (1873-1934) was a Jewish poet who wrote in Hebrew and is considered Israel's national poet. His home in Tel Aviv is now a museum on Bialik Street.",
                "url": "https://en.wikipedia.org/wiki/Hayim_Nahman_Bialik"
            },
            "weizmann": {
                "title": "Chaim Weizmann",
                "description": "Chaim Weizmann (1874-1952) was a Zionist leader and scientist who became the first President of Israel. He played a key role in obtaining the Balfour Declaration.",
                "url": "https://en.wikipedia.org/wiki/Chaim_Weizmann"
            },
        }

        street_lower = street.lower()
        for key, info in known_streets.items():
            if key in street_lower:
                return self._create_result(
                    junction=junction,
                    title=info["title"],
                    description=info["description"],
                    url=info["url"],
                    relevance_score=random.uniform(85, 95),
                    quality_score=random.uniform(88, 95),
                    confidence=random.uniform(90, 98),
                )

        # Generic fallback
        return self._create_result(
            junction=junction,
            title=f"About {street}",
            description=f"Historical information about {street}. Search Wikipedia for more details about this location and its significance.",
            url=f"https://en.wikipedia.org/wiki/Special:Search?search={street.replace(' ', '+')}+Israel",
            relevance_score=random.uniform(50, 70),
            quality_score=random.uniform(50, 65),
            confidence=random.uniform(40, 60),
        )


class JudgeAgent(BaseAgent):
    """
    Agent that evaluates contestant results and picks a winner.

    Receives results from Video, Music, and History agents
    and determines which provides the best recommendation.
    """

    def __init__(self):
        super().__init__(AgentType.JUDGE, "Judge")

    def process(self, junction: Junction) -> AgentResult:
        """Not used directly - use evaluate() instead."""
        raise NotImplementedError("JudgeAgent uses evaluate(), not process()")

    def evaluate(
        self,
        junction: Junction,
        contestants: List[AgentResult]
    ) -> JudgeDecision:
        """
        Evaluate contestant results and determine a winner.

        Args:
            junction: The junction being judged
            contestants: List of AgentResults from Video, Music, History agents

        Returns:
            JudgeDecision with the winner and reasoning
        """
        start_time = time.time()

        if not contestants:
            raise ValueError("No contestants to evaluate")

        # Filter out failed results
        valid_contestants = [c for c in contestants if c.is_success]

        if not valid_contestants:
            # All failed - pick first as "winner" with error note
            return JudgeDecision(
                junction_id=junction.junction_id,
                junction_address=junction.address,
                winner=contestants[0],
                winner_type=contestants[0].agent_type,
                winning_score=0,
                contestants=contestants,
                reasoning="All agents failed to produce valid results.",
                decision_time_ms=(time.time() - start_time) * 1000,
            )

        # Calculate judge scores for each contestant
        judge_scores = {}
        for contestant in valid_contestants:
            # Weight the scores
            relevance_weight = 0.45
            quality_weight = 0.30
            confidence_weight = 0.15
            freshness_weight = 0.10  # Bonus for faster processing

            # Calculate weighted score
            score = (
                contestant.relevance_score * relevance_weight +
                contestant.quality_score * quality_weight +
                contestant.confidence * confidence_weight
            )

            # Add freshness bonus (faster = better)
            max_time = 500  # ms
            freshness_bonus = max(0, (max_time - contestant.processing_time_ms) / max_time * 10)
            score += freshness_bonus * freshness_weight

            judge_scores[contestant.agent_type.value] = score

        # Find winner
        winner = max(valid_contestants, key=lambda c: judge_scores[c.agent_type.value])
        winning_score = judge_scores[winner.agent_type.value]

        # Generate reasoning
        reasoning = self._generate_reasoning(winner, valid_contestants, judge_scores)

        return JudgeDecision(
            junction_id=junction.junction_id,
            junction_address=junction.address,
            winner=winner,
            winner_type=winner.agent_type,
            winning_score=winning_score,
            contestants=contestants,
            reasoning=reasoning,
            judge_scores=judge_scores,
            decision_time_ms=(time.time() - start_time) * 1000,
        )

    def _generate_reasoning(
        self,
        winner: AgentResult,
        contestants: List[AgentResult],
        scores: dict
    ) -> str:
        """Generate explanation for the decision."""
        winner_type = winner.agent_type.value.title()
        winner_score = scores[winner.agent_type.value]

        # Find runners up
        others = [c for c in contestants if c != winner]
        if others:
            runner_up = max(others, key=lambda c: scores[c.agent_type.value])
            margin = winner_score - scores[runner_up.agent_type.value]

            if margin > 10:
                return (f"{winner_type} wins decisively with a score of {winner_score:.1f}. "
                       f"'{winner.title}' offers the best combination of relevance and quality.")
            else:
                return (f"{winner_type} narrowly wins with {winner_score:.1f} points. "
                       f"'{winner.title}' edges out the competition by {margin:.1f} points.")

        return f"{winner_type} wins by default with {winner_score:.1f} points."
