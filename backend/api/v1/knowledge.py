import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status

from jarvis.jarvis_core.knowledge import KnowledgeDocument, KnowledgeService
from jarvis.api.dependencies import get_current_user, get_tenant_id, get_knowledge_service
from jarvis.jarvis_core.auth import AuthContext

logger = logging.getLogger("jarvis.api.knowledge")
router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.post("/ingest", response_model=KnowledgeDocument)
async def ingest_document(
    document: KnowledgeDocument,
    knowledge: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    document.tenant_id = tenant_id
    result = await knowledge.ingest(document)
    return result


@router.get("/search")
async def search_knowledge(
    query: str,
    limit: int = Query(5, ge=1, le=50),
    knowledge: KnowledgeService = Depends(get_knowledge_service),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    result = await knowledge.search(tenant_id, query, limit)
    return {"results": result}


@router.get("/documents/{document_id}", response_model=KnowledgeDocument)
async def get_document(
    document_id: str,
    knowledge: KnowledgeService = Depends(get_knowledge_service),
    current_user: AuthContext = Depends(get_current_user),
):
    doc = await knowledge.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: str,
    knowledge: KnowledgeService = Depends(get_knowledge_service),
    current_user: AuthContext = Depends(get_current_user),
):
    await knowledge.delete(document_id)
