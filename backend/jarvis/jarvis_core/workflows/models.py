from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowRunStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class TransitionTrigger(str, Enum):
    SYSTEM = "system"
    USER = "user"
    AGENT = "agent"
    CONNECTOR = "connector"
    APPROVAL = "approval"
    SCHEDULE = "schedule"


class WorkflowState(BaseModel):
    name: str
    description: Optional[str] = None
    terminal: bool = False
    requires_approval: bool = False


class WorkflowTransition(BaseModel):
    from_state: str
    to_state: str
    trigger: TransitionTrigger = TransitionTrigger.SYSTEM
    guard: Optional[str] = None
    description: Optional[str] = None


class WorkflowDefinition(BaseModel):
    id: str
    tenant_id: str
    name: str
    version: int = 1
    agent_slug: str
    initial_state: str
    states: list[WorkflowState]
    transitions: list[WorkflowTransition]
    approval_points: list[str] = Field(default_factory=list)
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True


class WorkflowInstance(BaseModel):
    id: str
    tenant_id: str
    definition_id: str
    definition_version: int
    current_state: str
    status: WorkflowRunStatus = WorkflowRunStatus.CREATED
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    approval_id: Optional[str] = None
    created_by_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    completed_at: Optional[datetime] = None


class WorkflowEvent(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    workflow_instance_id: str
    from_state: Optional[str] = None
    to_state: str
    trigger: TransitionTrigger
    actor_user_id: Optional[str] = None
    agent_id: Optional[str] = None
    approval_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)
