"""
Database Manager for Multi-Agent Podcast System

Handles SQLite connections, queries, and CRUD operations.
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager


class DatabaseManager:
    """Manages SQLite database connections and operations."""

    def __init__(self, db_path: str = "podcast_multiagent.db"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_database_exists()

    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        schema_path = Path(__file__).parent / "schema.sql"

        with sqlite3.connect(self.db_path) as conn:
            with open(schema_path, 'r') as f:
                schema = f.read()
                conn.executescript(schema)
            conn.commit()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # ========================================================================
    # USER OPERATIONS
    # ========================================================================

    def create_user(self, user_id: str, email: str, preferences: Dict) -> str:
        """Create a new user."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO users (user_id, email, preferences_json, last_active)
                VALUES (?, ?, ?, ?)
            """, (user_id, email, json.dumps(preferences), datetime.now()))
        return user_id

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID."""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM users WHERE user_id = ?
            """, (user_id,)).fetchone()

            if row:
                return {
                    "user_id": row["user_id"],
                    "email": row["email"],
                    "preferences": json.loads(row["preferences_json"]) if row["preferences_json"] else {},
                    "created_at": row["created_at"],
                    "last_active": row["last_active"]
                }
        return None

    def update_user_preferences(self, user_id: str, preferences: Dict):
        """Update user preferences."""
        with self.get_connection() as conn:
            conn.execute("""
                UPDATE users
                SET preferences_json = ?, last_active = ?
                WHERE user_id = ?
            """, (json.dumps(preferences), datetime.now(), user_id))

    # ========================================================================
    # CONTENT OPERATIONS
    # ========================================================================

    def add_content(self, content_id: str, content_type: str, title: str,
                    description: str, metadata: Dict, source: str = "unknown") -> str:
        """Add new content (episode or podcast)."""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO content
                (content_id, content_type, title, description, metadata_json, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (content_id, content_type, title, description, json.dumps(metadata), source))
        return content_id

    def get_content(self, content_id: str) -> Optional[Dict]:
        """Get content by ID."""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM content WHERE content_id = ?
            """, (content_id,)).fetchone()

            if row:
                return {
                    "content_id": row["content_id"],
                    "content_type": row["content_type"],
                    "title": row["title"],
                    "description": row["description"],
                    "metadata": json.loads(row["metadata_json"]) if row["metadata_json"] else {},
                    "first_seen": row["first_seen"],
                    "source": row["source"]
                }
        return None

    # ========================================================================
    # INTERACTION TRACKING
    # ========================================================================

    def record_interaction(self, user_id: str, content_id: str, event_type: str,
                          context: Dict = None, duration_seconds: int = None,
                          scroll_depth: float = None, completion_rate: float = None) -> str:
        """Record a user interaction with content."""
        interaction_id = f"int_{uuid.uuid4().hex[:12]}"

        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO interactions
                (interaction_id, user_id, content_id, event_type, context_json,
                 duration_seconds, scroll_depth, completion_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                interaction_id, user_id, content_id, event_type,
                json.dumps(context or {}), duration_seconds, scroll_depth, completion_rate
            ))

        return interaction_id

    def get_user_interactions(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Get recent interactions for a user."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT i.*, c.title, c.metadata_json
                FROM interactions i
                JOIN content c ON i.content_id = c.content_id
                WHERE i.user_id = ?
                ORDER BY i.timestamp DESC
                LIMIT ?
            """, (user_id, limit)).fetchall()

            return [{
                "interaction_id": row["interaction_id"],
                "content_id": row["content_id"],
                "content_title": row["title"],
                "event_type": row["event_type"],
                "timestamp": row["timestamp"],
                "duration_seconds": row["duration_seconds"],
                "context": json.loads(row["context_json"]) if row["context_json"] else {}
            } for row in rows]

    # ========================================================================
    # AGENT DECISION TRACKING
    # ========================================================================

    def record_agent_decision(self, agent_name: str, user_id: str, decision_type: str,
                             input_data: Dict, output_data: Dict, reasoning: str = None,
                             confidence: float = None, execution_time_ms: int = None,
                             parent_task_id: str = None) -> str:
        """Record an agent decision."""
        decision_id = f"dec_{uuid.uuid4().hex[:12]}"

        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO agent_decisions
                (decision_id, agent_name, user_id, decision_type, input_data_json,
                 output_data_json, reasoning, confidence_score, execution_time_ms, parent_task_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id, agent_name, user_id, decision_type,
                json.dumps(input_data), json.dumps(output_data),
                reasoning, confidence, execution_time_ms, parent_task_id
            ))

        return decision_id

    def get_agent_decisions(self, agent_name: str = None, user_id: str = None,
                           limit: int = 50) -> List[Dict]:
        """Get agent decisions with optional filters."""
        query = """
            SELECT * FROM agent_decisions
            WHERE 1=1
        """
        params = []

        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()

            return [{
                "decision_id": row["decision_id"],
                "agent_name": row["agent_name"],
                "decision_type": row["decision_type"],
                "input_data": json.loads(row["input_data_json"]),
                "output_data": json.loads(row["output_data_json"]),
                "reasoning": row["reasoning"],
                "confidence": row["confidence_score"],
                "timestamp": row["timestamp"],
                "execution_time_ms": row["execution_time_ms"]
            } for row in rows]

    def record_decision_outcome(self, decision_id: str, success_metric: str,
                               success_value: float, interaction_id: str = None,
                               notes: str = None) -> str:
        """Record the outcome of an agent decision."""
        outcome_id = f"out_{uuid.uuid4().hex[:12]}"

        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO decision_outcomes
                (outcome_id, decision_id, interaction_id, success_metric, success_value, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (outcome_id, decision_id, interaction_id, success_metric, success_value, notes))

        return outcome_id

    # ========================================================================
    # LEARNED PREFERENCES
    # ========================================================================

    def update_learned_preference(self, user_id: str, preference_key: str,
                                  preference_value: str, confidence: float,
                                  learned_from: str = "implicit", evidence_count: int = 1):
        """Update or insert a learned preference."""
        preference_id = f"pref_{uuid.uuid4().hex[:12]}"

        with self.get_connection() as conn:
            # Check if preference exists
            existing = conn.execute("""
                SELECT preference_id, evidence_count
                FROM learned_preferences
                WHERE user_id = ? AND preference_key = ?
            """, (user_id, preference_key)).fetchone()

            if existing:
                # Update existing
                new_evidence = existing["evidence_count"] + evidence_count
                conn.execute("""
                    UPDATE learned_preferences
                    SET preference_value = ?, confidence = ?, evidence_count = ?, last_updated = ?
                    WHERE preference_id = ?
                """, (preference_value, confidence, new_evidence, datetime.now(), existing["preference_id"]))
            else:
                # Insert new
                conn.execute("""
                    INSERT INTO learned_preferences
                    (preference_id, user_id, preference_key, preference_value,
                     confidence, learned_from, evidence_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (preference_id, user_id, preference_key, preference_value,
                      confidence, learned_from, evidence_count))

    def get_learned_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get all learned preferences for a user."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM learned_preferences
                WHERE user_id = ?
                ORDER BY confidence DESC
            """, (user_id,)).fetchall()

            preferences = {}
            for row in rows:
                preferences[row["preference_key"]] = {
                    "value": row["preference_value"],
                    "confidence": row["confidence"],
                    "learned_from": row["learned_from"],
                    "evidence_count": row["evidence_count"],
                    "last_updated": row["last_updated"]
                }

            return preferences

    # ========================================================================
    # ORCHESTRATOR TASKS
    # ========================================================================

    def create_orchestrator_task(self, user_id: str, user_goal: str,
                                 intent_classification: Dict) -> str:
        """Create a new orchestrator task."""
        task_id = f"task_{uuid.uuid4().hex[:12]}"

        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO orchestrator_tasks
                (task_id, user_id, user_goal, intent_classification_json, status)
                VALUES (?, ?, ?, ?, 'pending')
            """, (task_id, user_id, user_goal, json.dumps(intent_classification)))

        return task_id

    def update_orchestrator_task(self, task_id: str, status: str = None,
                                agent_sequence: List[str] = None,
                                result: Dict = None, error_message: str = None):
        """Update orchestrator task status and results."""
        with self.get_connection() as conn:
            updates = []
            params = []

            if status:
                updates.append("status = ?")
                params.append(status)

            if agent_sequence:
                updates.append("agent_sequence_json = ?")
                params.append(json.dumps(agent_sequence))

            if result:
                updates.append("result_json = ?")
                params.append(json.dumps(result))

            if error_message:
                updates.append("error_message = ?")
                params.append(error_message)

            if status in ['completed', 'failed']:
                updates.append("completed_at = ?")
                params.append(datetime.now())

            if updates:
                query = f"UPDATE orchestrator_tasks SET {', '.join(updates)} WHERE task_id = ?"
                params.append(task_id)
                conn.execute(query, params)

    # ========================================================================
    # ANALYTICS QUERIES
    # ========================================================================

    def get_user_engagement_summary(self, user_id: str) -> Dict:
        """Get engagement summary for a user."""
        with self.get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM user_engagement WHERE user_id = ?
            """, (user_id,)).fetchone()

            if row:
                return dict(row)
        return {}

    def get_agent_performance(self, agent_name: str = None) -> List[Dict]:
        """Get agent performance metrics."""
        query = "SELECT * FROM agent_success_rates"
        params = []

        if agent_name:
            query += " WHERE agent_name = ?"
            params.append(agent_name)

        with self.get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_topic_popularity(self, limit: int = 10) -> List[Dict]:
        """Get most popular topics."""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM topic_popularity LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_user_history_summary(self, user_id: str, days_back: int = 30) -> Dict:
        """Get comprehensive user history for learning."""
        with self.get_connection() as conn:
            # Get interaction patterns
            interactions = conn.execute("""
                SELECT
                    event_type,
                    COUNT(*) as count,
                    AVG(duration_seconds) as avg_duration,
                    strftime('%H', timestamp) as hour_of_day
                FROM interactions
                WHERE user_id = ?
                  AND timestamp > datetime('now', '-' || ? || ' days')
                GROUP BY event_type, hour_of_day
            """, (user_id, days_back)).fetchall()

            # Get content preferences (topics from saved/clicked content)
            content_prefs = conn.execute("""
                SELECT
                    json_extract(c.metadata_json, '$.topics') as topics,
                    COUNT(*) as interaction_count,
                    SUM(CASE WHEN i.event_type = 'save' THEN 1 ELSE 0 END) as saves
                FROM interactions i
                JOIN content c ON i.content_id = c.content_id
                WHERE i.user_id = ?
                  AND i.timestamp > datetime('now', '-' || ? || ' days')
                GROUP BY topics
                ORDER BY saves DESC, interaction_count DESC
            """, (user_id, days_back)).fetchall()

            return {
                "interaction_patterns": [dict(row) for row in interactions],
                "content_preferences": [dict(row) for row in content_prefs]
            }
