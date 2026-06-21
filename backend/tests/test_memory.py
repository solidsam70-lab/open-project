import pytest
from datetime import datetime, timezone
from jarvis.jarvis_core.memory import MemoryEntry, MemoryService


class TestMemoryEntry:

    def test_create_memory(self):
        entry = MemoryEntry(
            tenant_id="t1",
            agent_id="a1",
            memory_type="conversation",
            key="user_preference",
            value={"language": "Arabic"},
        )
        assert entry.importance == 0.5
        assert entry.context == {}

    def test_memory_importance(self):
        entry = MemoryEntry(
            tenant_id="t1",
            agent_id="a1",
            memory_type="decision",
            key="critical_decision",
            value={"approved": True},
            importance=0.95,
        )
        assert entry.importance == 0.95

    def test_memory_expiry(self):
        future = datetime.now(timezone.utc)
        entry = MemoryEntry(
            tenant_id="t1",
            agent_id="a1",
            memory_type="temporary",
            key="session_data",
            value={"step": 3},
            expires_at=future,
        )
        assert entry.expires_at == future


class TestMemoryService:

    def test_memory_entry_creation(self):
        entry = MemoryEntry(
            tenant_id="t1",
            agent_id="a1",
            memory_type="test",
            key="test_key",
            value={"data": "test_value"},
        )
        assert entry.memory_type == "test"
        assert entry.key == "test_key"
        assert entry.value["data"] == "test_value"
