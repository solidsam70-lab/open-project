from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Union
from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ActionMode(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    SEND = "send"
    CONFIGURE = "configure"
    SUBMIT = "submit"


class DecisionStatus(str, Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    BLOCK = "block"
    ESCALATE = "escalate"
    DRY_RUN_ONLY = "dry_run_only"


class ResourceRef(BaseModel):
    system: str = Field(..., examples=["odoo", "gmail", "whatsapp", "knowledge"])
    resource_type: str = Field(..., examples=["crm.lead", "account.move", "message"])
    resource_id: Optional[str] = None
    tenant_id: str


class ActorContext(BaseModel):
    tenant_id: str
    user_id: Optional[str] = None
    role: str = "member"
    permissions: list[str] = Field(default_factory=list)
    agent_id: Optional[str] = None
    workflow_execution_id: Optional[str] = None
    channel: str = "internal"


class ActionContext(BaseModel):
    action: str
    mode: ActionMode
    resource: ResourceRef
    payload: dict[str, Any] = Field(default_factory=dict)
    confidence: Optional[float] = None
    sources_used: list[str] = Field(default_factory=list)
    external_recipient: Optional[str] = None
    idempotency_key: Optional[str] = None
    dry_run: bool = False


class OdooModelPolicy(BaseModel):
    model: str
    read: bool = True
    create: Union[str, bool] = "approval_required"
    update: Union[str, bool] = "approval_required"
    delete: bool = False
    confirm: Union[str, bool] = "approval_required"
    post: Union[str, bool] = "approval_required"
    submit: Union[str, bool] = "approval_required"


class GovernancePolicy(BaseModel):
    tenant_id: str
    min_confidence_for_action: float = 0.75
    min_confidence_for_high_risk: float = 0.90
    require_sources_for_high_risk: bool = True
    require_approval_for_external_send: bool = True
    require_approval_for_financial_actions: bool = True
    require_approval_for_odoo_writes: bool = True
    allow_delete_actions: bool = False
    odoo_model_policies: dict[str, OdooModelPolicy] = Field(default_factory=dict)
    blocked_actions: list[str] = Field(default_factory=list)


class GovernanceDecision(BaseModel):
    status: DecisionStatus
    risk_level: RiskLevel
    reason: str
    approval_required: bool = False
    approval_reason: Optional[str] = None
    blocked: bool = False
    dry_run_required: bool = False
    escalation_required: bool = False
    missing_requirements: list[str] = Field(default_factory=list)
    audit_tags: list[str] = Field(default_factory=list)
