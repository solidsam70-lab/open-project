from abc import ABC, abstractmethod
from typing import Optional
from jarvis.jarvis_core.registry.models import AgentDefinition


class IAgentRegistry(ABC):

    @abstractmethod
    async def register(self, agent: AgentDefinition) -> AgentDefinition:
        ...

    @abstractmethod
    async def get(self, agent_id: str) -> Optional[AgentDefinition]:
        ...

    @abstractmethod
    async def get_by_slug(self, tenant_id: str, slug: str) -> Optional[AgentDefinition]:
        ...

    @abstractmethod
    async def list(self, tenant_id: str, status: Optional[str] = None) -> list[AgentDefinition]:
        ...

    @abstractmethod
    async def update(self, agent_id: str, updates: dict) -> AgentDefinition:
        ...

    @abstractmethod
    async def delete(self, agent_id: str) -> None:
        ...

    @abstractmethod
    async def load_from_config(self, tenant_id: str, config_path: str) -> AgentDefinition:
        ...
