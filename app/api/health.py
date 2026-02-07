"""Health check endpoints for Kubernetes probes."""

import time
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()

START_TIME = time.time()


@router.get("/healthz", summary="Liveness probe")
async def liveness():
    """Kubernetes liveness probe - checks if the app is running."""
    return {"status": "alive"}


@router.get("/readyz", summary="Readiness probe")
async def readiness(db: AsyncSession = Depends(get_db)):
    """Kubernetes readiness probe - checks if the app can serve traffic."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ready" if db_status == "connected" else "not_ready",
        "database": db_status,
    }


@router.get("/health", summary="Detailed health check")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check with system information."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "uptime_seconds": round(time.time() - START_TIME, 2),
    }
