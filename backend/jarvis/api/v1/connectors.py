import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.session import get_db
from jarvis.database.models import ConnectorConfig as ConnectorConfigDB
from jarvis.api.dependencies import get_current_user, get_tenant_id
from jarvis.jarvis_core.auth import AuthContext

logger = logging.getLogger("jarvis.api.connectors")
router = APIRouter(prefix="/connectors", tags=["Connectors"])


@router.post("/configure")
async def configure_connector(
    connector_type: str,
    name: str,
    config: dict,
    credentials: dict = {},
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    from sqlalchemy import select

    result = await db.execute(
        select(ConnectorConfigDB).where(
            ConnectorConfigDB.tenant_id == tenant_id,
            ConnectorConfigDB.connector_type == connector_type,
            ConnectorConfigDB.name == name,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.config = config
        existing.credentials = credentials
    else:
        db_config = ConnectorConfigDB(
            tenant_id=tenant_id,
            connector_type=connector_type,
            name=name,
            config=config,
            credentials=credentials,
        )
        db.add(db_config)

    await db.flush()
    return {"message": f"Connector {connector_type}/{name} configured", "status": "ok"}


@router.get("/")
async def list_connectors(
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    from sqlalchemy import select

    result = await db.execute(
        select(ConnectorConfigDB).where(ConnectorConfigDB.tenant_id == tenant_id)
    )
    configs = result.scalars().all()
    return [
        {
            "id": c.id,
            "type": c.connector_type,
            "name": c.name,
            "is_enabled": c.is_enabled,
            "last_sync": c.last_sync_at,
        }
        for c in configs
    ]


@router.delete("/{connector_id}", status_code=204)
async def delete_connector(
    connector_id: str,
    db: AsyncSession = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
    current_user: AuthContext = Depends(get_current_user),
):
    from sqlalchemy import select, delete

    result = await db.execute(
        select(ConnectorConfigDB).where(
            ConnectorConfigDB.id == connector_id,
            ConnectorConfigDB.tenant_id == tenant_id,
        )
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="Connector not found")

    stmt = delete(ConnectorConfigDB).where(ConnectorConfigDB.id == connector_id)
    await db.execute(stmt)
