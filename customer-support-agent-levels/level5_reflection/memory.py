"""
memory.py — Level 4
====================
SQLite-backed customer interaction history.

Two responsibilities:
  1. load_customer_history(customer_id)
       → returns past interactions as a formatted string
       → injected into the system prompt at session start

  2. save_interaction(customer_id, messages)
       → calls Claude to extract structured fields from the conversation
       → saves one row to SQLite per session

Schema (one row per conversation):
  customer_id      — who the customer was
  timestamp        — when the session ended
  issue_type       — damaged_item | late_delivery | return_request |
                     policy_question | billing | exchange | other
  resolution       — resolved | return_processed | escalated |
                     unresolved | info_provided
  sentiment        — positive | neutral | frustrated | angry
  orders_mentioned — comma-separated order IDs (e.g. "ORD-1001,ORD-1004")
  summary          — 1-2 sentence plain-English summary of the interaction
"""

import os
import json
import sqlite3
import anthropic
from datetime import datetime

# Shared across all levels — one DB for the whole project
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "shared", "memory.sqlite")

# ---------------------------------------------------------------------------
# DB setup
# ---------------------------------------------------------------------------

def _get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the interactions table if it doesn't exist."""
    with _get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id      TEXT    NOT NULL,
                timestamp        TEXT    NOT NULL,
                issue_type       TEXT,
                resolution       TEXT,
                sentiment        TEXT,
                orders_mentioned TEXT,
                summary          TEXT
            )
        """)


# ---------------------------------------------------------------------------
# Load history → inject into system prompt
# ---------------------------------------------------------------------------

def load_customer_history(customer_id: str, limit: int = 5) -> str:
    """
    Return a formatted string summarising the customer's last N sessions.
    Returns empty string if no history exists (new customer).
    """
    init_db()
    with _get_conn() as conn:
        rows = conn.execute(
            """SELECT timestamp, issue_type, resolution, sentiment,
                      orders_mentioned, summary
               FROM interactions
               WHERE customer_id = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (customer_id, limit),
        ).fetchall()

    if not rows:
        return ""

    lines = [f"Previous interactions with this customer ({len(rows)} session(s)):"]
    for row in rows:
        date = row["timestamp"][:10]   # just the date part
        orders = f" re: {row['orders_mentioned']}" if row["orders_mentioned"] else ""
        lines.append(
            f"- {date}: {row['issue_type']} → {row['resolution']} "
            f"({row['sentiment']}){orders}\n"
            f"  {row['summary']}"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Save interaction → extract structured fields with Claude
# ---------------------------------------------------------------------------

EXTRACTION_PROMPT = """You are extracting structured data from a customer support conversation.

Return ONLY a JSON object with exactly these fields:
{
  "issue_type": one of [damaged_item, late_delivery, return_request, policy_question, billing, exchange, other],
  "resolution": one of [resolved, return_processed, escalated, unresolved, info_provided],
  "sentiment": one of [positive, neutral, frustrated, angry],
  "orders_mentioned": comma-separated order IDs mentioned (e.g. "ORD-1001,ORD-1004"), or "" if none,
  "summary": a single sentence describing what happened and how it was resolved
}

No extra text, no markdown, just the JSON object."""


def save_interaction(customer_id: str, messages: list) -> dict:
    """
    Extract structured fields from the conversation and save to SQLite.
    Returns the saved row as a dict (useful for displaying in the UI).
    """
    init_db()

    # Build a plain-text transcript for Claude to extract from
    transcript_parts = []
    for msg in messages:
        if isinstance(msg["content"], list):
            continue   # skip tool_result messages
        role = msg["role"].upper()
        transcript_parts.append(f"{role}: {msg['content']}")
    transcript = "\n".join(transcript_parts)

    if not transcript.strip():
        return {}

    # Ask Claude to extract the structured fields
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=EXTRACTION_PROMPT,
        messages=[{"role": "user", "content": f"Conversation:\n{transcript}"}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude wrapped the JSON (e.g. ```json ... ```)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if Claude didn't return clean JSON
        extracted = {
            "issue_type": "other",
            "resolution": "unresolved",
            "sentiment": "neutral",
            "orders_mentioned": "",
            "summary": raw[:200],
        }

    row = {
        "customer_id":      customer_id,
        "timestamp":        datetime.utcnow().isoformat(),
        "issue_type":       extracted.get("issue_type", "other"),
        "resolution":       extracted.get("resolution", "unresolved"),
        "sentiment":        extracted.get("sentiment", "neutral"),
        "orders_mentioned": extracted.get("orders_mentioned", ""),
        "summary":          extracted.get("summary", ""),
    }

    with _get_conn() as conn:
        conn.execute(
            """INSERT INTO interactions
               (customer_id, timestamp, issue_type, resolution,
                sentiment, orders_mentioned, summary)
               VALUES (:customer_id, :timestamp, :issue_type, :resolution,
                       :sentiment, :orders_mentioned, :summary)""",
            row,
        )

    return row
