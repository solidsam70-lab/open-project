# V1 backward compatible exports (used by existing connectors)
from .models_v1 import ConnectorAuth, ConnectorBase, ConnectorResponse

# V2 new interface (next-gen governed connectors)
from .interface import ConnectorBase as ConnectorBaseV2
from .models import ConnectorAction, ConnectorCapability, ConnectorHealth, ConnectorResult, ConnectorStatus
from .service import GovernedConnectorExecutor

__all__ = [
    "ConnectorAction",
    "ConnectorAuth",
    "ConnectorBase",
    "ConnectorBaseV2",
    "ConnectorCapability",
    "ConnectorHealth",
    "ConnectorResponse",
    "ConnectorResult",
    "ConnectorStatus",
    "GovernedConnectorExecutor",
]
