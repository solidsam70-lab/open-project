from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class KnowledgeChunk(BaseModel):
    id: Optional[str] = None
    document_id: str
    tenant_id: str
    chunk_index: int
    content: str
    metadata: dict = Field(default_factory=dict)
    qdrant_point_id: Optional[str] = None
    created_at: Optional[datetime] = None


class KnowledgeDocument(BaseModel):
    id: Optional[str] = None
    tenant_id: str
    title: str
    source_type: str
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    content_type: str = "text"
    content: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    embedding_status: str = "pending"
    chunk_count: int = 0
    is_active: bool = True
    chunks: list[KnowledgeChunk] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeSearchResult(BaseModel):
    document_id: str
    chunk_id: str
    content: str
    title: str
    source_type: str
    score: float
    metadata: dict = Field(default_factory=dict)
