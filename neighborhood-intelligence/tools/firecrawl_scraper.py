"""
Firecrawl web scraper for Zillow, city planning, crime data, and GreatSchools.
"""
from firecrawl import FirecrawlApp
from typing import Optional, List
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIRECRAWL_API_KEY, USE_MOCK_DATA
from tools.cache import get_cached, set_cached


def get_client() -> FirecrawlApp:
    """Get a Firecrawl client."""
    if not FIRECRAWL_API_KEY:
        raise ValueError("FIRECRAWL_API_KEY not set in environment")
    return FirecrawlApp(api_key=FIRECRAWL_API_KEY)


def scrape_url(url: str, formats: List[str] = None) -> dict:
    """
    Scrape a URL and return its content.
    
    Args:
        url: URL to scrape
        formats: List of formats to return (e.g., ["markdown", "html"])
        
    Returns:
        dict with scraped content
    """
    cache_key = f"scrape:{url}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        return {"content": "Mock scraped content", "url": url}
    
    client = get_client()
    formats = formats or ["markdown"]
    
    try:
        result = client.scrape_url(url, params={"formats": formats})
        
        response = {
            "url": url,
            "content": result.get("markdown", result.get("html", "")),
            "metadata": result.get("metadata", {})
        }
        
        # Cache for 24 hours
        set_cached(cache_key, response, ttl_hours=24)
        
        return response
        
    except Exception as e:
        return {"error": str(e), "url": url}


def scrape_zillow_listing(address: str) -> dict:
    """
    Scrape Zillow for listing information.
    
    Args:
        address: Property address to search
        
    Returns:
        dict with property details
    """
    cache_key = f"zillow:{address}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_ZILLOW_DATA
        return MOCK_ZILLOW_DATA
    
    # Format address for Zillow URL
    formatted = address.lower().replace(" ", "-").replace(",", "")
    formatted = re.sub(r"[^a-z0-9-]", "", formatted)
    
    # Try to scrape Zillow search results
    search_url = f"https://www.zillow.com/homes/{formatted}_rb/"
    
    result = scrape_url(search_url)
    
    if "error" in result:
        return result
    
    # Parse the content to extract listing info
    content = result.get("content", "")
    
    # Extract basic info using patterns (simplified)
    response = {
        "address": address,
        "raw_content": content[:5000],  # First 5000 chars for analysis
        "source": "zillow",
        "scraped_url": search_url
    }
    
    # Cache for 24 hours
    set_cached(cache_key, response, ttl_hours=24)
    
    return response


def scrape_greatschools(city: str, state: str) -> dict:
    """
    Scrape GreatSchools for school ratings.
    
    Args:
        city: City name
        state: State abbreviation
        
    Returns:
        dict with school information
    """
    cache_key = f"greatschools:{city}:{state}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_SCHOOLS_DATA
        return MOCK_SCHOOLS_DATA
    
    # Format for GreatSchools URL
    city_formatted = city.lower().replace(" ", "-")
    state_lower = state.lower()
    
    url = f"https://www.greatschools.org/{state_lower}/{city_formatted}/schools/"
    
    result = scrape_url(url)
    
    if "error" in result:
        return result
    
    response = {
        "city": city,
        "state": state,
        "raw_content": result.get("content", "")[:8000],
        "source": "greatschools",
        "scraped_url": url
    }
    
    # Cache for 7 days (school ratings don't change often)
    set_cached(cache_key, response, ttl_hours=168)
    
    return response


def scrape_city_planning_portal(city: str, state: str) -> dict:
    """
    Scrape city planning portal for development projects.
    
    Args:
        city: City name
        state: State abbreviation
        
    Returns:
        dict with planning documents/info
    """
    cache_key = f"cityplanning:{city}:{state}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_CITY_PLANNING_DATA
        return MOCK_CITY_PLANNING_DATA
    
    # Common city planning URL patterns
    city_formatted = city.lower().replace(" ", "")
    
    potential_urls = [
        f"https://www.{city_formatted}.gov/planning",
        f"https://{city_formatted}.gov/departments/planning",
        f"https://www.{city_formatted}{state.lower()}.gov/planning"
    ]
    
    # Try each URL
    for url in potential_urls:
        try:
            result = scrape_url(url)
            if "error" not in result:
                response = {
                    "city": city,
                    "state": state,
                    "raw_content": result.get("content", "")[:8000],
                    "source": "city_portal",
                    "scraped_url": url
                }
                set_cached(cache_key, response, ttl_hours=48)
                return response
        except:
            continue
    
    return {
        "city": city,
        "state": state,
        "error": "Could not find city planning portal",
        "attempted_urls": potential_urls
    }


def scrape_crime_data_portal(city: str, state: str) -> dict:
    """
    Scrape city open data portal for crime statistics.
    
    Args:
        city: City name
        state: State abbreviation
        
    Returns:
        dict with crime data
    """
    cache_key = f"crime:{city}:{state}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_CRIME_DATA
        return MOCK_CRIME_DATA
    
    # Common open data portal patterns
    city_lower = city.lower().replace(" ", "")
    
    potential_urls = [
        f"https://data.{city_lower}.gov/browse?tags=crime",
        f"https://data.{city_lower}ca.gov/browse?tags=crime",  # California pattern
        f"https://{city_lower}.data.socrata.com/browse?tags=crime"
    ]
    
    for url in potential_urls:
        try:
            result = scrape_url(url)
            if "error" not in result:
                response = {
                    "city": city,
                    "state": state,
                    "raw_content": result.get("content", "")[:8000],
                    "source": "open_data_portal",
                    "scraped_url": url
                }
                set_cached(cache_key, response, ttl_hours=24)
                return response
        except:
            continue
    
    # Fallback: try CrimeMapping or SpotCrime
    spotcrime_url = "https://www.spotcrime.com/"
    result = scrape_url(spotcrime_url)
    
    return {
        "city": city,
        "state": state,
        "raw_content": result.get("content", "")[:5000] if "error" not in result else "",
        "source": "spotcrime",
        "note": "Could not find city-specific data portal, using general crime data"
    }
