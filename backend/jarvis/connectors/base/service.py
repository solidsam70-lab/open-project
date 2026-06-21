from __future__ import annotations

import logging
from jarvis.jarvis_core.governance import (
    ActionContext,
    ActorContext,
    GovernancePolicy,
    GovernanceService,
    ResourceRef,
)
from jarvis.jarvis_core.governance.models import DecisionStatus
from .exceptions import ConnectorActionNotSupportedError, ConnectorDryRunNotSupportedError
from .interface import ConnectorBase
from .models import ConnectorAction, ConnectorResult

logger = logging.getLogger("jarvis.connectors")


class GovernedConnectorExecutor:

    def __init__(self, governance_service: GovernanceService, audit_service=None):
        self.governance_service = governance_service
        self.audit_service = audit_service

    async def run(
        self,
        connector: ConnectorBase,
        *,
        actor: ActorContext,
        action: ConnectorAction,
        policy: GovernancePolicy,
        confidence: float | None = None,
        sources_used: list[str] | None = None,
    ) -> ConnectorResult:
        self._ensure_action_supported(connector, action)

        decision = await self.governance_service.evaluate(
            actor=actor,
            action=ActionContext(
                action=action.action,
                mode=action.mode,
                resource=ResourceRef(
                    system=action.connector_type,
                    resource_type=action.resource_type,
                    resource_id=action.resource_id,
                    tenant_id=action.tenant_id,
                ),
                payload=action.params,
                confidence=confidence,
                sources_used=sources_used or [],
                dry_run=action.dry_run,
                idempotency_key=action.idempotency_key,
            ),
            policy=policy,
        )

        if decision.status == DecisionStatus.BLOCK:
            return ConnectorResult(
                success=False,
                connector_type=action.connector_type,
                action=action.action,
                mode=action.mode,
                dry_run=action.dry_run,
                error_code="ACTION_BLOCKED",
                error_message=decision.reason,
                audit_metadata={"governance": decision.model_dump(mode="json")},
            )

        if decision.status in {DecisionStatus.REQUIRE_APPROVAL, DecisionStatus.ESCALATE}:
            return ConnectorResult(
                success=False,
                connector_type=action.connector_type,
                action=action.action,
                mode=action.mode,
                dry_run=True,
                error_code=decision.status.value.upper(),
                error_message=decision.reason,
                audit_metadata={"governance": decision.model_dump(mode="json")},
            )

        if action.dry_run or decision.dry_run_required:
            return await connector.dry_run(action)

        return await connector.execute(action)

    def _ensure_action_supported(self, connector: ConnectorBase, action: ConnectorAction) -> None:
        for capability in connector.capabilities():
            if (
                capability.action == action.action
                and capability.mode == action.mode
                and capability.resource_type == action.resource_type
            ):
                if action.dry_run and not capability.supports_dry_run:
                    raise ConnectorDryRunNotSupportedError(action.action)
                return
        raise ConnectorActionNotSupportedError(action.action)
