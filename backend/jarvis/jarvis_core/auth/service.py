import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.models import User as UserDB, Tenant as TenantDB
from jarvis.jarvis_core.auth.models import (
    TokenResponse, LoginRequest, RegisterRequest, AuthContext
)
from jarvis.jarvis_core.auth.interface import IAuthService

logger = logging.getLogger("jarvis.auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JARVIS_JWT_SECRET", "jarvis-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JARVIS_TOKEN_EXPIRE_MINUTES", "1440"))


class AuthService(IAuthService):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, tenant_slug: str, request: LoginRequest) -> TokenResponse:
        tenant = await self._get_tenant(tenant_slug)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_slug}")

        user = await self._get_user(tenant.id, request.email)
        if not user or not pwd_context.verify(request.password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        access_token = self._create_token(user.id, tenant.id, tenant_slug, user.role)

        return TokenResponse(
            access_token=access_token,
            user_id=user.id,
            tenant_id=tenant.id,
            role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        )

    async def validate_token(self, token: str) -> Optional[AuthContext]:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            tenant_id = payload.get("tenant_id")
            tenant_slug = payload.get("tenant_slug")
            email = payload.get("email")
            role = payload.get("role")

            if not all([user_id, tenant_id]):
                return None

            return AuthContext(
                user_id=user_id,
                tenant_id=tenant_id,
                tenant_slug=tenant_slug or "",
                email=email or "",
                role=role or "member",
            )
        except JWTError:
            logger.warning("Invalid token")
            return None

    async def register_user(
        self, tenant_slug: str, email: str, password: str, display_name: str
    ) -> AuthContext:
        tenant = await self._get_tenant(tenant_slug)
        if not tenant:
            raise ValueError(f"Tenant not found: {tenant_slug}")

        existing = await self._get_user(tenant.id, email)
        if existing:
            raise ValueError(f"User already exists: {email}")

        user = UserDB(
            tenant_id=tenant.id,
            email=email,
            password_hash=pwd_context.hash(password),
            display_name=display_name,
        )
        self.db.add(user)
        await self.db.flush()

        logger.info("Registered user: %s for tenant: %s", email, tenant_slug)

        return AuthContext(
            user_id=user.id,
            tenant_id=tenant.id,
            tenant_slug=tenant_slug,
            email=email,
            role="member",
        )

    async def _get_tenant(self, slug: str) -> Optional[TenantDB]:
        result = await self.db.execute(
            select(TenantDB).where(TenantDB.slug == slug)
        )
        return result.scalar_one_or_none()

    async def _get_user(self, tenant_id: str, email: str) -> Optional[UserDB]:
        result = await self.db.execute(
            select(UserDB).where(
                UserDB.tenant_id == tenant_id,
                UserDB.email == email,
            )
        )
        return result.scalar_one_or_none()

    def _create_token(self, user_id: str, tenant_id: str, tenant_slug: str, role: str) -> str:
        expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        claims = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "tenant_slug": tenant_slug,
            "role": role.value if hasattr(role, 'value') else str(role),
            "exp": expires,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(claims, JWT_SECRET, algorithm=JWT_ALGORITHM)
