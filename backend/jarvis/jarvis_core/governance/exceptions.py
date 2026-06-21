class GovernanceError(Exception):
    """Base exception for governance failures."""


class TenantBoundaryError(GovernanceError):
    """Raised when an action attempts to cross tenant boundaries."""


class ActionBlockedError(GovernanceError):
    """Raised when a governance policy blocks an action."""


class ApprovalRequiredError(GovernanceError):
    """Raised when an action cannot execute before human approval."""
