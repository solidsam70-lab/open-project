from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AuditEntry(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    user_id: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: dict = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: Optional[datetime] = None
