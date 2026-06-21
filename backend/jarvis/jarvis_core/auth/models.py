from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    display_name: str
    tenant_slug: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    user_id: str
    tenant_id: str
    role: str


class AuthContext(BaseModel):
    user_id: str
    tenant_id: str
    tenant_slug: str
    email: str
    role: str
    permissions: list[str] = Field(default_factory=list)


class TenantAuth(BaseModel):
    tenant_id: str
    tenant_slug: str
    api_key: Optional[str] = None
    features: list[str] = Field(default_factory=list)
