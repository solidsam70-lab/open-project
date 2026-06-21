class ApprovalError(Exception):
    """Base approval exception."""


class ApprovalNotFoundError(ApprovalError):
    """Raised when an approval request cannot be found."""


class InvalidApprovalDecisionError(ApprovalError):
    """Raised when a decision is invalid for the approval state."""
