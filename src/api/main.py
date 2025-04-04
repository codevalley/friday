import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import note_routes, user_routes
from src.config import get_settings
from src.infrastructure.persistence.sqlalchemy.models import Base
from src.infrastructure.persistence.sqlalchemy import async_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()


# Create FastAPI app
app = FastAPI(
    title="Clean Architecture API",
    description="An API service built with Clean Architecture principles",
    version="0.1.0",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(user_routes.router)
app.include_router(note_routes.router)


# Startup event
@app.on_event("startup")
async def startup():
    # Create database tables
    async with async_engine.begin() as conn:
        if settings.create_tables:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Application startup complete")


# Shutdown event
@app.on_event("shutdown")
async def shutdown():
    logger.info("Application shutdown")


# Root endpoint
@app.get("/", tags=["status"])
async def root():
    """API status endpoint"""
    return {"status": "ok", "version": app.version}


# Run the API with uvicorn if executed directly
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )