import logging
from fastapi import APIRouter, Depends, HTTPException, status

from jarvis.jarvis_core.execution import ExecutionRequest, ExecutionResult
from jarvis.api.dependencies import (
    get_current_user, get_tenant_id, get_execution_engine,
)
from jarvis.jarvis_core.auth import AuthContext

logger = logging.getLogger("jarvis.api.execution")
router = APIRouter(prefix="/execution", tags=["Execution"])


@router.post("/run", response_model=ExecutionResult)
async def execute_workflow(
    request: ExecutionRequest,
    engine: ExecutionEngine = Depends(get_execution_engine),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    request.tenant_id = tenant_id
    request.user_id = current_user.user_id
    try:
        result = await engine.execute(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("Execution failed: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{execution_id}", response_model=ExecutionResult)
async def get_execution(
    execution_id: str,
    engine: ExecutionEngine = Depends(get_execution_engine),
    current_user: AuthContext = Depends(get_current_user),
):
    result = await engine.get_result(execution_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execution not found")
    return result
