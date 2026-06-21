class ConnectorError(Exception):
    """Base connector error."""


class ConnectorAuthError(ConnectorError):
    """Authentication or authorization failed."""


class ConnectorRateLimitError(ConnectorError):
    """The external system rate limited the request."""


class ConnectorActionNotSupportedError(ConnectorError):
    """Requested action is not supported by this connector."""


class ConnectorDryRunNotSupportedError(ConnectorError):
    """Requested dry-run is not supported for this action."""
