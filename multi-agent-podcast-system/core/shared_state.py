"""
Shared State Manager

Central hub for all agents to read/write shared state.
Acts as single source of truth for the multi-agent system.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid
from database.db_manager import DatabaseManager


class SharedStateManager:
    """
    Manages shared state across all agents in the system.

    Provides:
    - Database access
    - In-memory cache for hot data
    - State read/write operations
    - Learning data access
    """

    def __init__(self, db_path: str = "podcast_multiagent.db"):
        """
        Initialize shared state manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db = DatabaseManager(db_path)
        self._cache = {}  # In-memory cache for frequently accessed data

    # ========================================================================
    # USER STATE
    # ========================================================================

    def get_user_context(self, user_id: str) -> Dict:
        """
        Get complete user context for agents to make decisions.

        Returns:
            {
                "user_id": str,
                "preferences": {},  # Explicit preferences
                "learned_preferences": {},  # Discovered over time
                "recent_history": [],  # Recent interactions
                "engagement_summary": {}
            }
        """
        # Check cache first
        cache_key = f"user_context_{user_id}"
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            # Cache valid for 5 minutes
            if (datetime.now() - cached_time).seconds < 300:
                return cached_data

        # Build context from database
        user = self.db.get_user(user_id)
        if not user:
            # Create default user if doesn't exist
            self.db.create_user(
                user_id=user_id,
                email=f"{user_id}@example.com",
                preferences={
                    "recent_topics": ["AI", "technology"],
                    "preferred_length": "detailed"
                }
            )
            user = self.db.get_user(user_id)

        context = {
            "user_id": user_id,
            "preferences": user["preferences"],
            "learned_preferences": self.db.get_learned_preferences(user_id),
            "recent_history": self.db.get_user_interactions(user_id, limit=50),
            "engagement_summary": self.db.get_user_engagement_summary(user_id)
        }

        # Cache for next time
        self._cache[cache_key] = (datetime.now(), context)

        return context

    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update explicit user preferences."""
        self.db.update_user_preferences(user_id, preferences)
        # Invalidate cache
        cache_key = f"user_context_{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]

    # ========================================================================
    # CONTENT STATE
    # ========================================================================

    def add_episode(self, episode_id: str, title: str, description: str,
                   podcast_name: str, metadata: Dict) -> str:
        """
        Add a new episode to the system.

        Args:
            episode_id: Unique episode identifier
            title: Episode title
            description: Episode description
            podcast_name: Name of the podcast
            metadata: {topics, duration, published_date, audio_url, etc.}

        Returns:
            episode_id
        """
        return self.db.add_content(
            content_id=episode_id,
            content_type="episode",
            title=title,
            description=description,
            metadata={**metadata, "podcast_name": podcast_name},
            source="rss"
        )

    def add_podcast(self, podcast_id: str, name: str, description: str,
                   metadata: Dict) -> str:
        """Add a new podcast to the system."""
        return self.db.add_content(
            content_id=podcast_id,
            content_type="podcast",
            title=name,
            description=description,
            metadata=metadata,
            source="itunes"
        )

    def get_content(self, content_id: str) -> Optional[Dict]:
        """Get content by ID (episode or podcast)."""
        return self.db.get_content(content_id)

    # ========================================================================
    # INTERACTION TRACKING
    # ========================================================================

    def record_user_action(self, user_id: str, content_id: str, action: str,
                          context: Dict = None, duration: int = None) -> str:
        """
        Record a user interaction.

        Args:
            user_id: User identifier
            content_id: Content they interacted with
            action: 'click', 'save', 'dismiss', 'read', 'share'
            context: {time_of_day, device, location}
            duration: Seconds spent engaging

        Returns:
            interaction_id
        """
        # Enrich context with timestamp metadata
        enriched_context = context or {}
        now = datetime.now()
        enriched_context.update({
            "hour_of_day": now.hour,
            "day_of_week": now.strftime("%A"),
            "timestamp": now.isoformat()
        })

        interaction_id = self.db.record_interaction(
            user_id=user_id,
            content_id=content_id,
            event_type=action,
            context=enriched_context,
            duration_seconds=duration
        )

        # Invalidate user context cache
        cache_key = f"user_context_{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]

        return interaction_id

    # ========================================================================
    # AGENT DECISION TRACKING
    # ========================================================================

    def record_agent_decision(self, agent_name: str, user_id: str,
                             decision_type: str, input_data: Dict,
                             output_data: Dict, reasoning: str = None,
                             confidence: float = None,
                             execution_time_ms: int = None,
                             parent_task_id: str = None) -> str:
        """
        Record a decision made by an agent.

        Args:
            agent_name: 'discovery', 'curator', 'personalization', 'delivery'
            user_id: User this decision was for
            decision_type: 'recommend', 'filter', 'summarize', 'schedule'
            input_data: Full input the agent received
            output_data: Full output the agent produced
            reasoning: AI's explanation of decision
            confidence: 0-1 score
            execution_time_ms: How long it took
            parent_task_id: Orchestrator task this is part of

        Returns:
            decision_id
        """
        return self.db.record_agent_decision(
            agent_name=agent_name,
            user_id=user_id,
            decision_type=decision_type,
            input_data=input_data,
            output_data=output_data,
            reasoning=reasoning,
            confidence=confidence,
            execution_time_ms=execution_time_ms,
            parent_task_id=parent_task_id
        )

    def link_decision_to_outcome(self, decision_id: str, interaction_id: str = None,
                                success_metric: str = "unknown", success_value: float = 0.0):
        """
        Link an agent decision to its outcome.

        This is how the learning system knows if decisions were good.

        Args:
            decision_id: The decision to track
            interaction_id: User interaction that resulted (or None if ignored)
            success_metric: 'clicked', 'saved', 'ignored', 'dismissed'
            success_value: -1.0 (bad) to 1.0 (great)
        """
        self.db.record_decision_outcome(
            decision_id=decision_id,
            interaction_id=interaction_id,
            success_metric=success_metric,
            success_value=success_value
        )

    # ========================================================================
    # ORCHESTRATOR TASK MANAGEMENT
    # ========================================================================

    def create_task(self, user_id: str, user_goal: str,
                   intent_classification: Dict) -> str:
        """
        Create a new orchestrator task.

        Args:
            user_id: User who initiated this
            user_goal: Original user request
            intent_classification: {primary_intent, required_agents, optional_agents}

        Returns:
            task_id
        """
        return self.db.create_orchestrator_task(
            user_id=user_id,
            user_goal=user_goal,
            intent_classification=intent_classification
        )

    def update_task_status(self, task_id: str, status: str,
                          agent_sequence: List[str] = None,
                          result: Dict = None, error: str = None):
        """Update orchestrator task progress."""
        self.db.update_orchestrator_task(
            task_id=task_id,
            status=status,
            agent_sequence=agent_sequence,
            result=result,
            error_message=error
        )

    # ========================================================================
    # LEARNING DATA ACCESS
    # ========================================================================

    def get_learning_data_for_agent(self, agent_name: str, user_id: str) -> Dict:
        """
        Get historical data for an agent to learn from.

        Returns:
            {
                "past_decisions": [],  # What this agent decided before
                "decision_outcomes": [],  # How those decisions performed
                "user_patterns": {}  # User behavior patterns
            }
        """
        # Get past decisions by this agent for this user
        decisions = self.db.get_agent_decisions(
            agent_name=agent_name,
            user_id=user_id,
            limit=100
        )

        # Get user history summary
        user_patterns = self.db.get_user_history_summary(user_id, days_back=30)

        return {
            "past_decisions": decisions,
            "user_patterns": user_patterns,
            "learned_preferences": self.db.get_learned_preferences(user_id)
        }

    def update_learned_preference(self, user_id: str, preference_key: str,
                                  preference_value: str, confidence: float):
        """
        Update a learned preference.

        Example:
            preference_key = "preferred_summary_style"
            preference_value = "detailed"
            confidence = 0.85
        """
        self.db.update_learned_preference(
            user_id=user_id,
            preference_key=preference_key,
            preference_value=preference_value,
            confidence=confidence,
            learned_from="implicit"
        )

    # ========================================================================
    # ANALYTICS
    # ========================================================================

    def get_agent_performance_metrics(self, agent_name: str = None) -> List[Dict]:
        """Get performance metrics for agents."""
        return self.db.get_agent_performance(agent_name)

    def get_popular_topics(self, limit: int = 10) -> List[Dict]:
        """Get most popular topics across all users."""
        return self.db.get_topic_popularity(limit)

    # ========================================================================
    # UTILITY
    # ========================================================================

    def generate_id(self, prefix: str = "id") -> str:
        """Generate a unique ID."""
        return f"{prefix}_{uuid.uuid4().hex[:12]}"

    def clear_cache(self):
        """Clear in-memory cache."""
        self._cache.clear()
