import pytest

from jarvis.jarvis_core.workflows import (
    TransitionTrigger,
    WorkflowDefinition,
    WorkflowRuntimeService,
    WorkflowState,
    WorkflowStateMachine,
    WorkflowTransition,
    InMemoryWorkflowRepository,
)
from jarvis.jarvis_core.workflows.exceptions import InvalidStateTransitionError
from jarvis.jarvis_core.workflows.models import WorkflowRunStatus


def lead_workflow_definition():
    return WorkflowDefinition(
        id="lead_qualification",
        tenant_id="t1",
        name="Lead Qualification",
        agent_slug="lead_qualification",
        initial_state="new_message_received",
        states=[
            WorkflowState(name="new_message_received"),
            WorkflowState(name="lead_extracted"),
            WorkflowState(name="approval_requested", requires_approval=True),
            WorkflowState(name="completed", terminal=True),
        ],
        transitions=[
            WorkflowTransition(from_state="new_message_received", to_state="lead_extracted", trigger=TransitionTrigger.AGENT),
            WorkflowTransition(from_state="lead_extracted", to_state="approval_requested", trigger=TransitionTrigger.SYSTEM),
            WorkflowTransition(from_state="approval_requested", to_state="completed", trigger=TransitionTrigger.APPROVAL),
        ],
        approval_points=["approval_requested"],
    )


@pytest.mark.asyncio
async def test_workflow_transitions_to_approval_state():
    definition = lead_workflow_definition()
    repo = InMemoryWorkflowRepository()
    service = WorkflowRuntimeService(repo)
    instance = await service.start(definition, input_data={"message": "Need Odoo"})
    instance = await service.transition(definition, instance, "lead_extracted", TransitionTrigger.AGENT)
    instance = await service.transition(definition, instance, "approval_requested", TransitionTrigger.SYSTEM, approval_id="a1")

    assert instance.status == WorkflowRunStatus.WAITING_FOR_APPROVAL
    assert instance.approval_id == "a1"


@pytest.mark.asyncio
async def test_invalid_workflow_transition_fails():
    definition = lead_workflow_definition()
    repo = InMemoryWorkflowRepository()
    service = WorkflowRuntimeService(repo)
    instance = await service.start(definition, input_data={})

    with pytest.raises(InvalidStateTransitionError):
        await service.transition(definition, instance, "completed", TransitionTrigger.AGENT)
