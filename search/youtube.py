"""YouTube trailer search functionality."""

import re
import requests
from typing import Optional

from utils.colors import print_colored, Colors


def search_youtube(query: str, verbose: bool = False) -> Optional[str]:
    """Search YouTube for a trailer and return the first result URL"""
    try:
        search_url = f"https://www.youtube.com/results?search_query={query}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        # Use regex to find video IDs
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)

        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
        else:
            if verbose:
                print_colored(f"  ⚠️  No video IDs found for query: {query}", Colors.YELLOW)
            return None
    except requests.RequestException as e:
        if verbose:
            print_colored(f"  ❌ Error searching for '{query}': {e}", Colors.RED)
    return None
