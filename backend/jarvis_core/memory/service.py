import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.models import MemoryEntry as MemoryEntryDB
from jarvis.jarvis_core.memory.models import MemoryEntry, MemorySearchResult
from jarvis.jarvis_core.memory.interface import IMemoryService

logger = logging.getLogger("jarvis.memory")


class MemoryService(IMemoryService):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def store(self, entry: MemoryEntry) -> MemoryEntry:
        db_entry = MemoryEntryDB(
            tenant_id=entry.tenant_id,
            agent_id=entry.agent_id,
            user_id=entry.user_id,
            memory_type=entry.memory_type,
            key=entry.key,
            value=entry.value,
            importance=entry.importance,
            context=entry.context,
            expires_at=entry.expires_at,
        )
        self.db.add(db_entry)
        await self.db.flush()
        logger.debug("Stored memory: %s/%s", entry.memory_type, entry.key)
        entry.id = db_entry.id
        entry.created_at = db_entry.created_at
        return entry

    async def get_recent(self, tenant_id: str, agent_id: str, limit: int = 10) -> list[dict]:
        result = await self.db.execute(
            select(MemoryEntryDB)
            .where(
                MemoryEntryDB.tenant_id == tenant_id,
                MemoryEntryDB.agent_id == agent_id,
            )
            .order_by(MemoryEntryDB.created_at.desc())
            .limit(limit)
        )
        entries = []
        for row in result.scalars().all():
            entries.append({
                "type": row.memory_type,
                "key": row.key,
                "value": row.value,
                "importance": row.importance,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            })
        return entries

    async def search(
        self, tenant_id: str, query: str, memory_type: Optional[str] = None
    ) -> list[MemorySearchResult]:
        stmt = select(MemoryEntryDB).where(MemoryEntryDB.tenant_id == tenant_id)

        if memory_type:
            stmt = stmt.where(MemoryEntryDB.memory_type == memory_type)

        result = await self.db.execute(
            stmt.order_by(MemoryEntryDB.importance.desc()).limit(20)
        )

        results = []
        query_lower = query.lower()
        for row in result.scalars().all():
            value_str = json.dumps(row.value).lower()
            key_str = row.key.lower()

            if query_lower in value_str or query_lower in key_str:
                results.append(MemorySearchResult(
                    id=row.id,
                    memory_type=row.memory_type,
                    key=row.key,
                    value=row.value,
                    importance=row.importance,
                    context=row.context or {},
                    created_at=row.created_at,
                    score=row.importance,
                ))

        return results

    async def forget(self, entry_id: str) -> None:
        stmt = delete(MemoryEntryDB).where(MemoryEntryDB.id == entry_id)
        await self.db.execute(stmt)
        logger.info("Forgot memory entry: %s", entry_id)
