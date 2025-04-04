#!/usr/bin/env python3
"""
Debug script for database operations
"""
import asyncio
import logging
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = "app.db"


def get_users():
    """Get all users from the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    conn.close()
    
    return [dict(user) for user in users]


def main():
    """Debug database operations"""
    try:
        logger.info("Checking users table...")
        users = get_users()
        
        if users:
            logger.info(f"Found {len(users)} users")
            for i, user in enumerate(users):
                # Log user details without showing full password hash
                safe_user = user.copy()
                if 'user_secret' in safe_user:
                    safe_user['user_secret'] = f"{safe_user['user_secret'][:10]}... (length: {len(safe_user['user_secret'])})"
                logger.info(f"User {i+1}: {safe_user}")
        else:
            logger.info("No users found in the database")
    
    except sqlite3.OperationalError as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()