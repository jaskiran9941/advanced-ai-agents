"""
SQLite database connection management
"""
import sqlite3
import os
from contextlib import contextmanager
from .models import DATABASE_SCHEMA

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "../../../product_market_fit.db")


def init_database():
    """Initialize database with schema"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Execute schema
    cursor.executescript(DATABASE_SCHEMA)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DATABASE_PATH}")


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)
