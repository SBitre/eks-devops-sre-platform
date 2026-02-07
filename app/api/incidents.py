"""Incident management API endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.models.models import Incident, IncidentTimeline, IncidentStatus, IncidentSeverity
from app.schemas.schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, TimelineEventCreate
)
from app.core.middleware import INCIDENT_COUNT, MTTR_HISTOGRAM

router = APIRouter()


@router.post("/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(
    incident: IncidentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new incident."""
    db_incident = Incident(
        title=incident.title,
        description=incident.description,
        severity=IncidentSeverity(incident.severity),
        status=IncidentStatus.TRIGGERED,
        service_name=incident.service_name,
        environment=incident.environment,
        deployment_id=incident.deployment_id,
        on_call_engineer=incident.on_call_engineer,
        triggered_at=datetime.utcnow(),
    )
    db.add(db_incident)
    await db.flush()
    await db.refresh(db_incident)

    INCIDENT_COUNT.labels(severity=incident.severity, status="triggered").inc()
    return db_incident


@router.get("/incidents", response_model=List[IncidentResponse])
async def list_incidents(
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    service_name: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List incidents with optional filters."""
    query = select(Incident).order_by(Incident.triggered_at.desc())

    if severity:
        query = query.where(Incident.severity == severity)
    if status:
        query = query.where(Incident.status == status)
    if service_name:
        query = query.where(Incident.service_name == service_name)

    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific incident by ID."""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    update: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update incident status and details."""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if update.status:
        new_status = IncidentStatus(update.status)
        incident.status = new_status

        if new_status == IncidentStatus.ACKNOWLEDGED:
            incident.acknowledged_at = datetime.utcnow()
        elif new_status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.utcnow()
            if incident.triggered_at:
                mttr = (incident.resolved_at - incident.triggered_at).total_seconds()
                incident.mttr_seconds = mttr
                MTTR_HISTOGRAM.labels(severity=incident.severity.value).observe(mttr)

        INCIDENT_COUNT.labels(
            severity=incident.severity.value, status=update.status
        ).inc()

    if update.root_cause:
        incident.root_cause = update.root_cause
    if update.action_items:
        incident.action_items = update.action_items
    if update.on_call_engineer:
        incident.on_call_engineer = update.on_call_engineer

    incident.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(incident)
    return incident


@router.post("/incidents/{incident_id}/timeline", status_code=201)
async def add_timeline_event(
    incident_id: UUID,
    event: TimelineEventCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a timeline event to an incident (for postmortem)."""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Incident not found")

    timeline_event = IncidentTimeline(
        incident_id=incident_id,
        event_type=event.event_type,
        description=event.description,
        author=event.author,
    )
    db.add(timeline_event)
    await db.flush()
    await db.refresh(timeline_event)

    return {
        "id": str(timeline_event.id),
        "event_type": timeline_event.event_type,
        "description": timeline_event.description,
        "author": timeline_event.author,
        "created_at": timeline_event.created_at,
    }
