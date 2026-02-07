"""Deployment tracking API endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import Deployment, DeploymentStatus
from app.schemas.schemas import DeploymentCreate, DeploymentUpdate, DeploymentResponse
from app.core.middleware import DEPLOYMENT_COUNT

router = APIRouter()


@router.post("/deployments", response_model=DeploymentResponse, status_code=201)
async def create_deployment(
    deployment: DeploymentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new deployment event."""
    db_deployment = Deployment(
        service_name=deployment.service_name,
        environment=deployment.environment,
        version=deployment.version,
        commit_sha=deployment.commit_sha,
        deployed_by=deployment.deployed_by,
        description=deployment.description,
        status=DeploymentStatus.PENDING,
    )
    db.add(db_deployment)
    await db.flush()
    await db.refresh(db_deployment)

    DEPLOYMENT_COUNT.labels(
        environment=deployment.environment, status="pending"
    ).inc()

    return db_deployment


@router.get("/deployments", response_model=List[DeploymentResponse])
async def list_deployments(
    service_name: Optional[str] = Query(None),
    environment: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List deployments with optional filters."""
    query = select(Deployment).order_by(Deployment.created_at.desc())

    if service_name:
        query = query.where(Deployment.service_name == service_name)
    if environment:
        query = query.where(Deployment.environment == environment)
    if status:
        query = query.where(Deployment.status == status)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific deployment by ID."""
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment


@router.patch("/deployments/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_id: UUID,
    update: DeploymentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update deployment status (e.g., mark as success/failed)."""
    result = await db.execute(
        select(Deployment).where(Deployment.id == deployment_id)
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployment.status = DeploymentStatus(update.status)
    if update.duration_seconds:
        deployment.duration_seconds = update.duration_seconds
    deployment.updated_at = datetime.utcnow()

    await db.flush()
    await db.refresh(deployment)

    DEPLOYMENT_COUNT.labels(
        environment=deployment.environment, status=update.status
    ).inc()

    return deployment


@router.get("/deployments/stats/summary")
async def deployment_stats(
    environment: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    """Get deployment statistics for DORA metrics."""
    since = datetime.utcnow() - timedelta(days=days)
    base_query = select(Deployment).where(Deployment.created_at >= since)

    if environment:
        base_query = base_query.where(Deployment.environment == environment)

    result = await db.execute(base_query)
    deployments = result.scalars().all()

    total = len(deployments)
    successful = sum(1 for d in deployments if d.status == DeploymentStatus.SUCCESS)
    failed = sum(1 for d in deployments if d.status == DeploymentStatus.FAILED)
    rolled_back = sum(1 for d in deployments if d.status == DeploymentStatus.ROLLED_BACK)

    avg_duration = 0
    durations = [d.duration_seconds for d in deployments if d.duration_seconds]
    if durations:
        avg_duration = sum(durations) / len(durations)

    return {
        "period_days": days,
        "total_deployments": total,
        "successful": successful,
        "failed": failed,
        "rolled_back": rolled_back,
        "success_rate": round((successful / total * 100) if total > 0 else 0, 2),
        "change_failure_rate": round(((failed + rolled_back) / total * 100) if total > 0 else 0, 2),
        "deployment_frequency_per_day": round(total / days, 2),
        "avg_duration_seconds": round(avg_duration, 2),
    }
