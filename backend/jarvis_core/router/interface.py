from abc import ABC, abstractmethod
from typing import Optional
from jarvis.jarvis_core.router.models import Intent, RouteMatch


class IRouter(ABC):

    @abstractmethod
    async def register_intent(self, intent: Intent) -> Intent:
        ...

    @abstractmethod
    async def route(self, tenant_id: str, query: str, context: dict) -> RouteMatch:
        ...

    @abstractmethod
    async def classify_intent(self, query: str, agent_role: str) -> str:
        ...
