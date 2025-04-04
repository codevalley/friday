#!/usr/bin/env python3
"""
Debug script for password hashing and verification
"""
import asyncio
import logging
import bcrypt

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def hash_password(password: str) -> str:
    """Hash a password for secure storage"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode("utf-8")


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)


async def main():
    """Test password hashing and verification"""
    password = "password123"
    
    # Hash the password
    logger.info(f"Hashing password: {password}")
    hashed = await hash_password(password)
    logger.info(f"Hashed password: {hashed}")
    
    # Verify the password
    result = await verify_password(password, hashed)
    logger.info(f"Verification result for correct password: {result}")
    
    # Verify wrong password
    wrong_result = await verify_password("wrongpassword", hashed)
    logger.info(f"Verification result for wrong password: {wrong_result}")
    
    # Log hash details
    logger.info(f"Hashed password length: {len(hashed)}")
    logger.info(f"Hashed password type: {type(hashed)}")
    logger.info(f"Hashed password first few chars: {hashed[:10]}")


if __name__ == "__main__":
    asyncio.run(main())