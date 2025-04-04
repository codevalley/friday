#!/usr/bin/env python3
"""
Debug script for Friday API
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
    "name": "debuguser",
    "password": "password123",
    "tier": "free"
}


async def debug_api():
    """Debug the API by testing specific endpoints"""
    async with httpx.AsyncClient() as client:
        # Test root endpoint
        try:
            logger.info("Testing root endpoint...")
            response = await client.get(f"{BASE_URL}/")
            logger.info(f"Root response: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error testing root endpoint: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Test user creation
        try:
            logger.info("Testing user creation...")
            response = await client.post(f"{BASE_URL}/users/", json=TEST_USER)
            logger.info(f"User creation response: {response.status_code}")
            logger.info(f"User creation headers: {response.headers}")
            logger.info(f"User creation body: {response.text}")
        except Exception as e:
            logger.error(f"Error testing user creation: {str(e)}")
            logger.error(traceback.format_exc())
        
        # Test users list
        try:
            logger.info("Testing users list...")
            response = await client.get(f"{BASE_URL}/users/")
            logger.info(f"Users list response: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error testing users list: {str(e)}")
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(debug_api())