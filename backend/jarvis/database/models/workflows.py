from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from jarvis.database.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowDefinitionRecord(Base):
    __tablename__ = "workflow_definitions"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    agent_slug = Column(String(100), nullable=False, index=True)
    initial_state = Column(String(100), nullable=False)
    states = Column(JSONB, nullable=False)
    transitions = Column(JSONB, nullable=False)
    approval_points = Column(JSONB, nullable=False, default=list)
    input_schema = Column(JSONB, nullable=False, default=dict)
    output_schema = Column(JSONB, nullable=False, default=dict)
    metadata = Column(JSONB, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("ix_workflow_def_tenant_agent", "tenant_id", "agent_slug", "is_active"),
    )


class WorkflowInstanceRecord(Base):
    __tablename__ = "workflow_instances"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    definition_id = Column(String, nullable=False, index=True)
    definition_version = Column(Integer, nullable=False)
    current_state = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    input_data = Column(JSONB, nullable=False, default=dict)
    output_data = Column(JSONB, nullable=False, default=dict)
    context = Column(JSONB, nullable=False, default=dict)
    approval_id = Column(String, index=True)
    created_by_user_id = Column(String, index=True)
    agent_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_workflow_instance_queue", "tenant_id", "status", "current_state"),
    )


class WorkflowEventRecord(Base):
    __tablename__ = "workflow_events"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_instance_id = Column(String, nullable=False, index=True)
    from_state = Column(String(100))
    to_state = Column(String(100), nullable=False)
    trigger = Column(String(50), nullable=False)
    actor_user_id = Column(String, index=True)
    agent_id = Column(String, index=True)
    approval_id = Column(String, index=True)
    event_metadata = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    __table_args__ = (
        Index("ix_workflow_events_instance", "tenant_id", "workflow_instance_id", "created_at"),
    )
