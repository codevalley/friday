import os
from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # API settings
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite+aiosqlite:///./app.db"
    create_tables: bool = True
    
    # Redis settings
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT settings
    jwt_secret_key: str = "dev_secret_key"
    jwt_token_expires_minutes: int = 30
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance"""
    return Settings()