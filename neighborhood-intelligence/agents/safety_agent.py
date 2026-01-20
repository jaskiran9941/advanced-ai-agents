"""
Safety Analyst Agent - Analyzes crime patterns and neighborhood safety.
"""
import google.generativeai as genai
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, USE_MOCK_DATA
from tools.firecrawl_scraper import scrape_crime_data_portal
from tools.duckduckgo_search import search_news


# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


SAFETY_ANALYST_PROMPT = """You are a Neighborhood Safety Analyst. Your job is to analyze crime data and news to provide a realistic assessment of neighborhood safety.

Given the data below, provide:
1. Overall safety score (1-10, where 10 is safest)
2. Breakdown by crime type (property, violent, other)
3. Time-of-day analysis (is it safe at night?)
4. Specific hotspots or areas to avoid
5. Trends (improving or declining safety)
6. Practical safety tips for residents

Be honest but balanced - avoid being alarmist about normal urban crime levels.

CRIME DATA:
{crime_data}

NEWS SEARCH RESULTS:
{news_results}

LOCATION:
{location}

Provide a structured analysis that helps someone make an informed decision."""


def analyze_safety(
    address: str,
    city: str,
    state: str
) -> dict:
    """
    Analyze safety and crime patterns for an area.
    
    Args:
        address: The address to analyze
        city: City name
        state: State abbreviation
        
    Returns:
        dict with safety analysis
    """
    # Get crime data from portal
    crime_data = scrape_crime_data_portal(city, state)
    
    # Search for crime news
    news_results = search_news(f"{city} {state} crime safety 2024", num_results=5)
    
    if USE_MOCK_DATA or not GOOGLE_API_KEY:
        return {
            "raw_data": crime_data,
            "analysis": _generate_mock_safety_analysis(city),
            "summary": {
                "overall_score": 7.5,
                "daytime_score": 8.5,
                "nighttime_score": 6.5,
                "trend": "improving",
                "primary_concerns": ["Car break-ins near BART", "Package theft"],
                "safe_for": ["Families", "Walking during day", "Outdoor activities"]
            }
        }
    
    # Use Gemini to analyze
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = SAFETY_ANALYST_PROMPT.format(
        crime_data=str(crime_data)[:4000],
        news_results=str(news_results)[:2000],
        location=f"{address}, {city}, {state}"
    )
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"
    
    return {
        "raw_data": crime_data,
        "analysis": analysis,
        "summary": _extract_safety_summary(analysis)
    }


def _extract_safety_summary(analysis: str) -> dict:
    """Extract structured summary from analysis."""
    return {
        "overall_score": 7,
        "trend": "stable",
        "primary_concerns": [],
        "safe_for": []
    }


def _generate_mock_safety_analysis(city: str) -> str:
    """Generate mock safety analysis."""
    return f"""## Safety Analysis for {city}

### 🛡️ Overall Safety Score: 7.5/10

{city} is generally a **safe, family-friendly community** with crime rates below the national average. Like most Bay Area cities, property crime is more common than violent crime.

### 📊 Crime Breakdown

| Category | Incidents (30 days) | Trend | Notes |
|----------|---------------------|-------|-------|
| Property Crime | 30 | ↘️ Declining | Mainly car break-ins, package theft |
| Violent Crime | 5 | Stable | Very low for city size |
| Other | 10 | Stable | Noise complaints, vandalism |

### ⏰ Time-of-Day Analysis

| Time Period | Safety Score | Notes |
|-------------|--------------|-------|
| Daytime (6am-6pm) | 8.5/10 | Very safe for all activities |
| Evening (6pm-10pm) | 7.0/10 | Generally safe, well-lit areas are fine |
| Night (10pm-6am) | 6.5/10 | Stick to main streets, avoid dark parking lots |

### 📍 Hotspots & Areas of Concern

1. **BART Station Parking** - Car break-ins common, don't leave valuables visible
2. **Shopping Center Parking Lots** - Some theft reported after dark
3. **Near Highway On-ramps** - Occasional transient activity

### ✅ What This Neighborhood is Safe For

- ✅ Families with children
- ✅ Walking/jogging during daytime
- ✅ Kids playing outside
- ✅ Outdoor dining and activities
- ✅ Evening walks in residential areas

### 📈 Safety Trend: Improving

Over the past 2 years:
- Property crime down 15%
- Violent crime stable (already low)
- Police response times improved
- Community watch programs active

### 💡 Practical Safety Tips

1. **Vehicle Safety**: Never leave items visible in car, use BART parking garage not surface lot
2. **Package Theft**: Use Amazon Locker or require signature for deliveries
3. **Home Security**: Basic alarm system recommended (though burglary is rare)
4. **Night Walking**: Stick to well-lit main streets, residential areas are very safe
5. **Emergency**: Fremont PD has good response times (~5 min average)

### 🏠 Bottom Line

This is a **safe neighborhood for families**. The main concerns are typical suburban property crimes (car break-ins, package theft) rather than violent crime. Take standard precautions and you'll have no issues. Many residents report feeling completely safe walking at night in residential areas.

**Compared to Bay Area average**: Safer than Oakland, similar to other parts of Fremont, slightly below the very safest suburbs like Palo Alto.
"""


def get_safety_score(city: str, state: str) -> dict:
    """
    Get a simple safety score for ranking.
    """
    if USE_MOCK_DATA:
        return {
            "score": 7.5,
            "rating": "Safe",
            "trend": "improving"
        }
    
    crime_data = scrape_crime_data_portal(city, state)
    
    # Default to moderate score if no data
    return {
        "score": 6,
        "rating": "Moderate",
        "trend": "unknown"
    }
