"""
Commute Analyst Agent - Calculates rush-hour and off-peak commute times.
"""
import google.generativeai as genai
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, USE_MOCK_DATA
from tools.google_maps import get_rush_hour_commute, get_commute_time, geocode_address


# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


COMMUTE_ANALYST_PROMPT = """You are a Commute Analyst expert. Your job is to analyze commute data and provide actionable insights.

Given the commute data below, provide a clear analysis including:
1. A realistic assessment of the daily commute experience
2. Best and worst case scenarios
3. Transit alternatives if available
4. Recommendations for flexible work arrangements

Be specific with numbers and practical advice.

COMMUTE DATA:
{commute_data}

USER'S WORK SCHEDULE:
{work_schedule}

Provide your analysis in a structured format with clear sections."""


def analyze_commute(
    home_address: str,
    work_address: str,
    work_schedule: str = "Standard 9am-5pm, Monday-Friday"
) -> dict:
    """
    Analyze commute between home and work.
    
    Args:
        home_address: Home address
        work_address: Work address
        work_schedule: Description of work schedule
        
    Returns:
        dict with commute analysis
    """
    # Get raw commute data
    commute_data = get_rush_hour_commute(home_address, work_address)
    
    # If using mock data or no API key, return structured mock response
    if USE_MOCK_DATA or not GOOGLE_API_KEY:
        return {
            "raw_data": commute_data,
            "analysis": _generate_mock_analysis(commute_data),
            "summary": {
                "rush_hour_driving": commute_data.get("scenarios", {}).get("monday_morning", {}).get("duration_in_traffic_text", "38 min"),
                "off_peak_driving": commute_data.get("scenarios", {}).get("monday_morning", {}).get("duration_text", "22 min"),
                "transit": commute_data.get("scenarios", {}).get("transit", {}).get("duration_text", "1h 15min"),
                "recommendation": "Consider flexible hours to avoid peak traffic"
            }
        }
    
    # Use Gemini to analyze
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = COMMUTE_ANALYST_PROMPT.format(
        commute_data=str(commute_data),
        work_schedule=work_schedule
    )
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"
    
    # Extract key metrics
    monday = commute_data.get("scenarios", {}).get("monday_morning", {})
    friday = commute_data.get("scenarios", {}).get("friday_evening", {})
    transit = commute_data.get("scenarios", {}).get("transit", {})
    
    return {
        "raw_data": commute_data,
        "analysis": analysis,
        "summary": {
            "rush_hour_driving": monday.get("duration_in_traffic_text", monday.get("duration_text", "N/A")),
            "off_peak_driving": monday.get("duration_text", "N/A"),
            "friday_evening": friday.get("duration_in_traffic_text", friday.get("duration_text", "N/A")),
            "transit": transit.get("duration_text", "N/A"),
        }
    }


def _generate_mock_analysis(commute_data: dict) -> str:
    """Generate a mock analysis when not using real LLM."""
    return """## Commute Analysis

### Daily Commute Reality
Your typical morning commute during rush hour (8am departure) will take approximately **38 minutes**, though this can vary significantly based on traffic conditions. On lighter traffic days, you might see times as low as 22 minutes.

### Peak vs Off-Peak
- **Monday Morning (8am)**: 35-45 minutes - Heaviest traffic of the week
- **Friday Evening (5pm)**: 40-55 minutes - Weekend exodus adds congestion
- **Off-Peak (10am-3pm)**: 20-25 minutes - Relatively smooth

### Transit Alternative
Public transit takes approximately 1 hour 15 minutes, which is longer but allows for productive time (reading, emails, etc). Consider this option 1-2 days per week to reduce driving fatigue.

### Recommendations
1. **Flexible Start Time**: Leaving at 7:30am instead of 8am could save 10-15 minutes daily
2. **Hybrid Work**: If possible, work from home on Fridays to avoid worst traffic
3. **Alternative Routes**: Have 2-3 backup routes for accident days
"""


def get_commute_score(home_address: str, work_address: str) -> dict:
    """
    Get a simple commute score for ranking purposes.
    
    Returns a score from 1-10 where:
    - 10 = Less than 15 min commute
    - 7-9 = 15-30 min commute
    - 4-6 = 30-45 min commute
    - 1-3 = 45+ min commute
    """
    commute = get_commute_time(home_address, work_address)
    
    if "error" in commute:
        return {"score": 0, "error": commute["error"]}
    
    # Use traffic duration if available, otherwise regular duration
    duration_sec = commute.get("duration_in_traffic_seconds", commute.get("duration_seconds", 3600))
    duration_min = duration_sec / 60
    
    if duration_min < 15:
        score = 10
    elif duration_min < 20:
        score = 9
    elif duration_min < 25:
        score = 8
    elif duration_min < 30:
        score = 7
    elif duration_min < 35:
        score = 6
    elif duration_min < 40:
        score = 5
    elif duration_min < 45:
        score = 4
    elif duration_min < 50:
        score = 3
    elif duration_min < 60:
        score = 2
    else:
        score = 1
    
    return {
        "score": score,
        "duration_minutes": round(duration_min),
        "rating": ["Terrible", "Very Long", "Long", "Below Average", 
                   "Average", "Above Average", "Good", "Very Good", 
                   "Excellent", "Outstanding", "Perfect"][score]
    }
