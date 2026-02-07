"""Database models for the DevOps SRE Platform."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Enum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DeploymentStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class IncidentSeverity(str, enum.Enum):
    SEV1 = "sev1"
    SEV2 = "sev2"
    SEV3 = "sev3"
    SEV4 = "sev4"


class IncidentStatus(str, enum.Enum):
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


class Deployment(Base):
    """Track deployment events across environments."""
    __tablename__ = "deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(255), nullable=False, index=True)
    environment = Column(String(50), nullable=False, index=True)
    version = Column(String(100), nullable=False)
    commit_sha = Column(String(40), nullable=False)
    status = Column(Enum(DeploymentStatus), default=DeploymentStatus.PENDING, index=True)
    deployed_by = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    rollback_of = Column(UUID(as_uuid=True), ForeignKey("deployments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    incidents = relationship("Incident", back_populates="caused_by_deployment")


class Incident(Base):
    """Track incidents and their lifecycle."""
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(IncidentSeverity), nullable=False, index=True)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.TRIGGERED, index=True)
    service_name = Column(String(255), nullable=False, index=True)
    environment = Column(String(50), nullable=False)
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    mttr_seconds = Column(Float, nullable=True)
    root_cause = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id"), nullable=True)
    on_call_engineer = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    caused_by_deployment = relationship("Deployment", back_populates="incidents")
    timeline = relationship("IncidentTimeline", back_populates="incident", order_by="IncidentTimeline.created_at")


class IncidentTimeline(Base):
    """Incident timeline events for postmortem."""
    __tablename__ = "incident_timeline"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    author = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="timeline")


class SLO(Base):
    """Service Level Objectives definition and tracking."""
    __tablename__ = "slos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sli_type = Column(String(50), nullable=False)  # availability, latency, error_rate
    target_percentage = Column(Float, nullable=False)  # e.g., 99.9
    window_days = Column(Integer, default=30)
    current_percentage = Column(Float, nullable=True)
    error_budget_remaining = Column(Float, nullable=True)
    is_breached = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
