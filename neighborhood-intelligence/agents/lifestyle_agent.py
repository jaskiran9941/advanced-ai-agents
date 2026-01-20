"""
Lifestyle Scout Agent - Analyzes walkability and nearby amenities.
"""
import google.generativeai as genai
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, USE_MOCK_DATA
from tools.google_places import analyze_lifestyle_amenities, find_nearby_places
from tools.google_maps import geocode_address


# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


LIFESTYLE_SCOUT_PROMPT = """You are a Lifestyle Scout expert. Your job is to analyze neighborhood amenities and how well they match a person's lifestyle preferences.

Given the amenity data below and the user's lifestyle preferences, provide:
1. An overall lifestyle fit score (1-10)
2. Analysis of each preference category
3. Notable highlights (what's great about this location)
4. Gaps or concerns (what might be missing or inconvenient)
5. Practical daily life scenarios (e.g., "Your morning coffee run...")

Be specific with names, distances, and ratings.

AMENITY DATA:
{amenity_data}

USER'S LIFESTYLE PREFERENCES:
{preferences}

Provide your analysis in a conversational but structured format."""


def analyze_lifestyle(
    address: str,
    preferences: list
) -> dict:
    """
    Analyze lifestyle amenities for an address based on user preferences.
    
    Args:
        address: The address to analyze
        preferences: List of lifestyle preferences (e.g., ["gym", "temple", "park"])
        
    Returns:
        dict with lifestyle analysis
    """
    # Geocode the address first
    location_data = geocode_address(address)
    
    if not location_data or "error" in location_data:
        return {
            "error": f"Could not geocode address: {address}",
            "preferences": preferences
        }
    
    location = (location_data["lat"], location_data["lng"])
    
    # Get amenity data
    amenity_data = analyze_lifestyle_amenities(location, preferences)
    
    # Generate analysis
    if USE_MOCK_DATA or not GOOGLE_API_KEY:
        return {
            "raw_data": amenity_data,
            "analysis": _generate_mock_lifestyle_analysis(amenity_data, preferences),
            "summary": {
                "overall_score": amenity_data.get("overall_score", 7.5),
                "highlights": _get_highlights(amenity_data),
                "concerns": _get_concerns(amenity_data, preferences)
            }
        }
    
    # Use Gemini to analyze
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = LIFESTYLE_SCOUT_PROMPT.format(
        amenity_data=str(amenity_data),
        preferences=", ".join(preferences)
    )
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"
    
    return {
        "raw_data": amenity_data,
        "analysis": analysis,
        "summary": {
            "overall_score": amenity_data.get("overall_score", 0),
            "highlights": _get_highlights(amenity_data),
            "concerns": _get_concerns(amenity_data, preferences)
        }
    }


def _get_highlights(amenity_data: dict) -> list:
    """Extract highlights from amenity data."""
    highlights = []
    
    for pref, data in amenity_data.get("amenities", {}).items():
        if data.get("score", 0) >= 7:
            count = data.get("count", 0)
            top = data.get("top_places", [])
            if top:
                best = top[0]
                highlights.append(f"{pref.title()}: {count} options nearby, best rated: {best.get('name')} ({best.get('rating')}★)")
            else:
                highlights.append(f"{pref.title()}: {count} options within 1 mile")
    
    return highlights


def _get_concerns(amenity_data: dict, preferences: list) -> list:
    """Identify gaps or concerns in amenities."""
    concerns = []
    
    for pref, data in amenity_data.get("amenities", {}).items():
        if data.get("score", 0) <= 4:
            count = data.get("count", 0)
            if count == 0:
                concerns.append(f"No {pref} found within 1 mile")
            else:
                concerns.append(f"Limited {pref} options ({count}) nearby")
    
    return concerns


def _generate_mock_lifestyle_analysis(amenity_data: dict, preferences: list) -> str:
    """Generate a mock lifestyle analysis."""
    score = amenity_data.get("overall_score", 7.5)
    
    return f"""## Lifestyle Fit Analysis

### Overall Score: {score}/10

Your lifestyle preferences are **well-matched** to this neighborhood! Here's the breakdown:

### Preference Analysis

#### 🏋️ Gym/Fitness
Great news! There are multiple fitness options nearby:
- **24 Hour Fitness** (0.8 mi) - 4.2★ - Full gym with classes
- **Planet Fitness** (1.1 mi) - 4.0★ - Budget-friendly option

#### 🛕 Temple
Excellent temple proximity:
- **Fremont Hindu Temple** (0.8 mi) - 4.8★ - One of the largest in the Bay Area

#### 🌳 Parks
Abundant green space:
- **Central Park** (0.5 mi) - 4.6★ - Great for morning walks and kids
- **Lake Elizabeth** (0.9 mi) - 4.5★ - Beautiful lake setting

### Daily Life Scenarios
- **Morning routine**: 10-minute walk to Central Park for a jog, grab coffee at Philz on the way back
- **Weekend**: Easy walk to the temple for morning prayers, then picnic at Lake Elizabeth
- **Evenings**: Quick drive to 24 Hour Fitness for a workout

### What's Great
- Strong Indian community with great grocery stores (Patel Brothers nearby)
- Multiple high-rated parks within walking distance
- Temple is easily accessible for regular visits

### Watch Out For
- Limited walkability to some amenities (car helpful)
- Coffee shops are good but not exceptional
"""


def get_lifestyle_score(address: str, preferences: list) -> dict:
    """
    Get a simple lifestyle score for ranking purposes.
    """
    location_data = geocode_address(address)
    
    if not location_data or "error" in location_data:
        return {"score": 0, "error": "Could not geocode address"}
    
    location = (location_data["lat"], location_data["lng"])
    amenity_data = analyze_lifestyle_amenities(location, preferences)
    
    return {
        "score": amenity_data.get("overall_score", 0),
        "amenities": amenity_data.get("amenities", {}),
        "rating": _score_to_rating(amenity_data.get("overall_score", 0))
    }


def _score_to_rating(score: float) -> str:
    """Convert numeric score to text rating."""
    if score >= 9:
        return "Excellent"
    elif score >= 7:
        return "Very Good"
    elif score >= 5:
        return "Good"
    elif score >= 3:
        return "Fair"
    else:
        return "Poor"
