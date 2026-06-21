import logging
from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field


class ConnectorAuth(BaseModel):
    type: str  # api_key, oauth2, basic
    credentials: dict = Field(default_factory=dict)
    config: dict = Field(default_factory=dict)


class ConnectorResponse(BaseModel):
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)


class ConnectorBase(ABC):
    """Base class for all JARVIS connectors."""

    def __init__(self, config: dict = None, auth: ConnectorAuth = None):
        self.config = config or {}
        self.auth = auth
        self.logger = logging.getLogger(f"jarvis.connector.{self.__class__.__name__}")

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the connector with authentication."""
        ...

    @abstractmethod
    async def execute(self, action: str, params: dict) -> ConnectorResponse:
        """Execute a connector action."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the connector is operational."""
        ...

    @abstractmethod
    async def close(self) -> None:
        """Clean up connector resources."""
        ...

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
