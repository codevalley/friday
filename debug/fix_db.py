#!/usr/bin/env python3
"""
Fix script for database setup
"""
import asyncio
import logging
import sqlite3
import os

from src.infrastructure.persistence.sqlalchemy.models import Base
from sqlalchemy import create_engine
from src.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Settings
settings = get_settings()

# Database path
DB_PATH = "app.db"


def recreate_database():
    """Recreate the database"""
    # Remove old database if it exists
    if os.path.exists(DB_PATH):
        logger.info(f"Removing old database: {DB_PATH}")
        os.remove(DB_PATH)
    
    # Create database and tables using SQLAlchemy
    engine = create_engine(settings.database_url.replace('aiosqlite', 'sqlite'))
    logger.info("Creating tables with SQLAlchemy...")
    Base.metadata.create_all(engine)


def create_test_user():
    """Create a test user with a known password"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert a test user with known credentials
    user_id = "test123"
    name = "testuser"
    # This is a bcrypt hash for 'password123'
    user_secret = "$2b$12$LN0h79YV4jxGnwtJHU6r0.ceXgYf4RKdUOVnnzmVM0hvx8xV01gJa"
    tier = "free"
    
    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    if cursor.fetchone():
        logger.info(f"User '{name}' already exists")
    else:
        logger.info(f"Creating test user: {name}")
        cursor.execute(
            "INSERT INTO users (user_id, name, user_secret, tier, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (user_id, name, user_secret, tier)
        )
        conn.commit()
    
    conn.close()


def verify_database():
    """Verify the database tables and schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    logger.info(f"Tables in database: {tables}")
    
    # Get schema for users table
    cursor.execute("PRAGMA table_info(users);")
    user_columns = cursor.fetchall()
    logger.info(f"Users table schema: {user_columns}")
    
    # Get schema for notes table
    cursor.execute("PRAGMA table_info(notes);")
    note_columns = cursor.fetchall()
    logger.info(f"Notes table schema: {note_columns}")
    
    # Check for users
    cursor.execute("SELECT COUNT(*) FROM users;")
    user_count = cursor.fetchone()[0]
    logger.info(f"Number of users: {user_count}")
    
    conn.close()


def main():
    """Fix database issues"""
    try:
        recreate_database()
        create_test_user()
        verify_database()
        logger.info("Database setup complete")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()