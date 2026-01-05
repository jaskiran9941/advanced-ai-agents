"""
Learning Engine (Simplified)

Learns user preferences from interactions.
"""

from typing import Dict
from database.db_manager import DatabaseManager


class PreferenceLearner:
    """
    Learns user preferences from behavior.

    Simplified: Just tracks topic preferences and reading times.
    """

    def __init__(self, db: DatabaseManager):
        """
        Initialize learner.

        Args:
            db: DatabaseManager instance
        """
        self.db = db

    def update_topic_preferences(self, user_id: str):
        """
        Learn which topics user likes based on interactions.

        Simple algorithm:
        - Count saves per topic
        - Topics with high save rate = preferred
        """
        # Get user's interaction history
        history_summary = self.db.get_user_history_summary(user_id, days_back=30)

        content_prefs = history_summary.get("content_preferences", [])

        if not content_prefs:
            return

        # Find most saved topics
        for pref in content_prefs[:5]:  # Top 5 topics
            topics = pref.get("topics")
            saves = pref.get("saves", 0)
            total = pref.get("interaction_count", 1)

            if saves > 0:
                confidence = min(saves / total, 1.0)

                self.db.update_learned_preference(
                    user_id=user_id,
                    preference_key="preferred_topics",
                    preference_value=str(topics),
                    confidence=confidence,
                    learned_from="implicit",
                    evidence_count=saves
                )

    def update_reading_time_preferences(self, user_id: str):
        """
        Learn when user prefers to read.

        Simple: Find most common reading hour.
        """
        history_summary = self.db.get_user_history_summary(user_id, days_back=30)

        interaction_patterns = history_summary.get("interaction_patterns", [])

        if not interaction_patterns:
            return

        # Find most common hour
        hour_counts = {}
        for pattern in interaction_patterns:
            hour = pattern.get("hour_of_day")
            count = pattern.get("count", 0)

            if hour is not None:
                hour_counts[hour] = hour_counts.get(hour, 0) + count

        if hour_counts:
            best_hour = max(hour_counts, key=hour_counts.get)
            total = sum(hour_counts.values())
            confidence = hour_counts[best_hour] / total

            self.db.update_learned_preference(
                user_id=user_id,
                preference_key="preferred_reading_time",
                preference_value=str(best_hour),
                confidence=confidence,
                learned_from="implicit",
                evidence_count=hour_counts[best_hour]
            )

    def learn_from_feedback(self, decision_id: str, feedback_value: float):
        """
        Record feedback for a decision.

        Args:
            decision_id: Decision to rate
            feedback_value: -1 (bad) to 1 (good)
        """
        success_metric = "positive" if feedback_value > 0.5 else "negative"

        self.db.record_decision_outcome(
            decision_id=decision_id,
            success_metric=success_metric,
            success_value=feedback_value
        )

    def run_learning_cycle(self, user_id: str):
        """
        Run full learning cycle for a user.

        Call this periodically (e.g., after every 10 interactions).
        """
        self.update_topic_preferences(user_id)
        self.update_reading_time_preferences(user_id)
