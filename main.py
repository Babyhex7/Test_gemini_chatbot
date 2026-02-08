"""
EduMindAI - Reflective Emotional Companion Chatbot
Main Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from database.connection import engine
from database.models.base import Base
from api.endpoints.conversation import router as conversation_router
from api.endpoints.health import router as health_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME}...")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")
    
    # Pre-load knowledge base
    try:
        from core.knowledge.loader import get_knowledge_loader
        loader = get_knowledge_loader()
        loader.load_all()
        logger.info("Knowledge base loaded")
    except Exception as e:
        logger.error(f"Failed to load knowledge base: {e}")
    
    logger.info(f"{settings.APP_NAME} started successfully!")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}...")
    await engine.dispose()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    EduMindAI - Reflective Emotional Companion Chatbot for School Wellness
    
    A 4-phase conversation flow chatbot that helps students reflect on their emotions
    using the Gloria Willcox Feeling Wheel and Mental Health Continuum Model (MHCM).
    
    ## Features
    - Emotion detection using Feeling Wheel
    - Guided reflection with 5 questions
    - MHCM-based narrative generation
    - Practical coping tips
    
    ## Flow
    1. **BERCERITA** - User shares their story
    2. **REFLEKSI_RINGAN** - 5 reflection questions
    3. **NARASI_REFLEKTIF** - AI-generated reflective narrative
    4. **TIPS_CLOSING** - Practical tips and closing
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(conversation_router)


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "description": "Reflective Emotional Companion Chatbot for School Wellness",
        "docs": "/docs" if settings.DEBUG else "Disabled in production",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )
