"""SLO (Service Level Objective) tracking endpoints."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.models import SLO
from app.schemas.schemas import SLOCreate, SLOResponse

router = APIRouter()


@router.post("/slos", response_model=SLOResponse, status_code=201)
async def create_slo(
    slo: SLOCreate,
    db: AsyncSession = Depends(get_db),
):
    """Define a new Service Level Objective."""
    db_slo = SLO(
        service_name=slo.service_name,
        name=slo.name,
        description=slo.description,
        sli_type=slo.sli_type,
        target_percentage=slo.target_percentage,
        window_days=slo.window_days,
        current_percentage=slo.target_percentage,
        error_budget_remaining=100.0,
    )
    db.add(db_slo)
    await db.flush()
    await db.refresh(db_slo)
    return db_slo


@router.get("/slos", response_model=List[SLOResponse])
async def list_slos(
    service_name: Optional[str] = Query(None),
    breached: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List all SLOs with optional filters."""
    query = select(SLO).order_by(SLO.service_name)

    if service_name:
        query = query.where(SLO.service_name == service_name)
    if breached is not None:
        query = query.where(SLO.is_breached == breached)

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/slos/{slo_id}", response_model=SLOResponse)
async def get_slo(slo_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a specific SLO by ID."""
    result = await db.execute(select(SLO).where(SLO.id == slo_id))
    slo = result.scalar_one_or_none()
    if not slo:
        raise HTTPException(status_code=404, detail="SLO not found")
    return slo


@router.patch("/slos/{slo_id}", response_model=SLOResponse)
async def update_slo_status(
    slo_id: UUID,
    current_percentage: float,
    db: AsyncSession = Depends(get_db),
):
    """Update current SLI measurement for an SLO."""
    result = await db.execute(select(SLO).where(SLO.id == slo_id))
    slo = result.scalar_one_or_none()
    if not slo:
        raise HTTPException(status_code=404, detail="SLO not found")

    slo.current_percentage = current_percentage

    # Calculate error budget remaining
    allowed_downtime = 100.0 - slo.target_percentage  # e.g., 0.1 for 99.9%
    actual_downtime = 100.0 - current_percentage
    if allowed_downtime > 0:
        slo.error_budget_remaining = max(
            0, round(((allowed_downtime - actual_downtime) / allowed_downtime) * 100, 2)
        )
    else:
        slo.error_budget_remaining = 0

    slo.is_breached = current_percentage < slo.target_percentage

    await db.flush()
    await db.refresh(slo)
    return slo
