from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class AgentDefinition(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    name: str
    slug: str
    role: str
    goal: str
    model: str = "gpt-4o"
    temperature: float = 0.3
    status: AgentStatus = AgentStatus.DRAFT
    config_path: Optional[str] = None
    kpis: list[dict] = Field(default_factory=list)
    knowledge_sources: list[dict] = Field(default_factory=list)
    memory_sources: list[dict] = Field(default_factory=list)
    tools: list[dict] = Field(default_factory=list)
    workflows: list[dict] = Field(default_factory=list)
    input_schema: dict = Field(default_factory=dict)
    output_schema: dict = Field(default_factory=dict)
    escalation_rules: list[dict] = Field(default_factory=list)
    agent_metadata: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        use_enum_values = True
