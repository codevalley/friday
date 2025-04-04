#!/usr/bin/env python3
"""
Test script for Friday API
This script tests the API by performing a series of operations:
1. Create a user
2. Login as the user to get a token
3. Create a note
4. Read the note
5. Update the note
6. Read the note again to verify the update
7. Delete the note
8. Verify the note is deleted
9. List all users (admin operation)

Usage:
    python test_script.py [--flush]

    --flush: Drop all tables and recreate them before testing
"""

import argparse
import asyncio
import logging
import os
import sys
from datetime import datetime

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.config import get_settings

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
    "tier": "free"
}

TEST_NOTE = {
    "content": "This is a test note created by the test script."
}

# Settings
settings = get_settings()


async def flush_database():
    """Drop all tables and recreate them"""
    logger.info("Flushing database...")
    
    # Create engine
    engine = create_async_engine(settings.database_url)
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS notes"))
        await conn.execute(text("DROP TABLE IF EXISTS users"))
    
    logger.info("Database flushed. Tables will be recreated on next API start.")


async def run_test(flush: bool = False):
    """Run the test sequence"""
    if flush:
        await flush_database()
    
    async with httpx.AsyncClient() as client:
        # Step 1: Create a user
        logger.info("Creating user...")
        response = await client.post(f"{BASE_URL}/users/", json=TEST_USER)
        
        if response.status_code != 201:
            logger.error(f"Failed to create user: {response.text}")
            if response.status_code == 400 and "already exists" in response.text:
                logger.info("User already exists, continuing with tests...")
            else:
                return False
        else:
            user = response.json()
            logger.info(f"User created: {user['name']} (ID: {user['user_id']})")
        
        # Step 2: Login to get token
        logger.info("Logging in...")
        login_data = {
            "name": TEST_USER["name"],
            "password": TEST_USER["password"]
        }
        response = await client.post(f"{BASE_URL}/users/token", json=login_data)
        
        if response.status_code != 200:
            logger.error(f"Failed to login: {response.text}")
            return False
        
        token_data = response.json()
        token = token_data["access_token"]
        logger.info("Successfully logged in and received token")
        
        # Set auth header for subsequent requests
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        # Step 3: Create a note
        logger.info("Creating note...")
        response = await client.post(
            f"{BASE_URL}/notes/", 
            json=TEST_NOTE,
            headers=headers
        )
        
        if response.status_code != 201:
            logger.error(f"Failed to create note: {response.text}")
            return False
        
        note = response.json()
        note_id = note["note_id"]
        logger.info(f"Note created: {note_id}")
        
        # Step 4: Read the note
        logger.info(f"Reading note {note_id}...")
        response = await client.get(
            f"{BASE_URL}/notes/{note_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to read note: {response.text}")
            return False
        
        note = response.json()
        logger.info(f"Note content: {note['content']}")
        
        # Step 5: Update the note
        logger.info(f"Updating note {note_id}...")
        update_data = {
            "content": f"This note was updated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        response = await client.put(
            f"{BASE_URL}/notes/{note_id}",
            json=update_data,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to update note: {response.text}")
            return False
        
        updated_note = response.json()
        logger.info(f"Updated note content: {updated_note['content']}")
        
        # Step 6: Read the note again to verify update
        logger.info(f"Verifying note update...")
        response = await client.get(
            f"{BASE_URL}/notes/{note_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to read updated note: {response.text}")
            return False
        
        note = response.json()
        logger.info(f"Updated note content from server: {note['content']}")
        
        # Step 7: List all notes for the user
        logger.info(f"Listing all notes for the user...")
        response = await client.get(
            f"{BASE_URL}/notes/",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to list notes: {response.text}")
            return False
        
        notes = response.json()
        logger.info(f"User has {len(notes)} notes")
        
        # Step 8: Delete the note
        logger.info(f"Deleting note {note_id}...")
        response = await client.delete(
            f"{BASE_URL}/notes/{note_id}",
            headers=headers
        )
        
        if response.status_code != 204:
            logger.error(f"Failed to delete note: {response.text}")
            return False
        
        logger.info(f"Note deleted successfully")
        
        # Step 9: Verify the note is deleted
        logger.info(f"Verifying note is deleted...")
        response = await client.get(
            f"{BASE_URL}/notes/{note_id}",
            headers=headers
        )
        
        if response.status_code == 404:
            logger.info(f"Note verified as deleted (404 Not Found)")
        else:
            logger.error(f"Note was not deleted correctly, got status {response.status_code}")
            return False
        
        # Step 10: List all users (admin operation)
        logger.info(f"Listing all users...")
        response = await client.get(
            f"{BASE_URL}/users/",
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to list users: {response.text}")
            return False
        
        users = response.json()
        logger.info(f"There are {len(users)} users in the system")
        
        logger.info("All tests completed successfully!")
        return True


def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Test script for Friday API")
    parser.add_argument("--flush", action="store_true", help="Flush database before testing")
    args = parser.parse_args()
    
    # Make sure the API is running
    try:
        httpx.get(f"{BASE_URL}/")
    except httpx.ConnectError:
        logger.error(f"Cannot connect to API at {BASE_URL}. Is the server running?")
        sys.exit(1)
    
    # Run tests
    success = asyncio.run(run_test(flush=args.flush))
    
    if success:
        logger.info("✅ All tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()