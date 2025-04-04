#!/usr/bin/env python3
"""
Fix script for database setup (simple version)
"""
import logging
import sqlite3
import os
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "app.db"


def recreate_database():
    """Recreate the database"""
    # Remove old database if it exists
    if os.path.exists(DB_PATH):
        logger.info(f"Removing old database: {DB_PATH}")
        os.remove(DB_PATH)
    
    # Create new database with SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE users (
        user_id VARCHAR(36) PRIMARY KEY,
        name VARCHAR(50) NOT NULL UNIQUE,
        user_secret VARCHAR(255) NOT NULL,
        tier VARCHAR(20) NOT NULL,
        created_at DATETIME
    )
    ''')
    
    # Create notes table
    cursor.execute('''
    CREATE TABLE notes (
        note_id VARCHAR(36) PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        content TEXT NOT NULL,
        created DATETIME,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    logger.info("Database tables created")


def create_test_user():
    """Create a test user with a known password"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Insert a test user with known credentials
    user_id = str(uuid.uuid4())
    name = "testuser"
    # This is a bcrypt hash for 'password123'
    user_secret = "$2b$12$LN0h79YV4jxGnwtJHU6r0.ceXgYf4RKdUOVnnzmVM0hvx8xV01gJa"
    tier = "free"
    
    logger.info(f"Creating test user: {name}")
    cursor.execute(
        "INSERT INTO users (user_id, name, user_secret, tier, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, user_secret, tier, datetime.now().isoformat())
    )
    conn.commit()
    
    logger.info(f"Test user created with ID: {user_id}")
    
    conn.close()


def verify_database():
    """Verify the database tables and schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    logger.info(f"Tables in database: {tables}")
    
    # Check for users
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    logger.info(f"Users in database: {len(users)}")
    for user in users:
        logger.info(f"User: {user[0]}, {user[1]}, Secret: {user[2][:10]}...")
    
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
        logger.exception(e)


if __name__ == "__main__":
    main()