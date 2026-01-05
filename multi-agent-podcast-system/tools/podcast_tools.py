"""
Podcast Tools

Real podcast data fetching from iTunes API and RSS feeds.
Migrated from agentic-podcast-summarizer/app_real.py
"""

import requests
import feedparser
from datetime import datetime, timedelta
from time import mktime
from typing import List, Dict, Optional


def search_itunes_api(topics: List[str], limit: int = 5, country: str = "US") -> Dict:
    """
    Search iTunes/Apple Podcasts API for podcasts.

    Migrated from app_real.py lines 219-260.

    Args:
        topics: List of search topics (e.g., ["AI", "machine learning"])
        limit: Maximum number of results
        country: Country code (default: "US")

    Returns:
        {
            "success": bool,
            "recommendations": List[Dict],  # Podcast metadata
            "count": int,
            "source": "iTunes API",
            "error": str (if failed)
        }
    """
    search_query = " ".join(topics)

    try:
        response = requests.get(
            "https://itunes.apple.com/search",
            params={
                "term": search_query,
                "media": "podcast",
                "limit": limit,
                "country": country
            },
            timeout=10
        )

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"iTunes API error: {response.status_code}"
            }

        results = response.json().get("results", [])

        podcasts = []
        for r in results:
            if r.get("feedUrl"):  # Only include if has RSS feed
                podcasts.append({
                    "podcast_id": str(r.get("collectionId")),
                    "name": r.get("collectionName", "Unknown"),
                    "rss_url": r.get("feedUrl"),
                    "artist": r.get("artistName", "Unknown"),
                    "description": r.get("description", "No description"),
                    "artwork": r.get("artworkUrl600", ""),
                    "genres": r.get("genres", [])
                })

        return {
            "success": True,
            "recommendations": podcasts,
            "count": len(podcasts),
            "source": "iTunes API"
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"iTunes API request failed: {str(e)}"
        }


def fetch_episodes_from_rss(subscriptions: List[Dict], hours_back: int = 24,
                            max_episodes_per_feed: int = 10) -> Dict:
    """
    Fetch recent episodes from RSS feeds.

    Migrated from app_real.py lines 262-312.

    Args:
        subscriptions: List of {name, rss_url, tags}
        hours_back: How many hours back to check
        max_episodes_per_feed: Max episodes to check per feed

    Returns:
        {
            "success": bool,
            "episodes": List[Dict],  # Episode data
            "count": int,
            "source": "RSS Feeds",
            "time_range": str,
            "errors": List[str]  # Any parsing errors
        }
    """
    cutoff_time = datetime.now() - timedelta(hours=hours_back)
    all_episodes = []
    errors = []

    for subscription in subscriptions:
        try:
            feed = feedparser.parse(subscription["rss_url"])

            if feed.bozo:
                errors.append(f"Error parsing {subscription['name']}")
                continue

            for entry in feed.entries[:max_episodes_per_feed]:
                # Parse publish date
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime.fromtimestamp(mktime(entry.published_parsed))
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime.fromtimestamp(mktime(entry.updated_parsed))

                # Check if recent enough
                if pub_date and pub_date > cutoff_time:
                    episode = {
                        "episode_id": f"ep_{subscription['name']}_{entry.get('id', entry.get('link', ''))}".replace(" ", "_")[:100],
                        "title": entry.get("title", "Untitled"),
                        "description": entry.get("summary", "No description"),
                        "podcast": subscription["name"],
                        "published": pub_date.strftime("%Y-%m-%d %H:%M"),
                        "audio_url": entry.enclosures[0].href if hasattr(entry, "enclosures") and entry.enclosures else None,
                        "link": entry.get("link", ""),
                        "tags": subscription.get("tags", []),
                        "duration": entry.get("itunes_duration", "Unknown")
                    }
                    all_episodes.append(episode)

        except Exception as e:
            errors.append(f"Error fetching {subscription.get('name', 'unknown')}: {str(e)}")
            continue

    return {
        "success": True,
        "episodes": all_episodes,
        "count": len(all_episodes),
        "source": "RSS Feeds",
        "time_range": f"Last {hours_back} hours",
        "errors": errors if errors else None
    }


def get_podcast_metadata(rss_url: str) -> Optional[Dict]:
    """
    Get podcast metadata from RSS feed.

    Args:
        rss_url: RSS feed URL

    Returns:
        {
            "name": str,
            "description": str,
            "author": str,
            "image_url": str,
            "categories": List[str],
            "episode_count": int
        }
        or None if parsing fails
    """
    try:
        feed = feedparser.parse(rss_url)

        if feed.bozo:
            return None

        feed_data = feed.feed

        return {
            "name": feed_data.get("title", "Unknown"),
            "description": feed_data.get("subtitle", feed_data.get("description", "")),
            "author": feed_data.get("author", feed_data.get("itunes_author", "Unknown")),
            "image_url": feed_data.get("image", {}).get("href", ""),
            "categories": [cat.get("term", "") for cat in feed_data.get("tags", [])],
            "episode_count": len(feed.entries),
            "language": feed_data.get("language", "Unknown"),
            "last_updated": feed_data.get("updated", "")
        }

    except Exception:
        return None


# Utility functions

def validate_rss_url(url: str) -> bool:
    """
    Check if a URL is a valid RSS feed.

    Args:
        url: URL to validate

    Returns:
        True if valid RSS feed, False otherwise
    """
    try:
        feed = feedparser.parse(url)
        return not feed.bozo and len(feed.entries) > 0
    except Exception:
        return False


def extract_episode_topics(description: str, max_topics: int = 5) -> List[str]:
    """
    Extract potential topics from episode description (simple keyword extraction).

    Args:
        description: Episode description text
        max_topics: Maximum number of topics to return

    Returns:
        List of topic keywords
    """
    # Common podcast topic keywords
    topic_keywords = [
        "AI", "machine learning", "deep learning", "data science",
        "technology", "startup", "business", "productivity",
        "health", "fitness", "psychology", "neuroscience",
        "climate", "energy", "politics", "economics"
    ]

    description_lower = description.lower()
    found_topics = []

    for keyword in topic_keywords:
        if keyword.lower() in description_lower:
            found_topics.append(keyword)
            if len(found_topics) >= max_topics:
                break

    return found_topics
