"""
Scheduling Tools (Simplified for Learning)

Simple delivery timing and batching logic.
"""

from typing import List, Dict
from datetime import datetime


def predict_best_delivery_time(user_history: List[Dict]) -> Dict:
    """
    Predict best time to deliver content based on user reading patterns.

    Simplified version - just finds most common reading hour.

    Args:
        user_history: List of past interactions with timestamps

    Returns:
        {
            "recommended_hour": int (0-23),
            "confidence": float,
            "reasoning": str
        }
    """
    if not user_history:
        return {
            "recommended_hour": 8,  # Default: 8 AM
            "confidence": 0.3,
            "reasoning": "No history available. Defaulting to 8 AM."
        }

    # Count interactions by hour
    hour_counts = {}
    for interaction in user_history:
        try:
            timestamp = interaction.get("timestamp", "")
            hour = int(timestamp.split("T")[1].split(":")[0])
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        except Exception:
            continue

    if not hour_counts:
        return {
            "recommended_hour": 8,
            "confidence": 0.3,
            "reasoning": "Could not parse history. Defaulting to 8 AM."
        }

    # Find most common hour
    best_hour = max(hour_counts, key=hour_counts.get)
    total_interactions = sum(hour_counts.values())
    confidence = hour_counts[best_hour] / total_interactions

    return {
        "recommended_hour": best_hour,
        "confidence": round(confidence, 2),
        "reasoning": f"User most active at {best_hour}:00 ({hour_counts[best_hour]} interactions)"
    }


def batch_content_optimally(summaries: List[Dict]) -> Dict:
    """
    Group summaries for delivery.

    Simplified: Just group by urgency level.

    Args:
        summaries: List of summary dicts with urgency scores

    Returns:
        {
            "urgent": List[Dict],  # Deliver immediately
            "normal": List[Dict],  # Can batch
            "low_priority": List[Dict]  # Save for later
        }
    """
    urgent = []
    normal = []
    low_priority = []

    for summary in summaries:
        urgency = summary.get("urgency_score", 0.5)

        if urgency > 0.7:
            urgent.append(summary)
        elif urgency > 0.4:
            normal.append(summary)
        else:
            low_priority.append(summary)

    return {
        "urgent": urgent,
        "normal": normal,
        "low_priority": low_priority,
        "batching_strategy": f"{len(urgent)} urgent, {len(normal)} normal, {len(low_priority)} low priority"
    }


def assess_delivery_urgency(episode: Dict, relevance_score: float) -> float:
    """
    Simple urgency calculation.

    Args:
        episode: Episode metadata
        relevance_score: How relevant to user (0-1)

    Returns:
        Urgency score (0-1)
    """
    # Base urgency from relevance
    urgency = relevance_score * 0.6

    # Boost if published very recently
    published = episode.get("published", "")
    if published:
        try:
            pub_date = datetime.strptime(published, "%Y-%m-%d %H:%M")
            hours_old = (datetime.now() - pub_date).total_seconds() / 3600

            if hours_old < 24:
                urgency += 0.3
            elif hours_old < 72:
                urgency += 0.1
        except Exception:
            pass

    return min(urgency, 1.0)
