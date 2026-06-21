import logging
from typing import Optional

from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.session import get_db
from jarvis.jarvis_core.auth import AuthService, AuthContext
from jarvis.jarvis_core.registry import AgentRegistryService
from jarvis.jarvis_core.router import IntentRouter
from jarvis.jarvis_core.execution import ExecutionEngine
from jarvis.jarvis_core.memory import MemoryService
from jarvis.jarvis_core.knowledge import KnowledgeService
from jarvis.jarvis_core.audit import AuditService
from jarvis.connectors.base import ConnectorBase

logger = logging.getLogger("jarvis.api")


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
        )

    auth_service = AuthService(db)
    auth_context = await auth_service.validate_token(token)
    if not auth_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return auth_context


async def get_tenant_id(
    current_user: AuthContext = Depends(get_current_user),
) -> str:
    return current_user.tenant_id


def get_agent_registry(db: AsyncSession = Depends(get_db)) -> AgentRegistryService:
    return AgentRegistryService(db)


def get_intent_router() -> IntentRouter:
    return IntentRouter()


def get_execution_engine(
    db: AsyncSession = Depends(get_db),
    registry: AgentRegistryService = Depends(get_agent_registry),
    router: IntentRouter = Depends(get_intent_router),
    memory: MemoryService = Depends(lambda db: MemoryService(db)),
    knowledge: KnowledgeService = Depends(lambda db: KnowledgeService(db)),
) -> ExecutionEngine:
    return ExecutionEngine(
        db=db,
        agent_registry=registry,
        router=router,
        memory=memory,
        knowledge=knowledge,
        connectors={},
    )


def get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    return MemoryService(db)


def get_knowledge_service(db: AsyncSession = Depends(get_db)) -> KnowledgeService:
    return KnowledgeService(db)


def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    return AuditService(db)


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)
