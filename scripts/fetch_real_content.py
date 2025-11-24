#!/usr/bin/env python3
"""
Tour Guide Real Content Fetcher
Fetches actual YouTube videos and Spotify songs for each junction
"""

import os
import json
import requests
import base64
from datetime import datetime
from typing import Dict, List, Tuple

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

class TourGuideFetcher:
    """Fetches real YouTube videos and Spotify songs for tour junctions"""

    def __init__(self, youtube_api_key: str, spotify_client_id: str, spotify_client_secret: str):
        """
        Initialize with API credentials

        Args:
            youtube_api_key: YouTube Data API v3 key
            spotify_client_id: Spotify Client ID
            spotify_client_secret: Spotify Client Secret
        """
        self.youtube_api_key = youtube_api_key
        self.spotify_client_id = spotify_client_id
        self.spotify_client_secret = spotify_client_secret
        self.spotify_token = None

        # Authenticate with Spotify
        self._authenticate_spotify()

    def _authenticate_spotify(self):
        """Get Spotify access token using Client Credentials flow"""
        auth_url = "https://accounts.spotify.com/api/token"

        # Encode credentials
        credentials = f"{self.spotify_client_id}:{self.spotify_client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        data = {"grant_type": "client_credentials"}

        try:
            response = requests.post(auth_url, headers=headers, data=data)
            response.raise_for_status()
            self.spotify_token = response.json()['access_token']
            print(f"{Colors.GREEN}✓ Spotify authenticated successfully{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}✗ Spotify authentication failed: {e}{Colors.END}")
            raise

    def search_youtube_video(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search YouTube for videos

        Args:
            query: Search query string
            max_results: Number of results to return

        Returns:
            List of video results with titles, URLs, and details
        """
        youtube_url = "https://www.googleapis.com/youtube/v3/search"

        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "key": self.youtube_api_key,
            "maxResults": max_results,
            "order": "relevance",
            "videoEmbeddable": "true"
        }

        try:
            response = requests.get(youtube_url, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            if 'items' in data:
                for item in data['items']:
                    video_id = item['id'].get('videoId')
                    title = item['snippet'].get('title')
                    channel = item['snippet'].get('channelTitle')
                    thumbnail = item['snippet'].get('thumbnails', {}).get('default', {}).get('url')

                    results.append({
                        'title': title,
                        'video_id': video_id,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'channel': channel,
                        'thumbnail': thumbnail
                    })

            return results
        except Exception as e:
            print(f"{Colors.RED}✗ YouTube search failed for '{query}': {e}{Colors.END}")
            return []

    def search_spotify_track(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search Spotify for tracks

        Args:
            query: Search query string
            max_results: Number of results to return

        Returns:
            List of track results with names, artists, and URLs
        """
        spotify_url = "https://api.spotify.com/v1/search"

        headers = {
            "Authorization": f"Bearer {self.spotify_token}",
            "Content-Type": "application/json"
        }

        params = {
            "q": query,
            "type": "track",
            "limit": max_results
        }

        try:
            response = requests.get(spotify_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            results = []
            if 'tracks' in data and 'items' in data['tracks']:
                for track in data['tracks']['items']:
                    artists = ", ".join([artist['name'] for artist in track['artists']])

                    results.append({
                        'name': track['name'],
                        'artist': artists,
                        'url': track['external_urls']['spotify'],
                        'duration_ms': track['duration_ms'],
                        'popularity': track['popularity'],
                        'preview_url': track.get('preview_url'),
                        'album': track['album']['name']
                    })

            return results
        except Exception as e:
            print(f"{Colors.RED}✗ Spotify search failed for '{query}': {e}{Colors.END}")
            return []

    def fetch_junction_content(self, junction_name: str, search_terms: Dict) -> Dict:
        """
        Fetch content for a single junction

        Args:
            junction_name: Name of the junction
            search_terms: Dict with 'video', 'music', 'history' keys

        Returns:
            Dict with video and music results for this junction
        """
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}📍 JUNCTION: {junction_name}{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")

        # Search YouTube
        print(f"\n{Colors.BLUE}🎬 Searching YouTube for: {search_terms['video']}{Colors.END}")
        videos = self.search_youtube_video(search_terms['video'], max_results=3)

        # Search Spotify
        print(f"{Colors.BLUE}🎵 Searching Spotify for: {search_terms['music']}{Colors.END}")
        songs = self.search_spotify_track(search_terms['music'], max_results=3)

        return {
            'junction': junction_name,
            'videos': videos,
            'songs': songs,
            'timestamp': datetime.now().isoformat()
        }

def main():
    """Main execution"""

    # Get API credentials from environment variables
    youtube_api_key = os.getenv('YOUTUBE_API_KEY')
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    if not all([youtube_api_key, spotify_client_id, spotify_client_secret]):
        print(f"{Colors.RED}✗ Missing API credentials!{Colors.END}")
        print("\n{Colors.YELLOW}Please set environment variables:{Colors.END}")
        print("  export YOUTUBE_API_KEY='your_key'")
        print("  export SPOTIFY_CLIENT_ID='your_id'")
        print("  export SPOTIFY_CLIENT_SECRET='your_secret'")
        print("\nOr create ~/.tour_guide_env with these variables")
        return

    # Initialize fetcher
    print(f"{Colors.HEADER}{Colors.BOLD}🚗 Tour Guide Real Content Fetcher{Colors.END}")
    print(f"{Colors.HEADER}Ramat Hasharon → Tel Aviv Route{Colors.END}\n")

    fetcher = TourGuideFetcher(youtube_api_key, spotify_client_id, spotify_client_secret)

    # Define junctions with search terms
    junctions = [
        {
            'name': 'JUNCTION 1: Hasadot → Highway 5',
            'video': 'כביש 5 Highway 5 רמת השרון תל אביב',
            'music': 'Israeli music driving נסיעה'
        },
        {
            'name': 'JUNCTION 2: Highway 5 → Azrieli Complex',
            'video': 'מגדלי עזריאלי Azrieli Towers תל אביב',
            'music': 'Tel Aviv תל אביב Israeli pop'
        },
        {
            'name': 'JUNCTION 3: Azrieli → Menachem Begin',
            'video': 'מנחם בגין Menachem Begin תל אביב',
            'music': 'Israeli electronic music תל אביב'
        },
        {
            'name': 'JUNCTION 4: Menachem Begin → Ibn Gabirol',
            'video': 'אבן גבירול Ibn Gabirol תל אביב',
            'music': 'Israeli modern music אביב'
        },
        {
            'name': 'JUNCTION 5: Ibn Gabirol → King George',
            'video': 'קינג ג\'ורג\' King George תל אביב',
            'music': 'Israeli classic songs ישראלי'
        },
        {
            'name': 'JUNCTION 6: King George → Yitzhak Gratsiani',
            'video': 'יצחק גרציאני Gratsiani תל אביב',
            'music': 'Israeli music Tel Aviv ישראל'
        }
    ]

    # Fetch content for each junction
    results = []
    for junction in junctions:
        result = fetcher.fetch_junction_content(
            junction['name'],
            {
                'video': junction['video'],
                'music': junction['music']
            }
        )
        results.append(result)

        # Display results
        if result['videos']:
            print(f"\n{Colors.GREEN}✓ Top YouTube Videos:{Colors.END}")
            for i, video in enumerate(result['videos'][:2], 1):
                print(f"  {i}. {Colors.BOLD}{video['title']}{Colors.END}")
                print(f"     Channel: {video['channel']}")
                print(f"     URL: {Colors.CYAN}{video['url']}{Colors.END}")

        if result['songs']:
            print(f"\n{Colors.GREEN}✓ Top Spotify Tracks:{Colors.END}")
            for i, song in enumerate(result['songs'][:2], 1):
                print(f"  {i}. {Colors.BOLD}{song['name']}{Colors.END}")
                print(f"     Artist: {song['artist']}")
                print(f"     Popularity: {song['popularity']}/100")
                print(f"     URL: {Colors.CYAN}{song['url']}{Colors.END}")

    # Save results to file
    output_file = 'tour_guide_real_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Complete route results saved to: {output_file}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}Tour Guide Real Content Fetching Complete!{Colors.END}\n")

if __name__ == "__main__":
    main()
