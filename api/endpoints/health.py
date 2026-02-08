"""
Health Check API Endpoints
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from database.connection import get_db
from app.config import settings

router = APIRouter(prefix="/api", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "1.0.0"
    database: str = "unknown"
    gemini: str = "unknown"


class SystemInfoResponse(BaseModel):
    """System info response"""
    app_name: str
    version: str
    environment: str
    debug_mode: bool
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint
    
    Checks the status of the API, database, and Gemini API connection.
    """
    db_status = "unknown"
    gemini_status = "unknown"
    
    # Check database
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Gemini (just check if API key is set)
    try:
        if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 10:
            gemini_status = "configured"
        else:
            gemini_status = "not_configured"
    except Exception:
        gemini_status = "error"
    
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        database=db_status,
        gemini=gemini_status
    )


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe
    
    Simple check to verify the API is running.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe
    
    Checks if the API is ready to accept requests (database connection, etc.)
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "reason": str(e)
        }


@router.get("/info", response_model=SystemInfoResponse)
async def system_info():
    """
    Get system info
    
    Returns basic information about the application.
    """
    return SystemInfoResponse(
        app_name=settings.APP_NAME,
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        debug_mode=settings.DEBUG,
        timestamp=datetime.utcnow().isoformat()
    )
