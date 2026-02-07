"""DORA Metrics and engineering metrics endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import Deployment, Incident, DeploymentStatus, IncidentStatus
from app.schemas.schemas import DORAMetrics

router = APIRouter()


def _rate_dora(freq: float, lead_time: float, cfr: float, mttr: float) -> str:
    """Rate team performance based on DORA metrics."""
    score = 0
    if freq >= 1:
        score += 1  # daily or more
    if lead_time < 24:
        score += 1  # less than a day
    if cfr < 15:
        score += 1  # less than 15%
    if mttr < 1:
        score += 1  # less than 1 hour

    if score >= 4:
        return "Elite"
    elif score >= 3:
        return "High"
    elif score >= 2:
        return "Medium"
    return "Low"


@router.get("/metrics/dora", response_model=DORAMetrics)
async def get_dora_metrics(
    environment: str = Query("production"),
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    """
    Calculate DORA (DevOps Research and Assessment) four key metrics:
    1. Deployment Frequency
    2. Lead Time for Changes
    3. Change Failure Rate
    4. Mean Time to Recovery (MTTR)
    """
    since = datetime.utcnow() - timedelta(days=days)

    # Fetch deployments
    dep_result = await db.execute(
        select(Deployment)
        .where(Deployment.created_at >= since)
        .where(Deployment.environment == environment)
    )
    deployments = dep_result.scalars().all()

    # Fetch resolved incidents
    inc_result = await db.execute(
        select(Incident)
        .where(Incident.triggered_at >= since)
        .where(Incident.environment == environment)
    )
    incidents = inc_result.scalars().all()

    total_deps = len(deployments)
    failed_deps = sum(
        1 for d in deployments
        if d.status in (DeploymentStatus.FAILED, DeploymentStatus.ROLLED_BACK)
    )

    # Deployment Frequency (per day)
    deployment_frequency = total_deps / days if days > 0 else 0

    # Lead Time for Changes (avg deployment duration in hours)
    durations = [d.duration_seconds for d in deployments if d.duration_seconds]
    lead_time_hours = (sum(durations) / len(durations) / 3600) if durations else 0

    # Change Failure Rate
    cfr = (failed_deps / total_deps * 100) if total_deps > 0 else 0

    # MTTR (Mean Time to Recovery in hours)
    resolved = [i for i in incidents if i.mttr_seconds is not None]
    mttr_hours = (
        sum(i.mttr_seconds for i in resolved) / len(resolved) / 3600
        if resolved else 0
    )

    rating = _rate_dora(deployment_frequency, lead_time_hours, cfr, mttr_hours)

    return DORAMetrics(
        deployment_frequency=round(deployment_frequency, 2),
        lead_time_for_changes_hours=round(lead_time_hours, 2),
        change_failure_rate=round(cfr, 2),
        mttr_hours=round(mttr_hours, 2),
        period_days=days,
        environment=environment,
        rating=rating,
    )


@router.get("/metrics/summary")
async def platform_summary(db: AsyncSession = Depends(get_db)):
    """Get a high-level platform summary."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Active incidents
    active_result = await db.execute(
        select(Incident).where(
            Incident.status.notin_([IncidentStatus.RESOLVED, IncidentStatus.MITIGATED])
        )
    )
    active_incidents = len(active_result.scalars().all())

    # Today's deployments
    dep_result = await db.execute(
        select(Deployment).where(Deployment.created_at >= today)
    )
    todays_deployments = len(dep_result.scalars().all())

    return {
        "active_incidents": active_incidents,
        "deployments_today": todays_deployments,
        "timestamp": datetime.utcnow().isoformat(),
    }
