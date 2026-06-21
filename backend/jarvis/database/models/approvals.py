from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from jarvis.database.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalRecord(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    workflow_execution_id = Column(String, index=True)
    agent_id = Column(String, index=True)
    requested_by_user_id = Column(String, index=True)
    assigned_to_user_id = Column(String, index=True)
    action_type = Column(String(100), nullable=False)
    resource_system = Column(String(50), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String)
    proposed_payload = Column(JSONB, nullable=False, default=dict)
    risk_level = Column(String(20), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="pending", index=True)
    decision_note = Column(Text)
    decided_by_user_id = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    expires_at = Column(DateTime(timezone=True))
    decided_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_approvals_queue", "tenant_id", "status", "assigned_to_user_id"),
        Index("ix_approvals_workflow", "tenant_id", "workflow_execution_id"),
    )
