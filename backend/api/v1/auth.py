import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.session import get_db
from jarvis.jarvis_core.auth import AuthService, LoginRequest, RegisterRequest, TokenResponse

logger = logging.getLogger("jarvis.api.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login/{tenant_slug}", response_model=TokenResponse)
async def login(tenant_slug: str, request: LoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        result = await auth_service.authenticate(tenant_slug, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/register/{tenant_slug}")
async def register(tenant_slug: str, request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        result = await auth_service.register_user(
            tenant_slug=tenant_slug,
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )
        return {"message": "User registered", "user_id": result.user_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
