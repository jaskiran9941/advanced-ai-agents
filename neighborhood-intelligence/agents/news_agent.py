"""
City Planner Agent - Tracks future development and zoning changes.
"""
import google.generativeai as genai
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, USE_MOCK_DATA
from tools.duckduckgo_search import search_city_planning, search_news
from tools.firecrawl_scraper import scrape_city_planning_portal


# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


NEWS_ANALYST_PROMPT = """You are a City Development Analyst. Your job is to analyze news, city planning documents, and development projects to identify what's coming to a neighborhood.

Given the search results and scraped data below, identify:
1. Upcoming construction projects (addresses, types, timelines)
2. Zoning changes that might affect the area
3. Infrastructure improvements (roads, transit, utilities)
4. Commercial developments (new stores, restaurants, offices)
5. Any red flags (landfills, industrial projects, high-rise blocking views)

Categorize each item as POSITIVE, NEUTRAL, or CONCERNING for residents.

SEARCH RESULTS:
{search_results}

CITY PORTAL DATA:
{portal_data}

LOCATION BEING ANALYZED:
{location}

Provide a structured analysis with clear sections."""


def analyze_future_development(
    address: str,
    city: str,
    state: str
) -> dict:
    """
    Analyze future development and zoning changes for an area.
    
    Args:
        address: The specific address being analyzed
        city: City name
        state: State abbreviation
        
    Returns:
        dict with development analysis
    """
    # Search for news and planning info
    search_results = search_city_planning(city, state)
    news_results = search_news(f"{city} {state} new development construction 2025 2026", num_results=10)
    
    # Try to scrape city planning portal
    portal_data = scrape_city_planning_portal(city, state)
    
    # Combine all data
    all_data = {
        "search_results": search_results,
        "news": news_results,
        "portal": portal_data
    }
    
    if USE_MOCK_DATA or not GOOGLE_API_KEY:
        return {
            "raw_data": all_data,
            "analysis": _generate_mock_development_analysis(city),
            "summary": {
                "upcoming_projects": [
                    {"name": "Downtown Mixed-Use Development", "impact": "NEUTRAL", "timeline": "2026-2028"},
                    {"name": "Community Park", "impact": "POSITIVE", "timeline": "2027"}
                ],
                "zoning_alerts": ["Warm Springs rezoning under review"],
                "red_flags": []
            }
        }
    
    # Use Gemini to analyze
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = NEWS_ANALYST_PROMPT.format(
        search_results=str(search_results)[:4000],
        portal_data=str(portal_data)[:4000],
        location=f"{address}, {city}, {state}"
    )
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"
    
    return {
        "raw_data": all_data,
        "analysis": analysis,
        "summary": _extract_development_summary(analysis)
    }


def _extract_development_summary(analysis: str) -> dict:
    """Extract structured summary from analysis text."""
    # Simple extraction - in production, use structured output
    return {
        "upcoming_projects": [],
        "zoning_alerts": [],
        "red_flags": []
    }


def _generate_mock_development_analysis(city: str) -> str:
    """Generate mock development analysis."""
    return f"""## Future Development Analysis for {city}

### 🏗️ Upcoming Construction Projects

#### 1. Downtown Mixed-Use Development (345 Main St)
- **Type**: 120-unit residential + retail
- **Status**: Approved
- **Timeline**: Construction Q1 2026 → Completion Q2 2028
- **Impact**: NEUTRAL
  - Will add more residents and retail options
  - Expect construction noise and traffic during build phase
  - Located 0.5 miles from subject property

#### 2. New Community Park (500 Park Ave)
- **Type**: 5-acre public park with playground and trails
- **Status**: In Planning
- **Timeline**: Expected completion 2027
- **Impact**: POSITIVE ✅
  - Will significantly improve neighborhood recreation options
  - Property values typically increase near new parks

### 📋 Zoning Changes Under Review

#### Warm Springs District Rezoning
- **Current**: R-1 (Single Family)
- **Proposed**: R-2 (Medium Density)
- **Status**: Under City Council Review
- **Implication**: If approved, expect more townhomes and small apartments
- Could increase traffic but also improve walkability to shops

### 🚦 Infrastructure Improvements
- **BART Extension**: Warm Springs station opened 2017, well-established
- **Road Improvements**: Fremont Blvd repaving scheduled 2025
- **Utilities**: No major changes planned

### ⚠️ Potential Concerns
- No significant red flags identified
- Nearest industrial zone is 3+ miles away
- No landfill or power plant projects in planning

### 📊 Development Trend
{city} is seeing **moderate growth** with a focus on:
- Mixed-use infill development
- Public amenities (parks, trails)
- Smart growth principles

This suggests a maturing suburb focused on quality of life rather than rapid expansion.
"""


def get_development_alerts(city: str, state: str, radius_miles: float = 2.0) -> list:
    """
    Get quick alerts about nearby development.
    
    Returns list of development alerts.
    """
    if USE_MOCK_DATA:
        return [
            {"type": "construction", "name": "Mixed-Use Development", "distance": "0.5 mi", "concern": "low"},
            {"type": "park", "name": "New Community Park", "distance": "0.8 mi", "concern": "none (positive)"}
        ]
    
    # Search for recent development news
    news = search_news(f"{city} {state} construction development approved", num_results=5)
    
    alerts = []
    for article in news:
        if "error" not in article:
            alerts.append({
                "type": "news",
                "title": article.get("title", ""),
                "source": article.get("source", ""),
                "date": article.get("date", "")
            })
    
    return alerts
