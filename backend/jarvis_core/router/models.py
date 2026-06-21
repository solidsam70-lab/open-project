from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Intent(BaseModel):
    id: Optional[str] = None
    name: str
    description: str
    agent_slug: str
    patterns: list[str] = Field(default_factory=list)
    priority: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None


class RouteMatch(BaseModel):
    intent: Intent
    agent_slug: str
    confidence: float
    query: str
    context: dict = Field(default_factory=dict)
    matched_pattern: Optional[str] = None
