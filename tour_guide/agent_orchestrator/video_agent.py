"""
Video Agent - Finds relevant YouTube videos for junctions.
"""

import logging
import random
import requests
from typing import List, Optional

from ..route_fetcher.models import Junction
from .models import AgentResult, AgentType
from .base_agent import BaseAgent
from ..config import get_youtube_api_key

logger = logging.getLogger(__name__)

# Scoring constants
BASE_VIDEO_SCORE = 70
VIDEO_SCORE_VARIANCE = 20


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
        """Find a relevant video for the junction using YouTube API."""
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

                            score = BASE_VIDEO_SCORE + random.uniform(0, VIDEO_SCORE_VARIANCE)

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
            logger.error(f"YouTube API request error: {e}")
        except (KeyError, ValueError) as e:
            logger.error(f"YouTube API response parsing error: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in YouTube search: {e}")

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
        city = self._extract_city(address)

        # Direct location queries
        if clean_street and len(clean_street) > 2:
            if city:
                queries.append(f"{clean_street} {city}")
            queries.append(f"{clean_street} Israel")

        # City-based queries
        if city:
            queries.append(f"{city} walking tour")
            queries.append(f"{city} street view drive")

        # Word associations
        queries.extend(self._get_word_associations(clean_street))

        # Fallback
        queries.append("Israel driving tour")
        queries.append("Tel Aviv streets")

        return self._dedupe_queries(queries, max_count=8)

    def _extract_city(self, address: str) -> str:
        """Extract city from address string."""
        address_lower = address.lower()
        if "tel aviv" in address_lower:
            return "Tel Aviv"
        elif "jerusalem" in address_lower:
            return "Jerusalem"
        elif "haifa" in address_lower:
            return "Haifa"
        return ""

    def _get_word_associations(self, street: str) -> List[str]:
        """Get word-based query associations."""
        queries = []
        words = street.lower().split()

        word_associations = {
            "exit": ["exit music", "the exit"],
            "road": ["road trip video", "on the road"],
            "highway": ["highway driving", "highway music"],
            "bridge": ["bridge view", "over the bridge"],
        }

        for word in words:
            if word in word_associations:
                queries.extend(word_associations[word])

        return queries

    def _dedupe_queries(self, queries: List[str], max_count: int) -> List[str]:
        """Remove duplicate queries and limit count."""
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
            title="Video search failed",
            description=error_msg,
            url="",
            relevance_score=0,
            quality_score=0,
            confidence=0,
        )
