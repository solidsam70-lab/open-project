from __future__ import annotations

import logging
import uuid
from .models import (
    TransitionTrigger,
    WorkflowDefinition,
    WorkflowEvent,
    WorkflowInstance,
    WorkflowRunStatus,
)
from .state_machine import WorkflowStateMachine

logger = logging.getLogger("jarvis.workflows")


class WorkflowRuntimeService:

    def __init__(self, repository, audit_service=None):
        self.repository = repository
        self.audit_service = audit_service

    async def start(
        self,
        definition: WorkflowDefinition,
        *,
        input_data: dict,
        created_by_user_id: str | None = None,
        agent_id: str | None = None,
    ) -> WorkflowInstance:
        machine = WorkflowStateMachine(definition)
        instance = WorkflowInstance(
            id=str(uuid.uuid4()),
            tenant_id=definition.tenant_id,
            definition_id=definition.id,
            definition_version=definition.version,
            current_state=definition.initial_state,
            status=WorkflowRunStatus.RUNNING,
            input_data=input_data,
            created_by_user_id=created_by_user_id,
            agent_id=agent_id,
        )
        await self.repository.save_instance(instance)
        await self.repository.append_event(WorkflowEvent(
            tenant_id=instance.tenant_id,
            workflow_instance_id=instance.id,
            from_state=None,
            to_state=instance.current_state,
            trigger=TransitionTrigger.SYSTEM,
            actor_user_id=created_by_user_id,
            agent_id=agent_id,
            metadata={"event": "workflow_started"},
        ))
        logger.info("Workflow started id=%s definition=%s", instance.id, definition.id)
        return instance

    async def transition(
        self,
        definition: WorkflowDefinition,
        instance: WorkflowInstance,
        to_state: str,
        trigger: TransitionTrigger,
        **kwargs,
    ) -> WorkflowInstance:
        machine = WorkflowStateMachine(definition)
        instance, event = machine.transition(instance, to_state, trigger, **kwargs)
        await self.repository.save_instance(instance)
        await self.repository.append_event(event)
        logger.info("Workflow transition id=%s state=%s", instance.id, instance.current_state)
        return instance


class InMemoryWorkflowRepository:
    def __init__(self):
        self.instances: dict[str, WorkflowInstance] = {}
        self.events: list[WorkflowEvent] = []

    async def save_instance(self, instance: WorkflowInstance) -> WorkflowInstance:
        self.instances[instance.id] = instance
        return instance

    async def get_instance(self, tenant_id: str, instance_id: str) -> WorkflowInstance | None:
        item = self.instances.get(instance_id)
        if item and item.tenant_id == tenant_id:
            return item
        return None

    async def append_event(self, event: WorkflowEvent) -> WorkflowEvent:
        self.events.append(event)
        return event
