import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.models import AuditLog as AuditLogDB
from jarvis.jarvis_core.audit.models import AuditEntry

logger = logging.getLogger("jarvis.audit")


class AuditService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(self, entry: AuditEntry) -> AuditEntry:
        db_entry = AuditLogDB(
            tenant_id=entry.tenant_id,
            user_id=entry.user_id,
            action=entry.action,
            resource_type=entry.resource_type,
            resource_id=entry.resource_id,
            details=entry.details,
            ip_address=entry.ip_address,
            user_agent=entry.user_agent,
        )
        self.db.add(db_entry)
        await self.db.flush()
        entry.id = db_entry.id
        entry.created_at = db_entry.created_at
        logger.debug("Audit: %s on %s/%s by %s", entry.action, entry.resource_type, entry.resource_id, entry.user_id)
        return entry

    async def query(
        self,
        tenant_id: str,
        action: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditEntry]:
        stmt = select(AuditLogDB).where(AuditLogDB.tenant_id == tenant_id)

        if action:
            stmt = stmt.where(AuditLogDB.action == action)
        if user_id:
            stmt = stmt.where(AuditLogDB.user_id == user_id)
        if resource_type:
            stmt = stmt.where(AuditLogDB.resource_type == resource_type)

        stmt = stmt.order_by(AuditLogDB.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(stmt)

        return [
            AuditEntry(
                id=row.id,
                tenant_id=row.tenant_id,
                user_id=row.user_id,
                action=row.action,
                resource_type=row.resource_type,
                resource_id=row.resource_id,
                details=row.details or {},
                ip_address=row.ip_address,
                user_agent=row.user_agent,
                created_at=row.created_at,
            )
            for row in result.scalars().all()
        ]
