from __future__ import annotations

from datetime import datetime, timezone

from .exceptions import InvalidStateTransitionError, InvalidWorkflowDefinitionError
from .models import (
    TransitionTrigger,
    WorkflowDefinition,
    WorkflowEvent,
    WorkflowInstance,
    WorkflowRunStatus,
)


class WorkflowStateMachine:
    def __init__(self, definition: WorkflowDefinition):
        self.definition = definition
        self._states = {state.name: state for state in definition.states}
        self._transitions = definition.transitions
        self._validate_definition()

    def _validate_definition(self) -> None:
        if self.definition.initial_state not in self._states:
            raise InvalidWorkflowDefinitionError(
                f"Initial state '{self.definition.initial_state}' is not defined."
            )

        for transition in self._transitions:
            if transition.from_state not in self._states:
                raise InvalidWorkflowDefinitionError(f"Unknown from_state '{transition.from_state}'.")
            if transition.to_state not in self._states:
                raise InvalidWorkflowDefinitionError(f"Unknown to_state '{transition.to_state}'.")

    def can_transition(
        self,
        instance: WorkflowInstance,
        to_state: str,
        trigger: TransitionTrigger,
    ) -> bool:
        return any(
            t.from_state == instance.current_state
            and t.to_state == to_state
            and t.trigger == trigger
            for t in self._transitions
        )

    def transition(
        self,
        instance: WorkflowInstance,
        to_state: str,
        trigger: TransitionTrigger,
        *,
        actor_user_id: str | None = None,
        agent_id: str | None = None,
        approval_id: str | None = None,
        metadata: dict | None = None,
    ) -> tuple[WorkflowInstance, WorkflowEvent]:
        if not self.can_transition(instance, to_state, trigger):
            raise InvalidStateTransitionError(
                f"Transition {instance.current_state} -> {to_state} via {trigger.value} is not allowed."
            )

        from_state = instance.current_state
        instance.current_state = to_state
        instance.updated_at = datetime.now(timezone.utc)

        target = self._states[to_state]
        if target.terminal:
            instance.status = WorkflowRunStatus.COMPLETED
            instance.completed_at = datetime.now(timezone.utc)
        elif target.requires_approval or to_state in self.definition.approval_points:
            instance.status = WorkflowRunStatus.WAITING_FOR_APPROVAL
            instance.approval_id = approval_id
        else:
            instance.status = WorkflowRunStatus.RUNNING

        event = WorkflowEvent(
            tenant_id=instance.tenant_id,
            workflow_instance_id=instance.id,
            from_state=from_state,
            to_state=to_state,
            trigger=trigger,
            actor_user_id=actor_user_id,
            agent_id=agent_id,
            approval_id=approval_id,
            metadata=metadata or {},
        )
        return instance, event
