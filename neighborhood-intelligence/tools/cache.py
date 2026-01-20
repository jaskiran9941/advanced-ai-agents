"""
SQLite-based caching layer to reduce API calls and costs.
"""
import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

DB_PATH = "data/cache.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_cache():
    """Initialize the cache database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT,
            expires_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def _hash_key(key: str) -> str:
    """Create a consistent hash for cache keys."""
    return hashlib.md5(key.encode()).hexdigest()


def get_cached(key: str) -> Optional[Any]:
    """
    Get a cached value by key.
    
    Args:
        key: The cache key (will be hashed)
        
    Returns:
        The cached value if found and not expired, None otherwise
    """
    init_cache()
    conn = get_connection()
    cursor = conn.cursor()
    
    hashed_key = _hash_key(key)
    cursor.execute(
        "SELECT value, expires_at FROM cache WHERE key = ?",
        (hashed_key,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
    
    expires_at = datetime.fromisoformat(row["expires_at"])
    if datetime.now() > expires_at:
        # Cache expired, delete it
        delete_cached(key)
        return None
    
    return json.loads(row["value"])


def set_cached(key: str, value: Any, ttl_hours: int = 24) -> None:
    """
    Set a cached value.
    
    Args:
        key: The cache key (will be hashed)
        value: The value to cache (must be JSON-serializable)
        ttl_hours: Time-to-live in hours
    """
    init_cache()
    conn = get_connection()
    cursor = conn.cursor()
    
    hashed_key = _hash_key(key)
    expires_at = datetime.now() + timedelta(hours=ttl_hours)
    
    cursor.execute(
        """
        INSERT OR REPLACE INTO cache (key, value, expires_at)
        VALUES (?, ?, ?)
        """,
        (hashed_key, json.dumps(value), expires_at.isoformat())
    )
    conn.commit()
    conn.close()


def delete_cached(key: str) -> None:
    """Delete a cached value."""
    conn = get_connection()
    cursor = conn.cursor()
    hashed_key = _hash_key(key)
    cursor.execute("DELETE FROM cache WHERE key = ?", (hashed_key,))
    conn.commit()
    conn.close()


def clear_cache() -> None:
    """Clear all cached values."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cache")
    conn.commit()
    conn.close()


def clear_expired() -> int:
    """
    Clear expired cache entries.
    
    Returns:
        Number of entries deleted
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM cache WHERE expires_at < ?",
        (datetime.now().isoformat(),)
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted
