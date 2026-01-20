"""
DuckDuckGo search wrapper for free news and web search.
"""
from duckduckgo_search import DDGS
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import USE_MOCK_DATA, NEWS_SEARCH_RESULTS
from tools.cache import get_cached, set_cached


def search_news(
    query: str,
    num_results: int = NEWS_SEARCH_RESULTS,
    region: str = "us-en",
    time_range: Optional[str] = "m"  # d=day, w=week, m=month, y=year
) -> List[dict]:
    """
    Search for news articles using DuckDuckGo.
    
    Args:
        query: Search query
        num_results: Number of results to return
        region: Region code (e.g., "us-en")
        time_range: Time filter (d=day, w=week, m=month, y=year)
        
    Returns:
        List of news articles with title, body, url, date
    """
    cache_key = f"news:{query}:{num_results}:{time_range}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_NEWS_DATA
        return MOCK_NEWS_DATA
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(
                query,
                region=region,
                max_results=num_results,
                timelimit=time_range
            ))
        
        articles = []
        for r in results:
            articles.append({
                "title": r.get("title"),
                "body": r.get("body"),
                "url": r.get("url"),
                "source": r.get("source"),
                "date": r.get("date"),
                "image": r.get("image")
            })
        
        # Cache for 6 hours (news changes frequently)
        set_cached(cache_key, articles, ttl_hours=6)
        
        return articles
        
    except Exception as e:
        return [{"error": str(e)}]


def search_web(
    query: str,
    num_results: int = 10,
    region: str = "us-en"
) -> List[dict]:
    """
    General web search using DuckDuckGo.
    
    Args:
        query: Search query
        num_results: Number of results to return
        region: Region code
        
    Returns:
        List of web results with title, body, url
    """
    cache_key = f"web:{query}:{num_results}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_WEB_SEARCH_DATA
        return MOCK_WEB_SEARCH_DATA
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query,
                region=region,
                max_results=num_results
            ))
        
        web_results = []
        for r in results:
            web_results.append({
                "title": r.get("title"),
                "body": r.get("body"),
                "url": r.get("href")
            })
        
        # Cache for 24 hours
        set_cached(cache_key, web_results, ttl_hours=24)
        
        return web_results
        
    except Exception as e:
        return [{"error": str(e)}]


def search_local_news(location: str, topics: List[str] = None) -> List[dict]:
    """
    Search for local news relevant to a specific location.
    
    Args:
        location: City or neighborhood name
        topics: Optional list of topics to search for
        
    Returns:
        Combined list of news articles for the location
    """
    default_topics = ["development", "construction", "crime", "schools", "traffic"]
    topics = topics or default_topics
    
    all_articles = []
    seen_urls = set()
    
    for topic in topics:
        query = f"{location} {topic} news"
        articles = search_news(query, num_results=5)
        
        for article in articles:
            url = article.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                article["topic"] = topic
                all_articles.append(article)
    
    return all_articles


def search_city_planning(city: str, state: str) -> List[dict]:
    """
    Search for city planning and development news.
    
    Args:
        city: City name
        state: State abbreviation
        
    Returns:
        List of planning-related search results
    """
    queries = [
        f"{city} {state} city planning commission",
        f"{city} {state} new development approved",
        f"{city} {state} zoning changes",
        f"{city} {state} construction permits"
    ]
    
    all_results = []
    seen_urls = set()
    
    for query in queries:
        results = search_web(query, num_results=5)
        for r in results:
            url = r.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(r)
    
    return all_results
