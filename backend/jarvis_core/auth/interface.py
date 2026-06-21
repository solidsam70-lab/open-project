from abc import ABC, abstractmethod
from typing import Optional
from jarvis.jarvis_core.auth.models import TokenResponse, LoginRequest, AuthContext


class IAuthService(ABC):

    @abstractmethod
    async def authenticate(self, tenant_slug: str, request: LoginRequest) -> TokenResponse:
        ...

    @abstractmethod
    async def validate_token(self, token: str) -> Optional[AuthContext]:
        ...

    @abstractmethod
    async def register_user(self, tenant_slug: str, email: str, password: str, display_name: str) -> AuthContext:
        ...
