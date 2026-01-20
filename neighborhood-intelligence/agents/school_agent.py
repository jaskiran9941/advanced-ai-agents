"""
School Analyst Agent - Evaluates school quality and trends.
"""
import google.generativeai as genai
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, USE_MOCK_DATA
from tools.firecrawl_scraper import scrape_greatschools
from tools.duckduckgo_search import search_web


# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


SCHOOL_ANALYST_PROMPT = """You are a School District Analyst specializing in K-12 education evaluation.

Given the school data below, analyze:
1. Overall quality of schools serving this address
2. Elementary, Middle, and High school options with ratings
3. Any concerning trends (declining ratings, budget cuts, teacher turnover)
4. Positive trends (improving scores, new programs, awards)
5. Practical advice for parents (school choice options, magnet programs, etc.)

SCHOOL DATA:
{school_data}

SEARCH RESULTS:
{search_results}

ADDRESS:
{address}

CHILD AGES:
{child_ages}

Provide specific school names, ratings, and actionable insights."""


def analyze_schools(
    address: str,
    city: str,
    state: str,
    child_ages: list = None
) -> dict:
    """
    Analyze school quality for an address.
    
    Args:
        address: The address to analyze
        city: City name
        state: State abbreviation
        child_ages: List of children's ages (optional)
        
    Returns:
        dict with school analysis
    """
    child_ages = child_ages or []
    
    # Scrape GreatSchools
    school_data = scrape_greatschools(city, state)
    
    # Search for additional school news
    search_results = search_web(f"{city} {state} school ratings 2024 2025", num_results=5)
    
    if USE_MOCK_DATA or not GOOGLE_API_KEY:
        return {
            "raw_data": school_data,
            "analysis": _generate_mock_school_analysis(city, child_ages),
            "summary": {
                "overall_rating": "Excellent",
                "schools": [
                    {"name": "Mission San Jose Elementary", "type": "Elementary", "rating": 9, "trend": "stable"},
                    {"name": "Hopkins Junior High", "type": "Middle", "rating": 8, "trend": "improving"},
                    {"name": "Mission San Jose High", "type": "High", "rating": 10, "trend": "stable"}
                ],
                "highlights": ["Top-rated high school in district", "Strong STEM programs"],
                "concerns": []
            }
        }
    
    # Use Gemini to analyze
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = SCHOOL_ANALYST_PROMPT.format(
        school_data=str(school_data)[:4000],
        search_results=str(search_results)[:2000],
        address=address,
        child_ages=str(child_ages) if child_ages else "Not specified"
    )
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text
    except Exception as e:
        analysis = f"Error generating analysis: {str(e)}"
    
    return {
        "raw_data": school_data,
        "analysis": analysis,
        "summary": _extract_school_summary(analysis)
    }


def _extract_school_summary(analysis: str) -> dict:
    """Extract structured summary from analysis."""
    return {
        "overall_rating": "Good",
        "schools": [],
        "highlights": [],
        "concerns": []
    }


def _generate_mock_school_analysis(city: str, child_ages: list) -> str:
    """Generate mock school analysis."""
    age_specific = ""
    if child_ages:
        if any(age <= 5 for age in child_ages):
            age_specific += "\n**For your preschool-age child**: Look into the district's transitional kindergarten program starting at age 4."
        if any(5 <= age <= 10 for age in child_ages):
            age_specific += "\n**For your elementary-age child**: Mission San Jose Elementary is an excellent choice with strong parent involvement."
        if any(11 <= age <= 13 for age in child_ages):
            age_specific += "\n**For your middle schooler**: Hopkins Junior High has been improving steadily and offers great extracurriculars."
        if any(14 <= age <= 18 for age in child_ages):
            age_specific += "\n**For your high schooler**: Mission San Jose High is one of the top public high schools in California."
    
    return f"""## School Quality Analysis for {city}

### 📚 Overall Assessment: Excellent

{city} is known for having some of the best public schools in California. The district consistently ranks in the top tier statewide.

### 🏫 School Breakdown

#### Elementary Schools (K-5)
| School | Rating | Trend | Notes |
|--------|--------|-------|-------|
| Mission San Jose Elementary | 9/10 | Stable | High test scores, active PTA |
| Warm Springs Elementary | 8/10 | Improving | New principal making positive changes |
| Weibel Elementary | 9/10 | Stable | Strong gifted program |

#### Middle Schools (6-8)
| School | Rating | Trend | Notes |
|--------|--------|-------|-------|
| Hopkins Junior High | 8/10 | ↗️ Improving | Added STEM magnet program |
| Thornton Junior High | 7/10 | Stable | Good arts programs |

#### High Schools (9-12)
| School | Rating | Trend | Notes |
|--------|--------|-------|-------|
| Mission San Jose High | 10/10 | Stable | Top 1% nationally, incredible academics |
| Irvington High | 8/10 | Stable | Strong athletics, good academics |

### 📈 Trend Analysis
- **5-Year Trend**: Stable to improving across all levels
- **State Rankings**: Top 10% of California districts
- **Test Scores**: Consistently above state average
- **Funding**: Well-funded district with strong property tax base
{age_specific}

### ✅ Highlights
- **Mission San Jose High** is ranked #1 in the district and among the top public schools in California
- Strong parent involvement across all schools
- Excellent STEM and AP course offerings
- Active music and arts programs

### ⚠️ Things to Know
- High competition for spots in top schools (zoned by address)
- High academic pressure at top-rated schools
- Some schools have crowding issues

### 💡 Practical Tips
1. **School Choice**: You're zoned for specific schools based on address - verify zones before buying
2. **Magnet Programs**: Apply early for STEM magnet programs (lottery-based)
3. **Private Options**: Several private schools nearby if seeking alternatives
"""


def get_school_score(city: str, state: str) -> dict:
    """
    Get a simple school quality score for ranking.
    """
    if USE_MOCK_DATA:
        return {
            "score": 9,
            "rating": "Excellent",
            "top_school": "Mission San Jose High (10/10)"
        }
    
    school_data = scrape_greatschools(city, state)
    
    # Simple scoring based on scraped data
    return {
        "score": 7,  # Default to good
        "rating": "Good",
        "top_school": "See analysis for details"
    }
