"""
Configuration settings for Neighborhood Intelligence Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY", "")

# Feature flags
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

# Cache settings
CACHE_TTL_HOURS = 24  # How long to cache API responses
CACHE_DB_PATH = "data/cache.db"

# Google Maps settings
DEFAULT_DEPARTURE_TIME = "08:00"  # For rush hour simulation
COMMUTE_DAYS = ["monday", "friday"]  # Days to check for traffic patterns

# Search settings
NEWS_SEARCH_RESULTS = 10
NEARBY_SEARCH_RADIUS_METERS = 1609  # 1 mile

# Place types for lifestyle scoring
LIFESTYLE_PLACE_TYPES = {
    "gym": ["gym", "fitness_center"],
    "grocery": ["grocery_or_supermarket", "supermarket"],
    "temple": ["hindu_temple", "place_of_worship"],
    "park": ["park"],
    "coffee": ["cafe"],
    "restaurant": ["restaurant"],
    "school": ["school", "primary_school", "secondary_school"],
}
