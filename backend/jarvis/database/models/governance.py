from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Index
from sqlalchemy.dialects.postgresql import JSONB
from jarvis.database.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class GovernancePolicyRecord(Base):
    __tablename__ = "governance_policies"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    min_confidence_for_action = Column(Float, nullable=False, default=0.75)
    min_confidence_for_high_risk = Column(Float, nullable=False, default=0.90)
    require_sources_for_high_risk = Column(Boolean, nullable=False, default=True)
    require_approval_for_external_send = Column(Boolean, nullable=False, default=True)
    require_approval_for_financial_actions = Column(Boolean, nullable=False, default=True)
    require_approval_for_odoo_writes = Column(Boolean, nullable=False, default=True)
    allow_delete_actions = Column(Boolean, nullable=False, default=False)
    odoo_model_policies = Column(JSONB, nullable=False, default=dict)
    blocked_actions = Column(JSONB, nullable=False, default=list)
    metadata = Column(JSONB, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    __table_args__ = (
        Index("ix_governance_policy_tenant_active", "tenant_id", "is_active"),
    )
