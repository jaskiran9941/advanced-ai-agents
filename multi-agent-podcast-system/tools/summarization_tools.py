"""
Summarization Tools

GPT-4 based content summarization with context-aware styles.
Migrated and enhanced from agentic-podcast-summarizer/app_real.py
"""

from openai import OpenAI
from typing import Dict, Literal


SummaryStyle = Literal["brief", "detailed", "technical"]


def generate_summary(client: OpenAI, episode_title: str, episode_description: str,
                    style: SummaryStyle = "detailed", temperature: float = 0.7,
                    max_tokens: int = 800) -> Dict:
    """
    Generate AI summary using GPT-4.

    Migrated from app_real.py lines 340-377.

    Args:
        client: OpenAI client instance
        episode_title: Episode title
        episode_description: Episode description
        style: Summary style (brief/detailed/technical)
        temperature: GPT-4 temperature (0-1)
        max_tokens: Maximum tokens in response

    Returns:
        {
            "success": bool,
            "summary": str,
            "style_used": str,
            "source": "GPT-4",
            "tokens_used": int,
            "error": str (if failed)
        }
    """
    style_prompts = {
        "brief": "Create a brief 2-3 sentence summary focusing on the main takeaway.",
        "detailed": "Create a detailed summary with 5-7 key bullet points covering main topics and insights.",
        "technical": "Create an in-depth technical analysis with detailed explanations suitable for experts."
    }

    prompt = f"""{style_prompts[style]}

Episode Title: {episode_title}

Episode Description:
{episode_description[:4000]}

Provide a clear, informative summary."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )

        summary = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if response.usage else 0

        return {
            "success": True,
            "summary": summary,
            "style_used": style,
            "source": "GPT-4",
            "tokens_used": tokens_used
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"GPT-4 summarization failed: {str(e)}",
            "style_used": style
        }


def adapt_summary_depth(client: OpenAI, summary: str, target_depth: str,
                       user_expertise: str = "intermediate") -> Dict:
    """
    Adapt an existing summary to different depth/expertise level.

    NEW - Part of PersonalizationAgent capabilities.

    Args:
        client: OpenAI client
        summary: Existing summary to adapt
        target_depth: 'surface' | 'moderate' | 'deep'
        user_expertise: 'beginner' | 'intermediate' | 'expert'

    Returns:
        {
            "success": bool,
            "adapted_summary": str,
            "original_depth": str,
            "target_depth": str
        }
    """
    depth_instructions = {
        "surface": "Simplify this to high-level concepts only, suitable for quick scanning.",
        "moderate": "Maintain current level of detail with good balance of overview and specifics.",
        "deep": "Expand this with more technical details, examples, and deeper analysis."
    }

    expertise_context = {
        "beginner": "Explain concepts clearly with minimal jargon. Define technical terms.",
        "intermediate": "Use standard terminology. Brief explanations for complex concepts.",
        "expert": "Use technical language freely. Focus on nuances and advanced insights."
    }

    prompt = f"""{depth_instructions[target_depth]}

Context: This is for a {user_expertise}-level reader. {expertise_context[user_expertise]}

Original Summary:
{summary}

Adapted Summary:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )

        return {
            "success": True,
            "adapted_summary": response.choices[0].message.content,
            "original_depth": "unknown",
            "target_depth": target_depth,
            "user_expertise": user_expertise
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Summary adaptation failed: {str(e)}"
        }


def adjust_summary_focus(client: OpenAI, summary: str, focus_areas: list[str]) -> Dict:
    """
    Adjust summary to emphasize specific focus areas based on user interests.

    NEW - Part of PersonalizationAgent.

    Args:
        client: OpenAI client
        summary: Original summary
        focus_areas: Topics to emphasize (e.g., ["applications", "research", "business implications"])

    Returns:
        {
            "success": bool,
            "focused_summary": str,
            "focus_areas": List[str]
        }
    """
    focus_list = ", ".join(focus_areas)

    prompt = f"""Rewrite this summary to emphasize these specific aspects: {focus_list}

Keep the same length but reorganize and emphasize content related to {focus_list}.
De-emphasize or condense other aspects.

Original Summary:
{summary}

Focused Summary:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )

        return {
            "success": True,
            "focused_summary": response.choices[0].message.content,
            "focus_areas": focus_areas
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Focus adjustment failed: {str(e)}"
        }


def format_for_context(summary: str, consumption_context: str) -> str:
    """
    Format summary for specific consumption context (quick formatting, no LLM).

    Args:
        summary: Summary text
        consumption_context: 'morning_brief' | 'commute' | 'deep_reading' | 'email_digest'

    Returns:
        Formatted summary string
    """
    if consumption_context == "morning_brief":
        # Short paragraphs, bullet points
        lines = summary.split("\n")
        formatted = "☀️ Morning Brief\n\n" + "\n\n".join(lines[:3])

    elif consumption_context == "commute":
        # Mobile-friendly, short sentences
        formatted = "🚗 Commute Summary\n\n" + summary.replace(". ", ".\n\n")[:500] + "..."

    elif consumption_context == "deep_reading":
        # Full format with sections
        formatted = "📚 Deep Dive\n\n" + summary

    elif consumption_context == "email_digest":
        # Email-friendly HTML-style
        formatted = f"<h3>Episode Summary</h3>\n\n{summary}\n\n---"

    else:
        formatted = summary

    return formatted


def generate_custom_highlights(client: OpenAI, episode_description: str,
                               user_interests: list[str]) -> Dict:
    """
    Extract highlights specifically relevant to user interests.

    NEW - Part of PersonalizationAgent.

    Args:
        client: OpenAI client
        episode_description: Full episode description
        user_interests: User's specific interests (e.g., ["AI safety", "neural networks"])

    Returns:
        {
            "success": bool,
            "highlights": List[str],  # Relevant quotes/points
            "relevance_scores": Dict[str, float]  # Score per interest
        }
    """
    interests_list = ", ".join(user_interests)

    prompt = f"""Extract 3-5 specific highlights from this episode that relate to: {interests_list}

For each highlight, include:
- The specific point or quote
- Which interest area it relates to
- Why it's relevant

Episode Description:
{episode_description[:3000]}

Format as a numbered list."""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )

        highlights_text = response.choices[0].message.content
        highlights = [h.strip() for h in highlights_text.split("\n") if h.strip() and h[0].isdigit()]

        return {
            "success": True,
            "highlights": highlights,
            "user_interests": user_interests
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Highlight extraction failed: {str(e)}"
        }
