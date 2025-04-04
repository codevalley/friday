#!/usr/bin/env python3
"""
Test login script for Friday API
"""
import asyncio
import logging
import httpx
import traceback

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


async def test_login():
    """Test login functionality"""
    async with httpx.AsyncClient() as client:
        # Test login
        try:
            logger.info("Testing login...")
            response = await client.post(f"{BASE_URL}/users/token", json=TEST_USER)
            logger.info(f"Login response: {response.status_code}")
            logger.info(f"Login headers: {response.headers}")
            logger.info(f"Login body: {response.text}")
            
            if response.status_code == 200:
                token_data = response.json()
                token = token_data["access_token"]
                logger.info(f"Got token: {token[:20]}...")
                
                # Test authenticated endpoint
                headers = {
                    "Authorization": f"Bearer {token}"
                }
                
                logger.info("Testing authenticated endpoint...")
                response = await client.get(f"{BASE_URL}/users/me", headers=headers)
                logger.info(f"Auth response: {response.status_code}")
                logger.info(f"Auth body: {response.text}")
                
        except Exception as e:
            logger.error(f"Error testing login: {str(e)}")
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(test_login())