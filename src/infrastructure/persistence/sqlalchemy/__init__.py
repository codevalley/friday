from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import get_settings

settings = get_settings()

# Create async engine and session factory
async_engine = create_async_engine(
    settings.database_url, 
    echo=settings.debug,
    future=True
)

async_session_factory = sessionmaker(
    async_engine, 
    expire_on_commit=False, 
    class_=AsyncSession
)


async def get_db_session():
    """Get a new database session"""
    async with async_session_factory() as session:
        try:
            yield session
            # Make sure to commit any pending transactions
            await session.commit()
        except Exception:
            # Rollback on error
            await session.rollback()
            raise
        finally:
            await session.close()
