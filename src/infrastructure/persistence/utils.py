"""Database utility functions"""
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql import text


async def get_db_features(engine: AsyncEngine) -> Dict[str, bool]:
    """
    Detect database features and capabilities.
    
    Args:
        engine: SQLAlchemy async engine instance
        
    Returns:
        Dictionary of feature flags
    """
    features = {
        "vector_search": False,
        "vector_search_type": "none"
    }
    
    # Check if using PostgreSQL
    dialect = engine.dialect.name
    if dialect == "postgresql":
        try:
            # Test if pgvector is available
            import pgvector
            
            # Try to create a vector type to verify extension is installed
            async with engine.begin() as conn:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    features["vector_search"] = True
                    features["vector_search_type"] = "pgvector"
                except Exception:
                    # Extension couldn't be created
                    pass
        except ImportError:
            # pgvector not installed
            pass
    
    return features