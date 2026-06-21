import json
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.models import AgentRegistry as AgentRegistryDB
from jarvis.jarvis_core.registry.models import AgentDefinition, AgentStatus
from jarvis.jarvis_core.registry.interface import IAgentRegistry

logger = logging.getLogger("jarvis.registry")


class AgentRegistryService(IAgentRegistry):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, agent: AgentDefinition) -> AgentDefinition:
        existing = await self.get_by_slug(agent.tenant_id, agent.slug)
        if existing:
            logger.warning("Agent %s already registered, updating", agent.slug)
            return await self.update(existing.id, agent.model_dump())

        db_agent = AgentRegistryDB(
            tenant_id=agent.tenant_id,
            name=agent.name,
            slug=agent.slug,
            role=agent.role,
            goal=agent.goal,
            model=agent.model,
            temperature=agent.temperature,
            status=agent.status.value,
            agent_metadata=agent.agent_metadata,
            kpis=agent.kpis,
            knowledge_sources=agent.knowledge_sources,
            memory_sources=agent.memory_sources,
            tools=agent.tools,
            workflows=agent.workflows,
            input_schema=agent.input_schema,
            output_schema=agent.output_schema,
            escalation_rules=agent.escalation_rules,
        )
        self.db.add(db_agent)
        await self.db.flush()
        logger.info("Registered agent: %s (%s)", agent.name, agent.slug)
        return self._to_definition(db_agent)

    async def get(self, agent_id: str) -> Optional[AgentDefinition]:
        result = await self.db.execute(
            select(AgentRegistryDB).where(AgentRegistryDB.id == agent_id)
        )
        db_agent = result.scalar_one_or_none()
        return self._to_definition(db_agent) if db_agent else None

    async def get_by_slug(self, tenant_id: str, slug: str) -> Optional[AgentDefinition]:
        result = await self.db.execute(
            select(AgentRegistryDB).where(
                AgentRegistryDB.tenant_id == tenant_id,
                AgentRegistryDB.slug == slug,
            )
        )
        db_agent = result.scalar_one_or_none()
        return self._to_definition(db_agent) if db_agent else None

    async def list(self, tenant_id: str, status: Optional[str] = None) -> list[AgentDefinition]:
        query = select(AgentRegistryDB).where(AgentRegistryDB.tenant_id == tenant_id)
        if status:
            query = query.where(AgentRegistryDB.status == status)
        result = await self.db.execute(query.order_by(AgentRegistryDB.created_at.desc()))
        return [self._to_definition(row) for row in result.scalars().all()]

    async def update(self, agent_id: str, updates: dict) -> AgentDefinition:
        updates.pop("id", None)
        updates.pop("created_at", None)
        if "status" in updates and isinstance(updates["status"], AgentStatus):
            updates["status"] = updates["status"].value
        if "status" in updates and isinstance(updates["status"], str):
            updates["status"] = updates["status"]

        stmt = (
            update(AgentRegistryDB)
            .where(AgentRegistryDB.id == agent_id)
            .values(**updates)
        )
        await self.db.execute(stmt)
        agent = await self.get(agent_id)
        logger.info("Updated agent: %s", agent_id)
        return agent

    async def delete(self, agent_id: str) -> None:
        stmt = delete(AgentRegistryDB).where(AgentRegistryDB.id == agent_id)
        await self.db.execute(stmt)
        logger.info("Deleted agent: %s", agent_id)

    async def load_from_config(self, tenant_id: str, config_path: str) -> AgentDefinition:
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Agent config not found: {config_path}")

        with open(path) as f:
            data = json.load(f)

        data["tenant_id"] = tenant_id
        data["config_path"] = config_path
        agent = AgentDefinition(**data)
        return await self.register(agent)

    def _to_definition(self, db_agent: AgentRegistryDB) -> AgentDefinition:
        return AgentDefinition(
            id=db_agent.id,
            tenant_id=db_agent.tenant_id,
            name=db_agent.name,
            slug=db_agent.slug,
            role=db_agent.role,
            goal=db_agent.goal,
            model=db_agent.model,
            temperature=db_agent.temperature,
            status=AgentStatus(db_agent.status),
            config_path=db_agent.config_path,
            kpis=db_agent.kpis or [],
            knowledge_sources=db_agent.knowledge_sources or [],
            memory_sources=db_agent.memory_sources or [],
            tools=db_agent.tools or [],
            workflows=db_agent.workflows or [],
            input_schema=db_agent.input_schema or {},
            output_schema=db_agent.output_schema or {},
            escalation_rules=db_agent.escalation_rules or [],
            agent_metadata=db_agent.agent_metadata or {},
            created_at=db_agent.created_at,
            updated_at=db_agent.updated_at,
        )
