"""
Google Maps API wrapper for commute calculations.
"""
import googlemaps
from datetime import datetime, timedelta
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_MAPS_API_KEY, USE_MOCK_DATA
from tools.cache import get_cached, set_cached


def get_client() -> googlemaps.Client:
    """Get a Google Maps API client."""
    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("GOOGLE_MAPS_API_KEY not set in environment")
    return googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


def get_next_weekday_datetime(weekday: int, hour: int = 8, minute: int = 0) -> datetime:
    """
    Get the next occurrence of a weekday at a specific time.
    
    Args:
        weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
        hour: Hour of day (24h format)
        minute: Minute
        
    Returns:
        datetime of the next occurrence
    """
    today = datetime.now()
    days_ahead = weekday - today.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    next_date = today + timedelta(days=days_ahead)
    return next_date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def get_commute_time(
    origin: str,
    destination: str,
    departure_time: Optional[datetime] = None,
    mode: str = "driving"
) -> dict:
    """
    Calculate commute time between two addresses.
    
    Args:
        origin: Starting address
        destination: Destination address
        departure_time: When to depart (for traffic prediction)
        mode: "driving", "transit", "bicycling", or "walking"
        
    Returns:
        dict with duration, distance, and traffic info
    """
    # Check cache first
    cache_key = f"commute:{origin}:{destination}:{mode}:{departure_time}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    # Use mock data if enabled
    if USE_MOCK_DATA:
        from data.mock_data import MOCK_COMMUTE_DATA
        return MOCK_COMMUTE_DATA
    
    client = get_client()
    
    try:
        # Get directions with traffic info
        result = client.directions(
            origin=origin,
            destination=destination,
            mode=mode,
            departure_time=departure_time or datetime.now(),
            alternatives=False,
            traffic_model="best_guess" if mode == "driving" else None
        )
        
        if not result:
            return {"error": "No route found"}
        
        leg = result[0]["legs"][0]
        
        response = {
            "origin": leg["start_address"],
            "destination": leg["end_address"],
            "distance_text": leg["distance"]["text"],
            "distance_meters": leg["distance"]["value"],
            "duration_text": leg["duration"]["text"],
            "duration_seconds": leg["duration"]["value"],
            "mode": mode,
        }
        
        # Add traffic duration if available (driving only)
        if "duration_in_traffic" in leg:
            response["duration_in_traffic_text"] = leg["duration_in_traffic"]["text"]
            response["duration_in_traffic_seconds"] = leg["duration_in_traffic"]["value"]
        
        # Cache for 6 hours (traffic changes)
        set_cached(cache_key, response, ttl_hours=6)
        
        return response
        
    except Exception as e:
        return {"error": str(e)}


def get_rush_hour_commute(origin: str, destination: str) -> dict:
    """
    Get commute times for typical rush hour scenarios.
    
    Returns commute times for:
    - Monday 8am (typical start of week)
    - Friday 5pm (typical end of week)
    - Off-peak (current time or midday estimate)
    """
    results = {
        "origin": origin,
        "destination": destination,
        "scenarios": {}
    }
    
    # Monday 8am rush hour
    monday_8am = get_next_weekday_datetime(0, 8, 0)
    results["scenarios"]["monday_morning"] = get_commute_time(
        origin, destination, monday_8am, "driving"
    )
    
    # Friday 5pm rush hour
    friday_5pm = get_next_weekday_datetime(4, 17, 0)
    results["scenarios"]["friday_evening"] = get_commute_time(
        origin, destination, friday_5pm, "driving"
    )
    
    # Transit option (no traffic consideration needed)
    results["scenarios"]["transit"] = get_commute_time(
        origin, destination, None, "transit"
    )
    
    return results


def geocode_address(address: str) -> Optional[dict]:
    """
    Convert an address to lat/lng coordinates.
    
    Args:
        address: Street address or location name
        
    Returns:
        dict with lat, lng, and formatted_address
    """
    cache_key = f"geocode:{address}"
    cached = get_cached(cache_key)
    if cached:
        return cached
    
    if USE_MOCK_DATA:
        return {
            "lat": 37.5485,
            "lng": -121.9886,
            "formatted_address": address
        }
    
    client = get_client()
    
    try:
        result = client.geocode(address)
        if not result:
            return None
        
        location = result[0]["geometry"]["location"]
        response = {
            "lat": location["lat"],
            "lng": location["lng"],
            "formatted_address": result[0]["formatted_address"]
        }
        
        # Cache geocoding results for 30 days
        set_cached(cache_key, response, ttl_hours=720)
        
        return response
        
    except Exception as e:
        return {"error": str(e)}
