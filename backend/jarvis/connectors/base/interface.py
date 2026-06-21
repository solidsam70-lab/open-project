from __future__ import annotations

from abc import ABC, abstractmethod
from .models import ConnectorAction, ConnectorCapability, ConnectorHealth, ConnectorResult


class ConnectorBase(ABC):
    connector_type: str

    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def health_check(self) -> ConnectorHealth:
        ...

    @abstractmethod
    def capabilities(self) -> list[ConnectorCapability]:
        ...

    @abstractmethod
    async def validate_permissions(self, action: ConnectorAction) -> bool:
        ...

    @abstractmethod
    async def dry_run(self, action: ConnectorAction) -> ConnectorResult:
        ...

    @abstractmethod
    async def execute(self, action: ConnectorAction) -> ConnectorResult:
        ...
