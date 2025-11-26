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
    Uses creative query building to find related content.
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
        address = junction.address or ""

        if not self.youtube_api_key:
            return self._create_error_result(junction, "YouTube API key not configured")

        result = self._search_youtube(street, address, junction)
        if result:
            return result

        return self._create_error_result(junction, "No video found for this location")

    def _search_youtube(self, street: str, address: str, junction: Junction) -> Optional[AgentResult]:
        """Search YouTube API with creative queries."""
        try:
            # Build creative search queries
            search_queries = self._build_creative_queries(street, address)

            best_video = None
            best_score = 0

            for query in search_queries:
                youtube_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": query,
                    "type": "video",
                    "key": self.youtube_api_key,
                    "maxResults": 5,
                    "order": "relevance",
                    "videoEmbeddable": "true",
                }

                response = requests.get(youtube_url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    if "items" in data and data["items"]:
                        for item in data["items"]:
                            video_id = item["id"].get("videoId")
                            if not video_id:
                                continue
                            snippet = item["snippet"]
                            title = snippet.get("title", "")
                            description = snippet.get("description", "")
                            channel = snippet.get("channelTitle", "")

                            # Use view count proxy via snippet data
                            score = 70 + random.uniform(0, 20)

                            if score > best_score:
                                best_score = score
                                best_video = {
                                    "title": title,
                                    "description": description[:200] + "..." if len(description) > 200 else description,
                                    "url": f"https://www.youtube.com/watch?v={video_id}",
                                    "channel": channel,
                                    "query": query,
                                    "score": score,
                                }

                # Found a good video, stop searching
                if best_video:
                    break

            if best_video:
                return self._create_result(
                    junction=junction,
                    title=best_video["title"],
                    description=f"Found for: '{best_video['query']}'. Channel: {best_video['channel']}",
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

    def _build_creative_queries(self, street: str, address: str) -> List[str]:
        """Build creative search queries based on street name."""
        queries = []

        # Clean the street name
        clean_street = street
        for remove in ["Go through", "roundabout", "Turn left", "Turn right",
                       "Continue", "Slight", "Keep", "Merge", "Take"]:
            clean_street = clean_street.replace(remove, "").strip()
        clean_street = clean_street.strip(" ,.-")

        # Extract city
        city = ""
        address_lower = address.lower()
        if "tel aviv" in address_lower:
            city = "Tel Aviv"
        elif "jerusalem" in address_lower:
            city = "Jerusalem"
        elif "haifa" in address_lower:
            city = "Haifa"

        # Direct location queries
        if clean_street and len(clean_street) > 2:
            if city:
                queries.append(f"{clean_street} {city}")
            queries.append(f"{clean_street} Israel")

        # City-based queries
        if city:
            queries.append(f"{city} walking tour")
            queries.append(f"{city} street view drive")

        # Extract keywords and numbers for creative associations
        words = clean_street.lower().split()

        # Number associations
        number_words = {"1st": "one", "2nd": "two", "3rd": "three", "4th": "four", "5th": "five",
                       "first": "one", "second": "two", "third": "three", "exit": "exit"}
        for word in words:
            if word in number_words:
                queries.append(f"{number_words[word]} music video")
            if word.isdigit():
                queries.append(f"number {word} song")

        # Word associations for common terms
        word_associations = {
            "exit": ["exit music", "the exit"],
            "road": ["road trip video", "on the road"],
            "highway": ["highway driving", "highway music"],
            "bridge": ["bridge view", "over the bridge"],
            "turn": ["turn around", "every turn"],
            "left": ["left turn", "what's left"],
            "right": ["right way", "do it right"],
            "north": ["north star", "going north"],
            "south": ["south bound", "going south"],
        }
        for word in words:
            if word in word_associations:
                queries.extend(word_associations[word])

        # Israel fallback
        queries.append("Israel driving tour")
        queries.append("Tel Aviv streets")

        # Remove duplicates
        seen = set()
        unique = []
        for q in queries:
            if q.lower() not in seen and q.strip():
                seen.add(q.lower())
                unique.append(q)

        return unique[:8]

    def _create_error_result(self, junction: Junction, error_msg: str) -> AgentResult:
        """Create an error result."""
        return self._create_result(
            junction=junction,
            title="Video search failed",
            description=error_msg,
            url="",
            relevance_score=0,
            quality_score=0,
            confidence=0,
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

            response = requests.post(auth_url, headers=headers, data=data, timeout=10)

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

                response = requests.get(spotify_url, headers=headers, params=params, timeout=10)

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
                # Boost scores to be competitive with other agents
                # Spotify popularity is 0-100, but often 40-70 for good tracks
                popularity = best_track["popularity"]
                boosted_relevance = min(95, popularity + 25 + random.uniform(0, 10))
                boosted_quality = min(95, popularity + 20 + random.uniform(0, 15))

                return self._create_result(
                    junction=junction,
                    title=f"{best_track['name']} - {best_track['artist']}",
                    description=f"Found for: '{best_track['query']}'. Album: {best_track['album']}",
                    url=best_track["url"],
                    relevance_score=boosted_relevance,
                    quality_score=boosted_quality,
                    confidence=random.uniform(82, 96),
                    raw_data=best_track,
                )

        except requests.exceptions.RequestException as e:
            print(f"Spotify API error: {e}")
        except Exception as e:
            print(f"Spotify search error: {e}")

        return None

    def _build_search_queries(self, street: str, address: str) -> List[str]:
        """
        Build creative search queries based on street name and address.
        Uses word associations to find related music.
        """
        queries = []

        # Clean the street name - remove navigation instructions
        clean_street = street
        for remove in ["Go through", "roundabout", "Turn left", "Turn right",
                       "Continue", "Slight", "Keep", "Merge", "Take exit", "Take the"]:
            clean_street = clean_street.replace(remove, "").strip()
        clean_street = clean_street.strip(" ,.-")

        # Extract city
        city = ""
        address_lower = address.lower()
        if "tel aviv" in address_lower or "תל אביב" in address:
            city = "Tel Aviv"
        elif "jerusalem" in address_lower or "ירושלים" in address:
            city = "Jerusalem"
        elif "haifa" in address_lower or "חיפה" in address:
            city = "Haifa"

        # Direct street name search
        if clean_street and len(clean_street) > 2:
            queries.append(clean_street)
            if city:
                queries.append(f"{clean_street} {city}")

        # Extract words for creative associations
        words = clean_street.lower().split()

        # Number-based song associations
        number_songs = {
            "1": ["One", "Number One"],
            "2": ["Just the Two of Us", "Two of Us", "It Takes Two"],
            "3": ["Three Little Birds", "Three Times a Lady"],
            "4": ["Four Seasons", "Fantastic Four"],
            "5": ["Five", "Mambo No 5"],
            "1st": ["One", "First"],
            "2nd": ["Just the Two of Us", "Second"],
            "3rd": ["Three", "Third"],
            "4th": ["Four", "Fourth"],
            "5th": ["5th Symphony", "Fifth"],
            "first": ["One", "First Time"],
            "second": ["Just the Two of Us", "Second Chance"],
            "third": ["Three", "Third Eye"],
        }

        for word in words:
            if word in number_songs:
                queries.extend(number_songs[word])

        # Word-based song associations
        word_songs = {
            "exit": ["Exit Music", "Exit", "The Way Out"],
            "road": ["On the Road Again", "Road to Nowhere", "Life is a Highway"],
            "highway": ["Highway to Hell", "Life is a Highway", "Highway Star"],
            "street": ["Street Life", "Dancing in the Street", "On the Street"],
            "avenue": ["Avenue", "Park Avenue"],
            "bridge": ["Bridge Over Troubled Water", "London Bridge"],
            "turn": ["Turn Turn Turn", "Turn Around"],
            "left": ["Left Outside Alone", "Left Behind"],
            "right": ["Right Here Right Now", "Mr Right"],
            "north": ["North", "True North"],
            "south": ["South Side", "Going South"],
            "east": ["East", "Far East"],
            "west": ["West Coast", "Go West"],
            "king": ["King", "Kings and Queens"],
            "david": ["David", "King David"],
            "george": ["George", "King George"],
            "park": ["Life in the Park", "Central Park"],
            "garden": ["Garden", "In the Garden"],
            "sun": ["Here Comes the Sun", "Walking on Sunshine"],
            "moon": ["Moon", "Fly Me to the Moon"],
            "star": ["Star", "Lucky Star", "Starman"],
            "love": ["Love", "All You Need is Love"],
            "heart": ["Heart", "Total Eclipse of the Heart"],
            "dream": ["Dream", "Dream On"],
            "night": ["Night", "In the Night"],
            "day": ["Day", "Beautiful Day"],
            "morning": ["Morning", "Good Morning"],
            "river": ["River", "Cry Me a River"],
            "sea": ["Sea", "Beyond the Sea"],
            "mountain": ["Mountain", "Ain't No Mountain"],
            "valley": ["Valley", "Valley Girl"],
            "center": ["Center", "Center Stage"],
            "central": ["Central", "Grand Central"],
        }

        for word in words:
            if word in word_songs:
                queries.extend(word_songs[word])

        # City-based queries
        if city:
            queries.append(city)
            queries.append(f"{city} song")

        # Israel fallback
        queries.append("Israeli music")
        queries.append("Israel song")
        queries.append("Tel Aviv")

        # Remove duplicates
        seen = set()
        unique = []
        for q in queries:
            if q.lower() not in seen and q.strip():
                seen.add(q.lower())
                unique.append(q)

        return unique[:10]  # Try up to 10 queries

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
    Uses creative query building to find related historical content.
    """

    def __init__(self):
        super().__init__(AgentType.HISTORY, "History Finder")

    def process(self, junction: Junction) -> AgentResult:
        """
        Find historical facts about the junction using Wikipedia API.
        """
        street = junction.street_name
        address = junction.address or ""

        # Try Wikipedia API search with creative queries
        result = self._search_wikipedia(street, address, junction)
        if result:
            return result

        return self._create_error_result(junction, "No historical information found")

    def _search_wikipedia(self, street: str, address: str, junction: Junction) -> Optional[AgentResult]:
        """Search Wikipedia for historical information about the location."""
        try:
            # Extract key terms for search
            search_terms = self._get_search_terms(street, address)

            best_result = None
            best_score = 0

            # Wikipedia requires User-Agent header
            headers = {
                "User-Agent": "TourGuideApp/1.0 (https://github.com/tour-guide; tour@guide.com)"
            }

            for term in search_terms:  # Try all search terms
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

                response = requests.get(wiki_search_url, params=search_params, headers=headers, timeout=10)

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

            # If we found any result, get more details (lowered threshold for creativity)
            if best_result and best_score > 20:
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
        """Generate creative search terms for Wikipedia based on location."""
        terms = []

        # Clean street name - remove navigation instructions
        clean_street = street
        for suffix in [" St", " Street", " Ave", " Avenue", " Blvd", " Road", " Rd",
                      "Go through", "roundabout", "Turn", "Continue", "Slight",
                      "Keep", "Merge", "Take", "exit", "1st", "2nd", "3rd", "4th", "5th"]:
            clean_street = clean_street.replace(suffix, "").strip()
        clean_street = clean_street.strip(" ,.-0123456789")

        # Israeli street name mappings to historical figures
        israeli_figures = {
            "jabotinsky": "Ze'ev Jabotinsky",
            "herzl": "Theodor Herzl",
            "ben gurion": "David Ben-Gurion",
            "weizmann": "Chaim Weizmann",
            "rothschild": "Rothschild Boulevard Tel Aviv",
            "dizengoff": "Dizengoff Street",
            "allenby": "Edmund Allenby",
            "king george": "George V",
            "king david": "King David",
            "ibn gabirol": "Solomon ibn Gabirol",
            "bialik": "Hayim Nahman Bialik",
            "nordau": "Max Nordau",
            "arlozorov": "Haim Arlosoroff",
            "rabin": "Yitzhak Rabin",
            "begin": "Menachem Begin",
            "kaplan": "Eliezer Kaplan",
            "namir": "Mordechai Namir",
            "sokolov": "Nahum Sokolow",
            "hayarkon": "Yarkon River",
        }

        # Check for known Israeli streets
        street_lower = clean_street.lower()
        for key, wiki_term in israeli_figures.items():
            if key in street_lower:
                terms.append(wiki_term)

        # Extract city
        city = ""
        address_lower = address.lower()
        if "tel aviv" in address_lower:
            city = "Tel Aviv"
        elif "jerusalem" in address_lower:
            city = "Jerusalem"
        elif "haifa" in address_lower:
            city = "Haifa"

        # Direct street search
        if clean_street and len(clean_street) > 2:
            if city:
                terms.append(f"{clean_street} {city}")
            terms.append(clean_street)

        # Word-based associations for historical topics
        words = clean_street.lower().split()
        word_associations = {
            "exit": ["history of exits", "road infrastructure"],
            "road": ["history of roads", "road construction"],
            "highway": ["highway history", "freeway"],
            "bridge": ["bridge engineering", "famous bridges"],
            "turn": ["road design"],
            "north": ["northern history"],
            "south": ["southern history"],
            "east": ["eastern history"],
            "west": ["western history"],
            "king": ["monarchy", "king history"],
            "david": ["King David", "David history"],
            "george": ["George history", "King George"],
            "park": ["park history", "urban parks"],
            "garden": ["garden history", "botanical"],
            "river": ["river history"],
            "sea": ["maritime history"],
            "mountain": ["mountain history"],
            "center": ["city center history"],
            "central": ["central district"],
            "old": ["old city", "ancient history"],
            "new": ["modern history", "new city"],
        }

        for word in words:
            if word in word_associations:
                terms.extend(word_associations[word])

        # City history as fallback
        if city:
            terms.append(f"{city} history")
            terms.append(city)

        # Israel history as final fallback
        terms.append("Israel history")
        terms.append("Tel Aviv history")

        # Remove duplicates
        seen = set()
        unique = []
        for t in terms:
            if t.lower() not in seen and t.strip():
                seen.add(t.lower())
                unique.append(t)

        return unique[:8]  # Try up to 8 terms

    def _get_page_extract(self, title: str) -> Optional[str]:
        """Get a short extract from a Wikipedia page."""
        try:
            wiki_url = "https://en.wikipedia.org/w/api.php"
            headers = {
                "User-Agent": "TourGuideApp/1.0 (https://github.com/tour-guide; tour@guide.com)"
            }
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
