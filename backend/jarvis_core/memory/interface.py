from abc import ABC, abstractmethod
from typing import Optional
from jarvis.jarvis_core.memory.models import MemoryEntry, MemorySearchResult


class IMemoryService(ABC):

    @abstractmethod
    async def store(self, entry: MemoryEntry) -> MemoryEntry:
        ...

    @abstractmethod
    async def get_recent(self, tenant_id: str, agent_id: str, limit: int = 10) -> list[dict]:
        ...

    @abstractmethod
    async def search(self, tenant_id: str, query: str, memory_type: Optional[str] = None) -> list[MemorySearchResult]:
        ...

    @abstractmethod
    async def forget(self, entry_id: str) -> None:
        ...
