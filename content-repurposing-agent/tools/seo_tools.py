"""
SEO research tools using SerpAPI.

✅ REAL MULTI-AGENT VALUE: LLMs don't have real-time keyword data
"""
import requests
from typing import Dict, List, Any, Optional
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("seo_tools")

def search_trending_keywords(topic: str, location: str = "United States") -> Dict[str, Any]:
    """
    Search for trending keywords related to a topic using Google Trends via SerpAPI.

    Args:
        topic: Topic to research
        location: Geographic location for trends

    Returns:
        Dictionary with trending keywords and search volumes
    """
    if not settings.seo.serpapi_api_key:
        logger.warning("SerpAPI key not configured, returning mock data")
        return _mock_trending_keywords(topic)

    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_trends",
            "q": topic,
            "data_type": "TIMESERIES",
            "api_key": settings.seo.serpapi_api_key,
            "geo": location
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Retrieved trending data for topic: {topic}")

        return {
            "topic": topic,
            "trending_keywords": _extract_keywords(data),
            "search_interest": data.get("interest_over_time", {}).get("timeline_data", [])
        }

    except Exception as e:
        logger.error(f"SerpAPI request failed: {str(e)}")
        return _mock_trending_keywords(topic)

def get_related_queries(topic: str) -> List[str]:
    """
    Get related search queries for a topic.

    Args:
        topic: Topic to research

    Returns:
        List of related queries
    """
    if not settings.seo.serpapi_api_key:
        logger.warning("SerpAPI key not configured, returning mock data")
        return _mock_related_queries(topic)

    try:
        url = "https://serpapi.com/search"
        params = {
            "engine": "google",
            "q": topic,
            "api_key": settings.seo.serpapi_api_key,
            "num": 10
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        related = data.get("related_searches", [])

        queries = [item.get("query", "") for item in related if item.get("query")]
        logger.info(f"Retrieved {len(queries)} related queries for: {topic}")

        return queries

    except Exception as e:
        logger.error(f"SerpAPI request failed: {str(e)}")
        return _mock_related_queries(topic)

def analyze_keyword_difficulty(keywords: List[str]) -> Dict[str, str]:
    """
    Analyze keyword difficulty (simplified version).

    Args:
        keywords: List of keywords to analyze

    Returns:
        Dictionary mapping keywords to difficulty ratings
    """
    # Simplified heuristic: shorter keywords = higher competition
    results = {}
    for keyword in keywords:
        word_count = len(keyword.split())
        if word_count <= 2:
            difficulty = "High"
        elif word_count <= 4:
            difficulty = "Medium"
        else:
            difficulty = "Low"

        results[keyword] = difficulty

    logger.info(f"Analyzed difficulty for {len(keywords)} keywords")
    return results

def _extract_keywords(serp_data: Dict) -> List[str]:
    """Extract keywords from SerpAPI response."""
    keywords = []

    # Extract from related queries
    if "related_queries" in serp_data:
        for query in serp_data["related_queries"]:
            if "query" in query:
                keywords.append(query["query"])

    # Extract from rising queries
    if "rising_queries" in serp_data:
        for query in serp_data["rising_queries"]:
            if "query" in query:
                keywords.append(query["query"])

    return list(set(keywords))  # Remove duplicates

def _mock_trending_keywords(topic: str) -> Dict[str, Any]:
    """Return mock trending keywords for testing without API key."""
    return {
        "topic": topic,
        "trending_keywords": [
            f"{topic} trends 2024",
            f"best {topic} practices",
            f"{topic} guide",
            f"how to {topic}",
            f"{topic} benefits"
        ],
        "search_interest": [
            {"date": "2024-01", "value": 75},
            {"date": "2024-02", "value": 82},
            {"date": "2024-03", "value": 90}
        ]
    }

def _mock_related_queries(topic: str) -> List[str]:
    """Return mock related queries for testing without API key."""
    return [
        f"{topic} explained",
        f"{topic} tutorial",
        f"{topic} examples",
        f"learn {topic}",
        f"{topic} vs alternatives"
    ]
