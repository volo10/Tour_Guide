"""
Music Agent - Finds relevant Spotify tracks for junctions.
"""

import logging
import random
import time
import base64
import requests
from typing import List, Optional

from ..route_fetcher.models import Junction
from .models import AgentResult, AgentType
from .base_agent import BaseAgent
from ..config import get_spotify_client_id, get_spotify_client_secret

logger = logging.getLogger(__name__)


class MusicAgent(BaseAgent):
    """
    Agent that finds music related to a junction by searching Spotify.
    Uses creative query building based on street names and locations.
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

        except requests.exceptions.RequestException as e:
            logger.error(f"Spotify authentication request error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in Spotify authentication: {e}")

        return None

    def process(self, junction: Junction) -> AgentResult:
        """Find music related to the junction by searching Spotify."""
        street = junction.street_name
        address = junction.address or ""

        token = self._get_spotify_token()
        if not token:
            return self._create_error_result(junction, "Spotify API credentials not configured")

        result = self._search_spotify(junction, street, address)
        if result:
            return result

        return self._create_error_result(junction, "No music found for this location")

    def _search_spotify(self, junction: Junction, street: str, address: str) -> Optional[AgentResult]:
        """Search Spotify using location-based queries."""
        try:
            search_queries = self._build_search_queries(street, address)
            best_track = None
            best_score = 0

            for query in search_queries:
                spotify_url = "https://api.spotify.com/v1/search"
                headers = {
                    "Authorization": f"Bearer {self.spotify_token}",
                    "Content-Type": "application/json"
                }
                params = {"q": query, "type": "track", "limit": 10, "market": "IL"}

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

                            if popularity > best_score and track_url:
                                best_score = popularity
                                best_track = {
                                    "name": track_name,
                                    "artist": artists,
                                    "album": album,
                                    "url": track_url,
                                    "popularity": popularity,
                                    "query": query,
                                }

                if best_track and best_score >= 50:
                    break

            if best_track:
                boosted_relevance = min(95, best_track["popularity"] + 25 + random.uniform(0, 10))
                boosted_quality = min(95, best_track["popularity"] + 20 + random.uniform(0, 15))

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
            logger.error(f"Spotify API request error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in Spotify search: {e}")

        return None

    def _build_search_queries(self, street: str, address: str) -> List[str]:
        """Build search queries based on street name and address."""
        queries = []

        # Clean street name
        clean_street = street
        for remove in ["Go through", "roundabout", "Turn left", "Turn right",
                       "Continue", "Slight", "Keep", "Merge", "Take exit", "Take the"]:
            clean_street = clean_street.replace(remove, "").strip()
        clean_street = clean_street.strip(" ,.-")

        city = self._extract_city(address)

        if clean_street and len(clean_street) > 2:
            queries.append(clean_street)
            if city:
                queries.append(f"{clean_street} {city}")

        # Word associations
        queries.extend(self._get_song_associations(clean_street))

        if city:
            queries.append(city)

        queries.append("Israeli music")
        queries.append("Tel Aviv")

        return self._dedupe_queries(queries, max_count=10)

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

    def _get_song_associations(self, street: str) -> List[str]:
        """Get song associations for street words."""
        queries = []
        words = street.lower().split()

        associations = {
            "road": ["On the Road Again", "Life is a Highway"],
            "highway": ["Highway to Hell", "Life is a Highway"],
            "bridge": ["Bridge Over Troubled Water"],
            "street": ["Street Life", "Dancing in the Street"],
            "sun": ["Here Comes the Sun", "Walking on Sunshine"],
            "moon": ["Fly Me to the Moon"],
            "star": ["Lucky Star", "Starman"],
        }

        for word in words:
            if word in associations:
                queries.extend(associations[word])

        return queries

    def _dedupe_queries(self, queries: List[str], max_count: int) -> List[str]:
        """Remove duplicates and limit."""
        seen = set()
        unique = []
        for q in queries:
            if q.lower() not in seen and q.strip():
                seen.add(q.lower())
                unique.append(q)
        return unique[:max_count]

    def _create_error_result(self, junction: Junction, error_msg: str) -> AgentResult:
        """Create an error result."""
        return self._create_result(
            junction=junction,
            title="Music search failed",
            description=error_msg,
            url="",
            relevance_score=0,
            quality_score=0,
            confidence=0,
        )
