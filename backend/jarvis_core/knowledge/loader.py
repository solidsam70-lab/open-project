import logging
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.models import KnowledgeDocument as KnowledgeDocumentDB, KnowledgeChunk as KnowledgeChunkDB
from jarvis.jarvis_core.knowledge.models import KnowledgeDocument, KnowledgeChunk, KnowledgeSearchResult
from jarvis.jarvis_core.knowledge.interface import IKnowledgeService

logger = logging.getLogger("jarvis.knowledge")


class KnowledgeService(IKnowledgeService):

    def __init__(self, db: AsyncSession, embedding_client=None, qdrant_client=None):
        self.db = db
        self.embedding_client = embedding_client
        self.qdrant_client = qdrant_client

    async def ingest(self, document: KnowledgeDocument) -> KnowledgeDocument:
        db_doc = KnowledgeDocumentDB(
            tenant_id=document.tenant_id,
            title=document.title,
            source_type=document.source_type,
            source_id=document.source_id,
            source_url=document.source_url,
            content_type=document.content_type,
            content=document.content,
            metadata=document.metadata,
        )
        self.db.add(db_doc)
        await self.db.flush()

        if document.content:
            chunks = self._chunk_text(
                document.content,
                document.metadata.get("chunk_size", 1000),
                document.metadata.get("chunk_overlap", 200),
            )

            for i, chunk_text in enumerate(chunks):
                chunk = KnowledgeChunkDB(
                    document_id=db_doc.id,
                    tenant_id=document.tenant_id,
                    chunk_index=i,
                    content=chunk_text,
                    metadata=document.metadata,
                )
                self.db.add(chunk)

            db_doc.chunk_count = len(chunks)

            if self.embedding_client and self.qdrant_client:
                await self._generate_embeddings(db_doc.id, chunks)
                db_doc.embedding_status = "completed"
            else:
                db_doc.embedding_status = "pending"

        await self.db.flush()
        logger.info("Ingested document: %s (%d chunks)", document.title, db_doc.chunk_count)

        document.id = db_doc.id
        document.embedding_status = db_doc.embedding_status
        document.chunk_count = db_doc.chunk_count
        return document

    async def search(self, tenant_id: str, query: str, limit: int = 5) -> str:
        if self.qdrant_client:
            return await self._vector_search(tenant_id, query, limit)

        return await self._keyword_search(tenant_id, query, limit)

    async def _vector_search(self, tenant_id: str, query: str, limit: int) -> str:
        try:
            query_embedding = await self.embedding_client.embed(query)
            search_result = self.qdrant_client.search(
                collection_name=f"jarvis_{tenant_id}",
                query_vector=query_embedding,
                limit=limit,
            )

            if not search_result:
                return "No relevant knowledge found."

            contexts = []
            for point in search_result:
                contexts.append(f"[Score: {point.score:.2f}]\n{point.payload.get('content', '')}")

            return "\n\n---\n\n".join(contexts)
        except Exception as e:
            logger.error("Vector search failed, falling back to keyword: %s", e)
            return await self._keyword_search(tenant_id, query, limit)

    async def _keyword_search(self, tenant_id: str, query: str, limit: int) -> str:
        result = await self.db.execute(
            select(KnowledgeChunkDB)
            .where(KnowledgeChunkDB.tenant_id == tenant_id)
            .order_by(KnowledgeChunkDB.chunk_index)
            .limit(limit * 5)
        )

        query_lower = query.lower()
        scored = []
        for chunk in result.scalars().all():
            content_lower = chunk.content.lower()
            word_matches = sum(1 for word in query_lower.split() if word in content_lower)
            if word_matches > 0:
                scored.append((word_matches, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_chunks = scored[:limit]

        if not top_chunks:
            return "No relevant knowledge found."

        contexts = []
        for score, chunk in top_chunks:
            doc_result = await self.db.execute(
                select(KnowledgeDocumentDB).where(KnowledgeDocumentDB.id == chunk.document_id)
            )
            doc = doc_result.scalar_one_or_none()
            title = doc.title if doc else "Unknown"
            contexts.append(f"[Source: {title} (Score: {score})]\n{chunk.content[:500]}")

        return "\n\n---\n\n".join(contexts)

    async def delete(self, document_id: str) -> None:
        stmt = delete(KnowledgeChunkDB).where(KnowledgeChunkDB.document_id == document_id)
        await self.db.execute(stmt)
        stmt = delete(KnowledgeDocumentDB).where(KnowledgeDocumentDB.id == document_id)
        await self.db.execute(stmt)
        logger.info("Deleted document: %s", document_id)

    async def get_document(self, document_id: str) -> Optional[KnowledgeDocument]:
        result = await self.db.execute(
            select(KnowledgeDocumentDB).where(KnowledgeDocumentDB.id == document_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return None

        chunks_result = await self.db.execute(
            select(KnowledgeChunkDB)
            .where(KnowledgeChunkDB.document_id == document_id)
            .order_by(KnowledgeChunkDB.chunk_index)
        )

        return KnowledgeDocument(
            id=doc.id,
            tenant_id=doc.tenant_id,
            title=doc.title,
            source_type=doc.source_type,
            source_id=doc.source_id,
            source_url=doc.source_url,
            content_type=doc.content_type,
            content=doc.content,
            metadata=doc.metadata or {},
            embedding_status=doc.embedding_status,
            chunk_count=doc.chunk_count,
            is_active=doc.is_active,
            chunks=[
                KnowledgeChunk(
                    id=c.id,
                    document_id=c.document_id,
                    tenant_id=c.tenant_id,
                    chunk_index=c.chunk_index,
                    content=c.content,
                    metadata=c.metadata or {},
                    qdrant_point_id=c.qdrant_point_id,
                )
                for c in chunks_result.scalars().all()
            ],
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)
            if end < text_len:
                last_period = text.rfind(". ", start, end)
                last_newline = text.rfind("\n", start, end)
                split_at = max(last_period, last_newline)
                if split_at > start:
                    end = split_at + 1

            chunks.append(text[start:end].strip())
            start = end - overlap if end < text_len else text_len

        return chunks if chunks else [text]
