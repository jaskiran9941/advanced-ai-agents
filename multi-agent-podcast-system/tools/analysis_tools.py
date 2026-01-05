"""
Analysis Tools

Episode relevance analysis, novelty detection, and interest prediction.
Enhanced from agentic-podcast-summarizer/app_real.py with learning capabilities.
"""

from typing import List, Dict
from datetime import datetime, timedelta


def analyze_episode_relevance(episode_title: str, episode_description: str,
                              user_interests: List[str]) -> Dict:
    """
    Analyze if an episode matches user's interests.

    Migrated from app_real.py lines 314-338, enhanced for learning.

    Args:
        episode_title: Episode title
        episode_description: Episode description
        user_interests: User's interest keywords

    Returns:
        {
            "success": bool,
            "relevance_score": float (0-1),
            "matches": List[str],  # Which interests matched
            "reasoning": str,
            "recommendation": "summarize" | "skip"
        }
    """
    combined_text = (episode_title + " " + episode_description).lower()

    score = 0.3  # Base score
    matches = []

    for interest in user_interests:
        if interest.lower() in combined_text:
            score += 0.2
            matches.append(interest)

    score = min(score, 1.0)

    return {
        "success": True,
        "relevance_score": round(score, 2),
        "matches": matches,
        "reasoning": f"Found {len(matches)} keyword matches: {', '.join(matches) if matches else 'none'}",
        "recommendation": "summarize" if score > 0.5 else "skip"
    }


def detect_novelty(episode: Dict, user_history: List[Dict]) -> Dict:
    """
    Detect if episode content is novel compared to user's history.

    NEW - Core capability for ContentCuratorAgent.

    Args:
        episode: {title, description, tags}
        user_history: List of previously consumed episodes

    Returns:
        {
            "novelty_score": float (0-1),  # 1 = very novel
            "similar_episodes": List[Dict],  # Previously seen similar content
            "reasoning": str
        }
    """
    if not user_history:
        return {
            "novelty_score": 1.0,
            "similar_episodes": [],
            "reasoning": "No history available - considering novel"
        }

    episode_topics = set(episode.get("tags", []))
    episode_title_words = set(episode.get("title", "").lower().split())

    similarity_scores = []
    similar_episodes = []

    for past_episode in user_history[-30:]:  # Check last 30 episodes
        past_topics = set(past_episode.get("tags", []))
        past_title_words = set(past_episode.get("title", "").lower().split())

        # Calculate similarity
        topic_overlap = len(episode_topics & past_topics) / max(len(episode_topics | past_topics), 1)
        title_overlap = len(episode_title_words & past_title_words) / max(len(episode_title_words | past_title_words), 1)

        similarity = (topic_overlap * 0.6) + (title_overlap * 0.4)
        similarity_scores.append(similarity)

        if similarity > 0.5:
            similar_episodes.append({
                "title": past_episode.get("title"),
                "similarity": round(similarity, 2)
            })

    avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
    novelty_score = 1.0 - avg_similarity

    return {
        "novelty_score": round(novelty_score, 2),
        "similar_episodes": similar_episodes[:3],  # Top 3 most similar
        "reasoning": f"Average similarity to history: {round(avg_similarity, 2)}. Found {len(similar_episodes)} similar episodes."
    }


