from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class WorkflowStep(BaseModel):
    name: str
    step_type: str = "action"
    input_data: dict = Field(default_factory=dict)
    output_data: dict = Field(default_factory=dict)
    status: str = "pending"
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class ExecutionRequest(BaseModel):
    tenant_id: str
    agent_slug: str
    workflow_name: str
    input_data: dict = Field(default_factory=dict)
    context: dict = Field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class ExecutionResult(BaseModel):
    id: str
    tenant_id: str
    agent_slug: str
    workflow_name: str
    status: str
    output_data: dict = Field(default_factory=dict)
    steps: list[WorkflowStep] = Field(default_factory=list)
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
