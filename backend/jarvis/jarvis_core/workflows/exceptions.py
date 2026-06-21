class WorkflowError(Exception):
    """Base workflow exception."""


class InvalidWorkflowDefinitionError(WorkflowError):
    """Raised when a workflow definition is malformed."""


class InvalidStateTransitionError(WorkflowError):
    """Raised when a transition is not allowed by the workflow definition."""


class WorkflowApprovalRequiredError(WorkflowError):
    """Raised when execution must pause for approval."""
