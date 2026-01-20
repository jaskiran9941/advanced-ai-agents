"""
Google Places API wrapper for finding nearby amenities.
"""
import googlemaps
from typing import List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_MAPS_API_KEY, USE_MOCK_DATA, LIFESTYLE_PLACE_TYPES, NEARBY_SEARCH_RADIUS_METERS
from tools.cache import get_cached, set_cached


def get_client() -> googlemaps.Client:
    """Get a Google Maps API client."""
    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY not set in environment")
    return googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


def find_nearby_places(
    location: tuple,  # (lat, lng)
    place_type: str,
    radius_meters: int = NEARBY_SEARCH_RADIUS_METERS,
    keyword: Optional[str] = None
) -> List[dict]:
    """
    Find places near a location.
    
    Args:
        location: (lat, lng) tuple
        place_type: Google Places type (e.g., "gym", "restaurant")
        radius_meters: Search radius in meters
        keyword: Optional keyword to filter results
        
    Returns:
        List of places with name, address, rating, distance
    """
    cache_key = f"places:{location}:{place_type}:{radius_meters}:{keyword}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_PLACES_DATA
        return MOCK_PLACES_DATA.get(place_type, [])
    
    client = get_client()
    
    try:
        results = client.places_nearby(
            location=location,
            radius=radius_meters,
            type=place_type,
            keyword=keyword
        )
        
        places = []
        for place in results.get("results", [])[:10]:  # Limit to 10 results
            place_info = {
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating"),
                "user_ratings_total": place.get("user_ratings_total", 0),
                "place_id": place.get("place_id"),
                "location": place.get("geometry", {}).get("location"),
                "types": place.get("types", []),
                "open_now": place.get("opening_hours", {}).get("open_now"),
            }
            places.append(place_info)
        
        # Cache for 24 hours
        set_cached(cache_key, places, ttl_hours=24)
        
        return places
        
    except Exception as e:
        return [{"error": str(e)}]


def get_place_details(place_id: str) -> dict:
    """
    Get detailed information about a specific place.
    
    Args:
        place_id: Google Place ID
        
    Returns:
        dict with detailed place information
    """
    cache_key = f"place_details:{place_id}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        return {"name": "Mock Place", "rating": 4.5}
    
    client = get_client()
    
    try:
        result = client.place(
            place_id=place_id,
            fields=[
                "name", "formatted_address", "formatted_phone_number",
                "opening_hours", "rating", "reviews", "website", "url"
            ]
        )
        
        place = result.get("result", {})
        response = {
            "name": place.get("name"),
            "address": place.get("formatted_address"),
            "phone": place.get("formatted_phone_number"),
            "website": place.get("website"),
            "google_maps_url": place.get("url"),
            "rating": place.get("rating"),
            "opening_hours": place.get("opening_hours", {}).get("weekday_text"),
            "reviews": [
                {
                    "rating": r.get("rating"),
                    "text": r.get("text", "")[:200],  # Truncate long reviews
                    "time": r.get("relative_time_description")
                }
                for r in place.get("reviews", [])[:3]  # Top 3 reviews
            ]
        }
        
        # Cache for 7 days
        set_cached(cache_key, response, ttl_hours=168)
        
        return response
        
    except Exception as e:
        return {"error": str(e)}


def analyze_lifestyle_amenities(location: tuple, preferences: List[str]) -> dict:
    """
    Analyze all lifestyle amenities for a location based on user preferences.
    
    Args:
        location: (lat, lng) tuple
        preferences: List of amenity types user cares about (e.g., ["gym", "temple", "park"])
        
    Returns:
        dict with counts and nearest places for each preference
    """
    results = {
        "location": location,
        "preferences": preferences,
        "amenities": {},
        "overall_score": 0
    }
    
    scores = []
    
    for pref in preferences:
        # Get the Google Place types for this preference
        place_types = LIFESTYLE_PLACE_TYPES.get(pref, [pref])
        
        all_places = []
        for place_type in place_types:
            places = find_nearby_places(location, place_type)
            all_places.extend(places)
        
        # Remove duplicates by place_id
        seen = set()
        unique_places = []
        for p in all_places:
            if p.get("place_id") and p["place_id"] not in seen:
                seen.add(p["place_id"])
                unique_places.append(p)
        
        # Sort by rating (highest first)
        unique_places.sort(key=lambda x: x.get("rating") or 0, reverse=True)
        
        results["amenities"][pref] = {
            "count": len(unique_places),
            "top_places": unique_places[:3],  # Top 3 by rating
        }
        
        # Score: 0 places = 0, 1-2 = 5, 3-5 = 7, 6+ = 10
        count = len(unique_places)
        if count == 0:
            score = 0
        elif count <= 2:
            score = 5
        elif count <= 5:
            score = 7
        else:
            score = 10
        
        results["amenities"][pref]["score"] = score
        scores.append(score)
    
    # Overall score is average of all preference scores
    if scores:
        results["overall_score"] = round(sum(scores) / len(scores), 1)
    
    return results