def predict_user_interest(episode: Dict, learned_preferences: Dict,
                         user_history: List[Dict]) -> Dict:
    """
    Predict user interest using learned preferences and behavior patterns.

    NEW - ML-lite scoring using learned data.

    Args:
        episode: Episode metadata
        learned_preferences: User's learned preferences from database
        user_history: Recent interaction history

    Returns:
        {
            "interest_score": float (0-1),
            "confidence": float (0-1),
            "factors": Dict[str, float],  # What influenced the score
            "reasoning": str
        }
    """
    factors = {}
    score = 0.5  # Start neutral

    # Factor 1: Topic preference match (40% weight)
    episode_tags = episode.get("tags", [])
    preferred_topics = learned_preferences.get("preferred_topics", {})

    if preferred_topics and episode_tags:
        topic_scores = []
        for tag in episode_tags:
            if tag in preferred_topics.get("value", []):
                topic_confidence = preferred_topics.get("confidence", 0.5)
                topic_scores.append(topic_confidence)

        if topic_scores:
            factors["topic_match"] = sum(topic_scores) / len(topic_scores)
            score += factors["topic_match"] * 0.4

    # Factor 2: Length preference (20% weight)
    preferred_length = learned_preferences.get("preferred_summary_style", {}).get("value", "detailed")
    episode_length = episode.get("duration", "Unknown")

    # Simple heuristic: if user prefers brief, favor shorter episodes
    if preferred_length == "brief" and "short" in str(episode_length).lower():
        factors["length_match"] = 0.8
        score += 0.16  # 0.8 * 0.2
    elif preferred_length == "detailed":
        factors["length_match"] = 0.6
        score += 0.12

    # Factor 3: Novelty vs familiarity balance (20% weight)
    novelty_result = detect_novelty(episode, user_history)
    novelty_score = novelty_result["novelty_score"]

    # Some users prefer novelty, some prefer familiar topics
    novelty_preference = learned_preferences.get("novelty_preference", {}).get("value", 0.5)
    novelty_factor = abs(novelty_score - float(novelty_preference))
    factors["novelty_balance"] = 1.0 - novelty_factor
    score += factors["novelty_balance"] * 0.2

    # Factor 4: Time-of-day preference (20% weight)
    current_hour = datetime.now().hour
    preferred_times = learned_preferences.get("preferred_reading_times", {}).get("value", [])

    if preferred_times and str(current_hour) in str(preferred_times):
        factors["time_match"] = 1.0
        score += 0.2
    else:
        factors["time_match"] = 0.5
        score += 0.1

    # Normalize score
    score = max(0.0, min(1.0, score))

    # Calculate confidence based on evidence
    total_evidence = sum([
        learned_preferences.get(key, {}).get("evidence_count", 0)
        for key in learned_preferences
    ])
    confidence = min(total_evidence / 50.0, 1.0)  # Max confidence after 50 interactions

    return {
        "interest_score": round(score, 2),
        "confidence": round(confidence, 2),
        "factors": {k: round(v, 2) for k, v in factors.items()},
        "reasoning": f"Predicted interest: {round(score, 2)} (confidence: {round(confidence, 2)}). "
                    f"Key factors: {', '.join([f'{k}={round(v, 2)}' for k, v in factors.items()])}"
    }


def assess_content_timeliness(episode: Dict) -> Dict:
    """
    Assess if episode content is time-sensitive or evergreen.

    Args:
        episode: Episode metadata

    Returns:
        {
            "is_timely": bool,
            "urgency_score": float (0-1),  # How urgent to consume
            "reasoning": str
        }
    """
    title = episode.get("title", "").lower()
    description = episode.get("description", "").lower()
    published = episode.get("published", "")

    # Check for time-sensitive keywords
    timely_keywords = [
        "breaking", "news", "today", "this week", "current",
        "latest", "2026", "just released", "announcement"
    ]

    urgency_score = 0.3  # Base urgency
    timely_indicators = []

    for keyword in timely_keywords:
        if keyword in title or keyword in description:
            urgency_score += 0.15
            timely_indicators.append(keyword)

    # Check recency (published in last 48 hours = more urgent)
    if published:
        try:
            pub_date = datetime.strptime(published, "%Y-%m-%d %H:%M")
            age_hours = (datetime.now() - pub_date).total_seconds() / 3600

            if age_hours < 48:
                urgency_score += 0.2
                timely_indicators.append("very recent")
        except Exception:
            pass

    urgency_score = min(urgency_score, 1.0)
    is_timely = urgency_score > 0.6

    return {
        "is_timely": is_timely,
        "urgency_score": round(urgency_score, 2),
        "reasoning": f"Urgency: {round(urgency_score, 2)}. "
                    f"{'Timely' if is_timely else 'Evergreen'} content. "
                    f"Indicators: {', '.join(timely_indicators) if timely_indicators else 'none'}"
    }
