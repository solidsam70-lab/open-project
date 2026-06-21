import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field


class ConnectorAuth(BaseModel):
    type: str
    credentials: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)


class ConnectorResponse(BaseModel):
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class ConnectorBase(ABC):
    """V1 connector base class - used by existing connectors (Odoo, Notion, etc.)."""

    def __init__(self, config: dict = None, auth: ConnectorAuth = None):
        self.config = config or {}
        self.auth = auth
        self.logger = logging.getLogger(f"jarvis.connector.{self.__class__.__name__}")

    @abstractmethod
    async def initialize(self) -> bool:
        ...

    @abstractmethod
    async def execute(self, action: str, params: dict) -> ConnectorResponse:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...

    @abstractmethod
    async def close(self) -> None:
        ...

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
