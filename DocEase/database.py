"""Database initialization and utility functions"""
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), 'conversions.db')


def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            conversion_type TEXT NOT NULL,
            output_file TEXT NOT NULL,
            user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Database initialized")


def init_users_table():
    """Initialize users table"""
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()
    logger.info("Users table initialized")


def migrate_users_column():
    """Add user_id column to conversions table if it doesn't exist"""
    conn = get_db_connection()
    try:
        conn.execute('ALTER TABLE conversions ADD COLUMN user_id INTEGER')
        logger.info("Added user_id column to conversions table")
    except Exception as e:
        logger.debug(f"user_id column may already exist: {str(e)}")
    conn.commit()
    conn.close()
