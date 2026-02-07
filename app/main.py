"""
DevOps Metrics & Incident Management Platform
A production-grade FastAPI application for tracking deployments,
incidents, SLOs, and engineering metrics.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api import deployments, incidents, health, slos, metrics
from app.core.config import settings
from app.core.middleware import RequestMetricsMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-grade DevOps Metrics & Incident Management Platform",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Prometheus metrics middleware
app.add_middleware(RequestMetricsMiddleware)

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# API Routes
app.include_router(health.router, tags=["Health"])
app.include_router(deployments.router, prefix="/api/v1", tags=["Deployments"])
app.include_router(incidents.router, prefix="/api/v1", tags=["Incidents"])
app.include_router(slos.router, prefix="/api/v1", tags=["SLOs"])
app.include_router(metrics.router, prefix="/api/v1", tags=["Metrics"])


@app.on_event("startup")
async def startup_event():
    """Initialize database connections and background tasks."""
    from app.core.database import init_db
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown."""
    from app.core.database import close_db
    await close_db()
