from abc import ABC, abstractmethod
from typing import Optional
from jarvis.jarvis_core.knowledge.models import KnowledgeDocument, KnowledgeChunk, KnowledgeSearchResult


class IKnowledgeService(ABC):

    @abstractmethod
    async def ingest(self, document: KnowledgeDocument) -> KnowledgeDocument:
        ...

    @abstractmethod
    async def search(self, tenant_id: str, query: str, limit: int = 5) -> str:
        ...

    @abstractmethod
    async def delete(self, document_id: str) -> None:
        ...

    @abstractmethod
    async def get_document(self, document_id: str) -> Optional[KnowledgeDocument]:
        ...
