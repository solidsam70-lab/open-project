from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class MemoryEntry(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    agent_id: Optional[str] = None
    user_id: Optional[str] = None
    memory_type: str = "conversation"
    key: str
    value: dict
    importance: float = 0.5
    context: dict = Field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class MemorySearchResult(BaseModel):
    id: str
    memory_type: str
    key: str
    value: dict
    importance: float
    context: dict
    created_at: datetime
    score: float = 0.0
