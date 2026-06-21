import pytest
from jarvis.jarvis_core.knowledge import KnowledgeDocument, KnowledgeService


class TestKnowledgeService:

    def test_chunk_text_basic(self):
        service = KnowledgeService(db=None)
        text = "Hello world. This is a test. " * 100
        chunks = service._chunk_text(text, chunk_size=200, overlap=50)
        assert len(chunks) > 1
        assert all(len(c) <= 220 for c in chunks)

    def test_chunk_text_short(self):
        service = KnowledgeService(db=None)
        text = "Short text"
        chunks = service._chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == "Short text"

    def test_chunk_text_empty(self):
        service = KnowledgeService(db=None)
        chunks = service._chunk_text("")
        assert chunks == []

    def test_chunk_text_none(self):
        service = KnowledgeService(db=None)
        chunks = service._chunk_text(None)
        assert chunks == []


class TestKnowledgeDocument:

    def test_create_document(self):
        doc = KnowledgeDocument(
            tenant_id="t1",
            title="Test Doc",
            source_type="manual",
            content="Test content",
        )
        assert doc.embedding_status == "pending"
        assert doc.is_active is True
        assert doc.chunk_count == 0

    def test_document_with_chunks(self):
        doc = KnowledgeDocument(
            tenant_id="t1",
            title="Doc with chunks",
            source_type="web",
            chunk_count=5,
        )
        assert doc.chunk_count == 5

    def test_document_metadata(self):
        doc = KnowledgeDocument(
            tenant_id="t1",
            title="Meta Doc",
            source_type="notion",
            metadata={"author": "test", "version": 2},
        )
        assert doc.metadata["author"] == "test"
        assert doc.metadata["version"] == 2
