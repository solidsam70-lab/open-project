from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from jarvis.jarvis_core.governance.models import RiskLevel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalRequest(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    workflow_execution_id: Optional[str] = None
    agent_id: Optional[str] = None
    requested_by_user_id: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    action_type: str
    resource_system: str
    resource_type: str
    resource_id: Optional[str] = None
    proposed_payload: dict[str, Any] = Field(default_factory=dict)
    risk_level: RiskLevel
    reason: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    decision_note: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    expires_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    decided_by_user_id: Optional[str] = None


class ApprovalDecision(BaseModel):
    approval_id: str
    tenant_id: str
    decided_by_user_id: str
    decision: ApprovalStatus
    note: Optional[str] = None


class ApprovalQuery(BaseModel):
    tenant_id: str
    status: Optional[ApprovalStatus] = None
    assigned_to_user_id: Optional[str] = None
    workflow_execution_id: Optional[str] = None
    limit: int = 50
    offset: int = 0
