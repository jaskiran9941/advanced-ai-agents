"""
CRUD operations for database
"""
import json
import sqlite3
from typing import Dict, List, Any, Optional
from .connection import get_db_connection


# ========== IDEAS ==========

def create_idea(name: str, description: str, target_market: str, user_id: str = "default_user") -> int:
    """Create a new idea"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ideas (name, description, target_market, user_id) VALUES (?, ?, ?, ?)",
            (name, description, target_market, user_id)
        )
        conn.commit()
        return cursor.lastrowid


def get_idea(idea_id: int) -> Optional[Dict]:
    """Get idea by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def list_ideas(user_id: str = "default_user") -> List[Dict]:
    """List all ideas for a user"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ideas WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def update_idea_status(idea_id: int, status: str):
    """Update idea status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE ideas SET status = ? WHERE id = ?", (status, idea_id))
        conn.commit()


# ========== RESEARCH ==========

def save_research(idea_id: int, research_data: Dict[str, Any]) -> int:
    """Save research findings"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO research
            (idea_id, market_size, competitors, trends, pain_points, opportunities, sources, raw_findings)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                idea_id,
                research_data.get("market_size"),
                json.dumps(research_data.get("competitors", [])),
                json.dumps(research_data.get("trends", [])),
                json.dumps(research_data.get("pain_points", [])),
                json.dumps(research_data.get("opportunities", [])),
                json.dumps(research_data.get("sources", [])),
                json.dumps(research_data.get("raw_findings", {}))
            )
        )
        conn.commit()
        return cursor.lastrowid


def get_research(idea_id: int) -> Optional[Dict]:
    """Get research for an idea"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM research WHERE idea_id = ? ORDER BY created_at DESC LIMIT 1", (idea_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            # Parse JSON fields
            for field in ['competitors', 'trends', 'pain_points', 'opportunities', 'sources', 'raw_findings']:
                if data.get(field):
                    data[field] = json.loads(data[field])
            return data
        return None


# ========== ICP ==========

def save_icp(idea_id: int, icp_data: Dict[str, Any]) -> int:
    """Save ICP profile"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO icp_profiles
            (idea_id, demographics, psychographics, behaviors, pain_points, goals, decision_criteria, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                idea_id,
                json.dumps(icp_data.get("demographics", {})),
                json.dumps(icp_data.get("psychographics", {})),
                json.dumps(icp_data.get("behaviors", {})),
                json.dumps(icp_data.get("pain_points", [])),
                json.dumps(icp_data.get("goals", [])),
                json.dumps(icp_data.get("decision_criteria", [])),
                icp_data.get("confidence_score", 0.0)
            )
        )
        conn.commit()
        return cursor.lastrowid


def get_icp(idea_id: int) -> Optional[Dict]:
    """Get ICP for an idea"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM icp_profiles WHERE idea_id = ? ORDER BY created_at DESC LIMIT 1", (idea_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            # Parse JSON fields
            for field in ['demographics', 'psychographics', 'behaviors', 'pain_points', 'goals', 'decision_criteria']:
                if data.get(field):
                    data[field] = json.loads(data[field])
            return data
        return None


def get_icp_by_id(icp_id: int) -> Optional[Dict]:
    """Get ICP by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM icp_profiles WHERE id = ?", (icp_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            for field in ['demographics', 'psychographics', 'behaviors', 'pain_points', 'goals', 'decision_criteria']:
                if data.get(field):
                    data[field] = json.loads(data[field])
            return data
        return None


# ========== PERSONAS ==========

def save_persona(icp_id: int, persona_data: Dict[str, Any]) -> int:
    """Save a persona"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO personas
            (icp_id, name, age, occupation, location, background_story, personality_traits,
            communication_style, knowledge_base, preferences, objections)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                icp_id,
                persona_data.get("name"),
                persona_data.get("age"),
                persona_data.get("occupation"),
                persona_data.get("location"),
                persona_data.get("background_story"),
                json.dumps(persona_data.get("personality_traits", [])),
                persona_data.get("communication_style"),
                json.dumps(persona_data.get("knowledge_base", {})),
                json.dumps(persona_data.get("preferences", {})),
                json.dumps(persona_data.get("objections", []))
            )
        )
        conn.commit()
        return cursor.lastrowid


def get_persona(persona_id: int) -> Optional[Dict]:
    """Get persona by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE id = ?", (persona_id,))
        row = cursor.fetchone()
        if row:
            data = dict(row)
            for field in ['personality_traits', 'knowledge_base', 'preferences', 'objections']:
                if data.get(field):
                    data[field] = json.loads(data[field])
            return data
        return None


def list_personas(icp_id: int) -> List[Dict]:
    """List all personas for an ICP"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE icp_id = ? AND is_active = 1", (icp_id,))
        rows = cursor.fetchall()
        personas = []
        for row in rows:
            data = dict(row)
            for field in ['personality_traits', 'knowledge_base', 'preferences', 'objections']:
                if data.get(field):
                    data[field] = json.loads(data[field])
            personas.append(data)
        return personas


# ========== CONVERSATIONS ==========

def save_conversation(persona_id: int, session_id: str, user_message: str,
                     persona_response: str, sentiment: str = None) -> int:
    """Save a conversation exchange"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO persona_conversations
            (persona_id, session_id, user_message, persona_response, sentiment)
            VALUES (?, ?, ?, ?, ?)""",
            (persona_id, session_id, user_message, persona_response, sentiment)
        )
        conn.commit()
        return cursor.lastrowid


def get_conversation_history(session_id: str) -> List[Dict]:
    """Get conversation history for a session"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM persona_conversations WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# ========== WORKFLOW TRACKING ==========

def start_workflow(idea_id: int, workflow_type: str, input_state: Dict) -> int:
    """Start tracking a workflow execution"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO workflow_executions (idea_id, workflow_type, status, input_state) VALUES (?, ?, ?, ?)",
            (idea_id, workflow_type, "running", json.dumps(input_state))
        )
        conn.commit()
        return cursor.lastrowid


def complete_workflow(workflow_id: int, output_state: Dict, error: str = None):
    """Mark workflow as complete"""
    status = "failed" if error else "completed"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE workflow_executions
            SET status = ?, output_state = ?, error_message = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?""",
            (status, json.dumps(output_state), error, workflow_id)
        )
        conn.commit()


def get_workflow_status(idea_id: int, workflow_type: str) -> Optional[Dict]:
    """Get latest workflow status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM workflow_executions
            WHERE idea_id = ? AND workflow_type = ?
            ORDER BY started_at DESC LIMIT 1""",
            (idea_id, workflow_type)
        )
        row = cursor.fetchone()
        if row:
            data = dict(row)
            if data.get('input_state'):
                data['input_state'] = json.loads(data['input_state'])
            if data.get('output_state'):
                data['output_state'] = json.loads(data['output_state'])
            return data
        return None


def update_workflow_progress(workflow_id: int, current_step: str, progress_percent: int, step_message: str = None):
    """Update workflow progress"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE workflow_executions
            SET current_step = ?, progress_percent = ?, step_message = ?
            WHERE id = ?""",
            (current_step, progress_percent, step_message, workflow_id)
        )
        conn.commit()


def get_workflow_progress(idea_id: int, workflow_type: str) -> Optional[Dict]:
    """Get workflow progress for polling"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, status, current_step, progress_percent, step_message, error_message
            FROM workflow_executions
            WHERE idea_id = ? AND workflow_type = ?
            ORDER BY started_at DESC LIMIT 1""",
            (idea_id, workflow_type)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
