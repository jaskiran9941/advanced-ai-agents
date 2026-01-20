"""
Orchestrator Agent - Coordinates all specialist agents and synthesizes results.
"""
import google.generativeai as genai
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_API_KEY, USE_MOCK_DATA
from agents.commute_agent import analyze_commute
from agents.lifestyle_agent import analyze_lifestyle
from agents.news_agent import analyze_future_development
from agents.school_agent import analyze_schools
from agents.safety_agent import analyze_safety


# Configure Gemini
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


ORCHESTRATOR_PROMPT = """You are a Neighborhood Intelligence Expert synthesizing multiple analyses into a comprehensive report.

Given all the analysis below from our specialist agents, create a unified "Day in the Life" narrative that helps someone understand what living at this address would really be like.

Structure your response as:
1. **Executive Summary** (2-3 sentences capturing the essence)
2. **Day-in-the-Life Narrative** (Morning routine → Commute → Evening → Weekend)
3. **Top 3 Highlights** (Best things about this location)
4. **Top 3 Concerns** (Things to be aware of)
5. **Final Verdict** (Is this a good fit for this person's life situation?)

USER PROFILE:
{user_profile}

COMMUTE ANALYSIS:
{commute_analysis}

LIFESTYLE ANALYSIS:
{lifestyle_analysis}

DEVELOPMENT ANALYSIS:
{development_analysis}

SCHOOL ANALYSIS:
{school_analysis}

SAFETY ANALYSIS:
{safety_analysis}

Write in a friendly, conversational tone that's easy to read."""


class UserProfile:
    """User profile with life situation details."""
    
    def __init__(
        self,
        address: str,
        city: str,
        state: str,
        work_address: str = None,
        has_kids: bool = False,
        child_ages: list = None,
        lifestyle_preferences: list = None,
        concerns: list = None,
        work_schedule: str = None
    ):
        self.address = address
        self.city = city
        self.state = state
        self.work_address = work_address
        self.has_kids = has_kids
        self.child_ages = child_ages or []
        self.lifestyle_preferences = lifestyle_preferences or ["park", "grocery"]
        self.concerns = concerns or []
        self.work_schedule = work_schedule or "Standard 9am-5pm, Monday-Friday"
    
    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "work_address": self.work_address,
            "has_kids": self.has_kids,
            "child_ages": self.child_ages,
            "lifestyle_preferences": self.lifestyle_preferences,
            "concerns": self.concerns,
            "work_schedule": self.work_schedule
        }
    
    def describe(self) -> str:
        """Generate a human-readable description of the user profile."""
        parts = [f"Looking at: {self.address}"]
        
        if self.work_address:
            parts.append(f"Works at: {self.work_address}")
        
        if self.has_kids and self.child_ages:
            parts.append(f"Has kids ages: {', '.join(map(str, self.child_ages))}")
        elif self.has_kids:
            parts.append("Has children")
        
        if self.lifestyle_preferences:
            parts.append(f"Lifestyle priorities: {', '.join(self.lifestyle_preferences)}")
        
        if self.concerns:
            parts.append(f"Concerns about: {', '.join(self.concerns)}")
        
        return "\n".join(parts)


def run_full_analysis(profile: UserProfile) -> dict:
    """
    Run a complete neighborhood analysis using all specialist agents.
    
    Args:
        profile: UserProfile with user's life situation
        
    Returns:
        dict with all analyses and synthesized report
    """
    results = {
        "profile": profile.to_dict(),
        "agents": {},
        "synthesis": None
    }
    
    # Run Commute Agent (if work address provided)
    if profile.work_address:
        print("🚗 Running Commute Analysis...")
        results["agents"]["commute"] = analyze_commute(
            profile.address,
            profile.work_address,
            profile.work_schedule
        )
    else:
        results["agents"]["commute"] = {"skipped": True, "reason": "No work address provided"}
    
    # Run Lifestyle Agent
    print("🏃 Running Lifestyle Analysis...")
    results["agents"]["lifestyle"] = analyze_lifestyle(
        profile.address,
        profile.lifestyle_preferences
    )
    
    # Run Development/News Agent
    print("📰 Running Development Analysis...")
    results["agents"]["development"] = analyze_future_development(
        profile.address,
        profile.city,
        profile.state
    )
    
    # Run School Agent (if has kids)
    if profile.has_kids:
        print("🏫 Running School Analysis...")
        results["agents"]["schools"] = analyze_schools(
            profile.address,
            profile.city,
            profile.state,
            profile.child_ages
        )
    else:
        results["agents"]["schools"] = {"skipped": True, "reason": "No children specified"}
    
    # Run Safety Agent
    print("🛡️ Running Safety Analysis...")
    results["agents"]["safety"] = analyze_safety(
        profile.address,
        profile.city,
        profile.state
    )
    
    # Synthesize all results
    print("📋 Synthesizing Final Report...")
    results["synthesis"] = synthesize_report(profile, results["agents"])
    
    return results


