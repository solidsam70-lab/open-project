from __future__ import annotations

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from jarvis.jarvis_core.governance.models import ActionMode, RiskLevel


class ConnectorStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    UNCONFIGURED = "unconfigured"


class ConnectorAction(BaseModel):
    tenant_id: str
    connector_type: str
    action: str
    mode: ActionMode
    resource_type: str
    resource_id: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = False
    idempotency_key: Optional[str] = None


class ConnectorResult(BaseModel):
    success: bool
    connector_type: str
    action: str
    mode: ActionMode
    dry_run: bool = False
    data: dict[str, Any] = Field(default_factory=dict)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    external_request_id: Optional[str] = None
    audit_metadata: dict[str, Any] = Field(default_factory=dict)


class ConnectorHealth(BaseModel):
    connector_type: str
    status: ConnectorStatus
    latency_ms: Optional[int] = None
    details: dict[str, Any] = Field(default_factory=dict)


class ConnectorCapability(BaseModel):
    action: str
    mode: ActionMode
    resource_type: str
    risk_level: RiskLevel = RiskLevel.LOW
    approval_required: bool = False
    supports_dry_run: bool = True
