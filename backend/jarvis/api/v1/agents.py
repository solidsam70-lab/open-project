import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.session import get_db
from jarvis.jarvis_core.registry import AgentDefinition, AgentRegistryService
from jarvis.jarvis_core.router import IntentRouter
from jarvis.jarvis_core.execution import ExecutionRequest, ExecutionEngine
from jarvis.api.dependencies import (
    get_current_user, get_tenant_id,
    get_agent_registry, get_execution_engine,
)
from jarvis.jarvis_core.auth import AuthContext

logger = logging.getLogger("jarvis.api.agents")
router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/register", response_model=AgentDefinition)
async def register_agent(
    agent: AgentDefinition,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    registry = AgentRegistryService(db)
    agent.tenant_id = tenant_id
    result = await registry.register(agent)
    return result


@router.get("/", response_model=list[AgentDefinition])
async def list_agents(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    registry = AgentRegistryService(db)
    agents = await registry.list(tenant_id, status)
    return agents


@router.get("/{agent_id}", response_model=AgentDefinition)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    registry = AgentRegistryService(db)
    agent = await registry.get(agent_id)
    if not agent or agent.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.get("/slug/{slug}", response_model=AgentDefinition)
async def get_agent_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    registry = AgentRegistryService(db)
    agent = await registry.get_by_slug(tenant_id, slug)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentDefinition)
async def update_agent(
    agent_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    registry = AgentRegistryService(db)
    existing = await registry.get(agent_id)
    if not existing or existing.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    result = await registry.update(agent_id, updates)
    return result


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    registry = AgentRegistryService(db)
    existing = await registry.get(agent_id)
    if not existing or existing.tenant_id != tenant_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    await registry.delete(agent_id)


@router.post("/load-config")
async def load_agent_config(
    config_path: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    registry = AgentRegistryService(db)
    try:
        agent = await registry.load_from_config(tenant_id, config_path)
        return agent
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