def synthesize_report(profile: UserProfile, agent_results: dict) -> dict:
    """
    Synthesize all agent results into a unified report.
    
    Args:
        profile: User profile
        agent_results: Results from all specialist agents
        
    Returns:
        dict with synthesis and narrative
    """
    if USE_MOCK_DATA or not GOOGLE_API_KEY:
        return {
            "narrative": _generate_mock_synthesis(profile, agent_results),
            "scores": _calculate_overall_scores(agent_results),
            "highlights": _extract_highlights(agent_results),
            "concerns": _extract_concerns(agent_results, profile)
        }
    
    # Use Gemini to synthesize
    model = genai.GenerativeModel("gemini-2.0-flash")
    
    prompt = ORCHESTRATOR_PROMPT.format(
        user_profile=profile.describe(),
        commute_analysis=_format_agent_result(agent_results.get("commute", {})),
        lifestyle_analysis=_format_agent_result(agent_results.get("lifestyle", {})),
        development_analysis=_format_agent_result(agent_results.get("development", {})),
        school_analysis=_format_agent_result(agent_results.get("schools", {})),
        safety_analysis=_format_agent_result(agent_results.get("safety", {}))
    )
    
    # Retry logic for rate limits
    import time
    max_retries = 3
    narrative = "Error generating synthesis after retries."
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            narrative = response.text
            break
        except Exception as e:
            if "429" in str(e) or "Resource exhausted" in str(e):
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    print(f"⚠️ Rate limit hit. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
            narrative = f"Error generating synthesis: {str(e)}"
            break
    
    return {
        "narrative": narrative,
        "scores": _calculate_overall_scores(agent_results),
        "highlights": _extract_highlights(agent_results),
        "concerns": _extract_concerns(agent_results, profile)
    }


def _format_agent_result(result: dict) -> str:
    """Format agent result for the synthesis prompt."""
    if result.get("skipped"):
        return f"SKIPPED: {result.get('reason', 'Not requested')}"
    
    analysis = result.get("analysis", "")
    summary = result.get("summary", {})
    
    return f"Analysis: {analysis[:2000]}\n\nSummary: {str(summary)}"


def _calculate_overall_scores(agent_results: dict) -> dict:
    """Calculate overall neighborhood scores."""
    scores = {}
    
    # Commute score
    commute = agent_results.get("commute", {})
    if not commute.get("skipped"):
        summary = commute.get("summary", {})
        # Extract minutes from rush hour text
        rush_hour = summary.get("rush_hour_driving", "30 min")
        try:
            minutes = int(rush_hour.split()[0])
            if minutes < 20:
                scores["commute"] = 9
            elif minutes < 30:
                scores["commute"] = 7
            elif minutes < 45:
                scores["commute"] = 5
            else:
                scores["commute"] = 3
        except:
            scores["commute"] = 5
    
    # Lifestyle score
    lifestyle = agent_results.get("lifestyle", {})
    if not lifestyle.get("skipped"):
        scores["lifestyle"] = lifestyle.get("summary", {}).get("overall_score", 5)
    
    # Safety score
    safety = agent_results.get("safety", {})
    if not safety.get("skipped"):
        scores["safety"] = safety.get("summary", {}).get("overall_score", 5)
    
    # Schools score
    schools = agent_results.get("schools", {})
    if not schools.get("skipped"):
        school_data = schools.get("summary", {}).get("schools", [])
        if school_data:
            avg = sum(s.get("rating", 5) for s in school_data) / len(school_data)
            scores["schools"] = round(avg, 1)
    
    # Overall score (weighted average)
    if scores:
        total = sum(scores.values())
        count = len(scores)
        scores["overall"] = round(total / count, 1)
    else:
        scores["overall"] = 5
    
    return scores


def _extract_highlights(agent_results: dict) -> list:
    """Extract top highlights from all agents."""
    highlights = []
    
    lifestyle = agent_results.get("lifestyle", {}).get("summary", {})
    if lifestyle.get("highlights"):
        highlights.extend(lifestyle["highlights"][:2])
    
    schools = agent_results.get("schools", {}).get("summary", {})
    if schools.get("highlights"):
        highlights.extend(schools["highlights"][:1])
    
    safety = agent_results.get("safety", {}).get("summary", {})
    if safety.get("safe_for"):
        highlights.append(f"Safe for: {', '.join(safety['safe_for'][:2])}")
    
    return highlights[:5]


def _extract_concerns(agent_results: dict, profile: UserProfile) -> list:
    """Extract top concerns from all agents."""
    concerns = []
    
    # Check commute
    commute = agent_results.get("commute", {}).get("summary", {})
    rush_hour = commute.get("rush_hour_driving", "")
    if rush_hour and "4" in rush_hour or "5" in rush_hour:
        concerns.append(f"Long commute: {rush_hour}")
    
    # Check lifestyle gaps
    lifestyle = agent_results.get("lifestyle", {}).get("summary", {})
    if lifestyle.get("concerns"):
        concerns.extend(lifestyle["concerns"][:2])
    
    # Check safety
    safety = agent_results.get("safety", {}).get("summary", {})
    if safety.get("primary_concerns"):
        concerns.extend(safety["primary_concerns"][:2])
    
    # Check development alerts
    development = agent_results.get("development", {}).get("summary", {})
    if development.get("red_flags"):
        concerns.extend(development["red_flags"][:1])
    
    return concerns[:5]


def _generate_mock_synthesis(profile: UserProfile, agent_results: dict) -> str:
    """Generate a mock synthesis narrative."""
    scores = _calculate_overall_scores(agent_results)
    
    return f"""# 🏠 Neighborhood Intelligence Report

## {profile.address}

### 📊 Overall Score: {scores.get('overall', 7)}/10

---

## Executive Summary

This location offers a **strong match** for your lifestyle priorities. With excellent schools, good safety scores, and reasonable access to your preferred amenities, it's a solid choice for {"families with children" if profile.has_kids else "your needs"}. The main trade-off is the commute, which will require some planning around rush hour times.

---

## 🌅 A Day in Your Life Here

**Morning (6:30am)**  
Wake up to a quiet residential street. If you're heading to work, leave by 7:30am to beat the worst of rush hour traffic. Your {agent_results.get('commute', {}).get('summary', {}).get('rush_hour_driving', '38 min')} commute is manageable if you can flex your schedule slightly.

**Daytime**  
{"The kids are at excellent schools nearby - " + agent_results.get('schools', {}).get('summary', {}).get('schools', [{}])[0].get('name', 'local elementary') + " is highly rated." if profile.has_kids else "The neighborhood is quiet during work hours."}

**Evening (6pm)**  
After work, you might stop by {"the temple (under a mile away)" if "temple" in profile.lifestyle_preferences else "the park"} before heading home. The neighborhood feels safe for evening walks.

**Weekend**  
This is where the location shines! {"Take the kids to " + "Central Park" if profile.has_kids else "Head to"} the nearby parks, visit Patel Brothers for groceries, or enjoy the many dining options nearby. The community has a strong {"family" if profile.has_kids else "neighborhood"} feel.

---

## ✅ Top Highlights

1. **Excellent Schools** - Top-rated options at all levels
2. **Strong Amenity Access** - Your lifestyle preferences are well-served
3. **Safe Neighborhood** - Family-friendly with improving crime trends

---

## ⚠️ Things to Consider

1. **Rush Hour Commute** - Plan for 35-45 min during peak times
2. **Limited Walkability** - Car is helpful for most errands
3. **Construction Nearby** - Some development activity in next 2 years

---

## 🎯 Final Verdict

**{"Great fit!" if scores.get('overall', 5) >= 7 else "Worth considering"}** This neighborhood aligns well with your priorities, especially around {"schools and family life" if profile.has_kids else "lifestyle amenities"}. The commute is the main consideration - if you can work hybrid or flex your hours, this becomes an even stronger choice.

**Recommendation:** {"Definitely worth pursuing" if scores.get('overall', 5) >= 7 else "Worth a serious look"} - schedule a visit during different times of day to get a feel for the traffic patterns and neighborhood vibe.
"""
