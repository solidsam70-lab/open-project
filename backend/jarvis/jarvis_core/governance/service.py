from __future__ import annotations

import logging
from .interface import IGovernanceService
from .models import (
    ActionContext,
    ActionMode,
    ActorContext,
    DecisionStatus,
    GovernanceDecision,
    GovernancePolicy,
    RiskLevel,
)
from .exceptions import TenantBoundaryError

logger = logging.getLogger("jarvis.governance")

FINANCIAL_MODELS = {"account.move", "account.payment", "account.journal", "account.tax"}
EXTERNAL_SYSTEMS = {"gmail", "outlook", "whatsapp", "slack", "teams"}
CONFIG_MODELS = {"ir.config_parameter", "res.users", "res.groups", "ir.module.module"}


class GovernanceService(IGovernanceService):

    async def evaluate(
        self,
        *,
        actor: ActorContext,
        action: ActionContext,
        policy: GovernancePolicy,
    ) -> GovernanceDecision:
        if actor.tenant_id != action.resource.tenant_id:
            logger.warning(
                "Tenant boundary violation actor_tenant=%s resource_tenant=%s action=%s",
                actor.tenant_id,
                action.resource.tenant_id,
                action.action,
            )
            raise TenantBoundaryError("Action resource belongs to another tenant")

        missing: list[str] = []
        tags: list[str] = [action.resource.system, action.resource.resource_type, action.mode.value]

        if action.action in policy.blocked_actions:
            return GovernanceDecision(
                status=DecisionStatus.BLOCK,
                risk_level=RiskLevel.CRITICAL,
                reason=f"Action '{action.action}' is blocked by tenant policy.",
                blocked=True,
                audit_tags=tags + ["blocked_action"],
            )

        risk = self._classify_risk(action)

        if action.mode == ActionMode.DELETE and not policy.allow_delete_actions:
            return GovernanceDecision(
                status=DecisionStatus.BLOCK,
                risk_level=RiskLevel.CRITICAL,
                reason="Delete actions are disabled by default.",
                blocked=True,
                audit_tags=tags + ["delete_blocked"],
            )

        if risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            if policy.require_sources_for_high_risk and not action.sources_used:
                missing.append("source_grounding")
            threshold = policy.min_confidence_for_high_risk
        else:
            threshold = policy.min_confidence_for_action

        if action.confidence is not None and action.confidence < threshold:
            missing.append("confidence_threshold")

        if action.resource.system == "odoo":
            odoo_decision = self._evaluate_odoo_policy(action, policy)
            if odoo_decision:
                odoo_decision.missing_requirements.extend(missing)
                return odoo_decision

        if action.resource.system in EXTERNAL_SYSTEMS and action.mode == ActionMode.SEND:
            if policy.require_approval_for_external_send:
                return GovernanceDecision(
                    status=DecisionStatus.REQUIRE_APPROVAL,
                    risk_level=risk,
                    reason="External communication requires human approval.",
                    approval_required=True,
                    approval_reason="external_send",
                    missing_requirements=missing,
                    audit_tags=tags + ["external_send"],
                )

        if action.mode in {ActionMode.WRITE, ActionMode.CONFIGURE, ActionMode.SUBMIT}:
            if missing:
                return GovernanceDecision(
                    status=DecisionStatus.ESCALATE,
                    risk_level=risk,
                    reason="Action is missing required confidence or source grounding.",
                    escalation_required=True,
                    missing_requirements=missing,
                    audit_tags=tags + ["missing_requirements"],
                )

            return GovernanceDecision(
                status=DecisionStatus.REQUIRE_APPROVAL,
                risk_level=risk,
                reason="Side-effecting action requires approval by default.",
                approval_required=True,
                approval_reason="side_effecting_action",
                audit_tags=tags + ["approval_default"],
            )

        return GovernanceDecision(
            status=DecisionStatus.ALLOW,
            risk_level=risk,
            reason="Read-only or low-risk action allowed.",
            audit_tags=tags + ["allowed"],
        )

    def _classify_risk(self, action: ActionContext) -> RiskLevel:
        model = action.resource.resource_type
        if action.mode in {ActionMode.DELETE, ActionMode.SUBMIT, ActionMode.CONFIGURE}:
            return RiskLevel.CRITICAL
        if model in FINANCIAL_MODELS:
            return RiskLevel.CRITICAL if action.mode != ActionMode.READ else RiskLevel.HIGH
        if model in CONFIG_MODELS:
            return RiskLevel.CRITICAL
        if action.resource.system in EXTERNAL_SYSTEMS and action.mode == ActionMode.SEND:
            return RiskLevel.HIGH
        if action.mode == ActionMode.WRITE:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _evaluate_odoo_policy(
        self,
        action: ActionContext,
        policy: GovernancePolicy,
    ) -> GovernanceDecision | None:
        if action.resource.system != "odoo":
            return None

        model_policy = policy.odoo_model_policies.get(action.resource.resource_type)
        if not model_policy:
            if action.mode == ActionMode.READ:
                return None
            return GovernanceDecision(
                status=DecisionStatus.REQUIRE_APPROVAL,
                risk_level=self._classify_risk(action),
                reason="No explicit Odoo model policy found; approval required.",
                approval_required=True,
                approval_reason="missing_odoo_model_policy",
                audit_tags=["odoo", "approval_missing_model_policy"],
            )

        mode_to_field = {
            ActionMode.READ: "read",
            ActionMode.WRITE: "update" if action.resource.resource_id else "create",
            ActionMode.DELETE: "delete",
            ActionMode.CONFIGURE: "update",
            ActionMode.SUBMIT: "submit",
        }
        field = mode_to_field.get(action.mode)
        allowed_value = getattr(model_policy, field, None) if field else None

        if allowed_value is True:
            return None
        if allowed_value is False:
            return GovernanceDecision(
                status=DecisionStatus.BLOCK,
                risk_level=self._classify_risk(action),
                reason=f"Odoo policy blocks {action.mode.value} on {action.resource.resource_type}.",
                blocked=True,
                audit_tags=["odoo", "blocked_by_model_policy"],
            )
        if isinstance(allowed_value, str) and "approval" in allowed_value:
            return GovernanceDecision(
                status=DecisionStatus.REQUIRE_APPROVAL,
                risk_level=self._classify_risk(action),
                reason=f"Odoo policy requires approval for {action.mode.value} on {action.resource.resource_type}.",
                approval_required=True,
                approval_reason=f"odoo_{action.resource.resource_type}_{action.mode.value}",
                dry_run_required="draft_only" in allowed_value,
                audit_tags=["odoo", "approval_by_model_policy"],
            )
        return None
