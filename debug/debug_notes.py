#!/usr/bin/env python3
"""
Debug script for notes functionality
"""
import asyncio
import logging
import httpx
import traceback
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Base URL for API
BASE_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "name": "testuser",
    "password": "password123",
}

TEST_NOTE = {
    "content": "This is a debug test note."
}

# Database path
DB_PATH = "app.db"


def check_notes_table():
    """Check the notes table in the database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check schema
        cursor.execute("PRAGMA table_info(notes);")
        schema = cursor.fetchall()
        logger.info(f"Notes table schema: {schema}")
        
        # Check for notes
        cursor.execute("SELECT * FROM notes;")
        notes = cursor.fetchall()
        logger.info(f"Notes in database: {len(notes)}")
        for note in notes:
            logger.info(f"Note: {note}")
        
        conn.close()
    except Exception as e:
        logger.error(f"Error checking notes table: {str(e)}")


async def debug_notes():
    """Debug notes functionality"""
    async with httpx.AsyncClient() as client:
        # First, login to get token
        try:
            logger.info("Logging in...")
            response = await client.post(f"{BASE_URL}/users/token", json=TEST_USER)
            
            if response.status_code != 200:
                logger.error(f"Failed to login: {response.text}")
                return
            
            token_data = response.json()
            token = token_data["access_token"]
            logger.info(f"Got token: {token[:20]}...")
            
            # Set auth header for subsequent requests
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            # Create a note
            logger.info("Creating note...")
            response = await client.post(
                f"{BASE_URL}/notes/", 
                json=TEST_NOTE,
                headers=headers
            )
            
            if response.status_code != 201:
                logger.error(f"Failed to create note: {response.text}")
                return
            
            note = response.json()
            note_id = note["note_id"]
            logger.info(f"Note created with ID: {note_id}")
            logger.info(f"Note response: {note}")
            
            # Check the database directly
            check_notes_table()
            
            # Read the note
            logger.info(f"Reading note {note_id}...")
            response = await client.get(
                f"{BASE_URL}/notes/{note_id}",
                headers=headers
            )
            
            logger.info(f"Read note response status: {response.status_code}")
            logger.info(f"Read note response: {response.text}")
            
            # List all notes
            logger.info("Listing all notes...")
            response = await client.get(
                f"{BASE_URL}/notes/",
                headers=headers
            )
            
            logger.info(f"List notes response status: {response.status_code}")
            logger.info(f"List notes response: {response.text}")
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(debug_notes())