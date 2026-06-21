import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query

from jarvis.jarvis_core.memory import MemoryEntry, MemoryService
from jarvis.api.dependencies import get_current_user, get_tenant_id, get_memory_service
from jarvis.jarvis_core.auth import AuthContext

logger = logging.getLogger("jarvis.api.memory")
router = APIRouter(prefix="/memory", tags=["Memory"])


@router.post("/store", response_model=MemoryEntry)
async def store_memory(
    entry: MemoryEntry,
    memory: MemoryService = Depends(get_memory_service),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    entry.tenant_id = tenant_id
    entry.user_id = current_user.user_id
    result = await memory.store(entry)
    return result


@router.get("/recent")
async def get_recent_memory(
    agent_id: str,
    limit: int = Query(10, ge=1, le=100),
    memory: MemoryService = Depends(get_memory_service),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    result = await memory.get_recent(tenant_id, agent_id, limit)
    return result


@router.get("/search")
async def search_memory(
    query: str,
    memory_type: Optional[str] = Query(None),
    memory: MemoryService = Depends(get_memory_service),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    result = await memory.search(tenant_id, query, memory_type)
    return result


@router.delete("/{entry_id}", status_code=204)
async def forget_memory(
    entry_id: str,
    memory: MemoryService = Depends(get_memory_service),
    current_user: AuthContext = Depends(get_current_user),
):
    await memory.forget(entry_id)
