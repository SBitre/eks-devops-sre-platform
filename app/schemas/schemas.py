"""Pydantic schemas for API request/response validation."""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# ─── Deployments ────────────────────────────────────────────

class DeploymentCreate(BaseModel):
    service_name: str = Field(..., example="payment-service")
    environment: str = Field(..., example="production")
    version: str = Field(..., example="v2.3.1")
    commit_sha: str = Field(..., example="a1b2c3d4e5f6")
    deployed_by: str = Field(..., example="github-actions")
    description: Optional[str] = None

class DeploymentUpdate(BaseModel):
    status: str = Field(..., example="success")
    duration_seconds: Optional[float] = None

class DeploymentResponse(BaseModel):
    id: UUID
    service_name: str
    environment: str
    version: str
    commit_sha: str
    status: str
    deployed_by: str
    description: Optional[str]
    duration_seconds: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Incidents ──────────────────────────────────────────────

class IncidentCreate(BaseModel):
    title: str = Field(..., example="High error rate on payment-service")
    description: Optional[str] = None
    severity: str = Field(..., example="sev2")
    service_name: str = Field(..., example="payment-service")
    environment: str = Field(..., example="production")
    deployment_id: Optional[UUID] = None
    on_call_engineer: Optional[str] = None

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    root_cause: Optional[str] = None
    action_items: Optional[str] = None
    on_call_engineer: Optional[str] = None

class TimelineEventCreate(BaseModel):
    event_type: str = Field(..., example="investigation_started")
    description: str = Field(..., example="Checking application logs for errors")
    author: str = Field(..., example="oncall-engineer")

class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    severity: str
    status: str
    service_name: str
    environment: str
    triggered_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    mttr_seconds: Optional[float]
    root_cause: Optional[str]
    on_call_engineer: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ─── SLOs ───────────────────────────────────────────────────

class SLOCreate(BaseModel):
    service_name: str = Field(..., example="payment-service")
    name: str = Field(..., example="Availability SLO")
    description: Optional[str] = None
    sli_type: str = Field(..., example="availability")
    target_percentage: float = Field(..., example=99.9)
    window_days: int = Field(default=30)

class SLOResponse(BaseModel):
    id: UUID
    service_name: str
    name: str
    sli_type: str
    target_percentage: float
    current_percentage: Optional[float]
    error_budget_remaining: Optional[float]
    is_breached: bool
    window_days: int
    created_at: datetime

    class Config:
        from_attributes = True


# ─── DORA Metrics ───────────────────────────────────────────

class DORAMetrics(BaseModel):
    """DORA (DevOps Research and Assessment) four key metrics."""
    deployment_frequency: float = Field(..., description="Deployments per day")
    lead_time_for_changes_hours: float = Field(..., description="Avg hours from commit to deploy")
    change_failure_rate: float = Field(..., description="% of deployments causing incidents")
    mttr_hours: float = Field(..., description="Mean Time to Recovery in hours")
    period_days: int
    environment: str
    rating: str = Field(..., description="Elite / High / Medium / Low")


class PlatformHealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    database: str
    uptime_seconds: float
    active_incidents: int
    deployments_today: int
