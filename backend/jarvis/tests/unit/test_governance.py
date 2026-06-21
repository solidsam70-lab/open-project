import pytest

from jarvis.jarvis_core.governance import (
    ActionContext,
    ActionMode,
    ActorContext,
    DecisionStatus,
    GovernancePolicy,
    GovernanceService,
    OdooModelPolicy,
    ResourceRef,
)
from jarvis.jarvis_core.governance.exceptions import TenantBoundaryError


@pytest.mark.asyncio
async def test_governance_allows_read_only_action():
    service = GovernanceService()
    decision = await service.evaluate(
        actor=ActorContext(tenant_id="t1", user_id="u1"),
        action=ActionContext(
            action="read_lead",
            mode=ActionMode.READ,
            resource=ResourceRef(system="odoo", resource_type="crm.lead", resource_id="1", tenant_id="t1"),
        ),
        policy=GovernancePolicy(tenant_id="t1"),
    )
    assert decision.status == DecisionStatus.ALLOW


@pytest.mark.asyncio
async def test_governance_requires_approval_for_odoo_write():
    service = GovernanceService()
    policy = GovernancePolicy(
        tenant_id="t1",
        odoo_model_policies={
            "crm.lead": OdooModelPolicy(model="crm.lead", update="approval_required")
        },
    )
    decision = await service.evaluate(
        actor=ActorContext(tenant_id="t1", user_id="u1"),
        action=ActionContext(
            action="update_lead",
            mode=ActionMode.WRITE,
            confidence=0.95,
            sources_used=["odoo:crm.lead:1"],
            resource=ResourceRef(system="odoo", resource_type="crm.lead", resource_id="1", tenant_id="t1"),
        ),
        policy=policy,
    )
    assert decision.status == DecisionStatus.REQUIRE_APPROVAL
    assert decision.approval_required is True


@pytest.mark.asyncio
async def test_governance_blocks_cross_tenant_action():
    service = GovernanceService()
    with pytest.raises(TenantBoundaryError):
        await service.evaluate(
            actor=ActorContext(tenant_id="t1", user_id="u1"),
            action=ActionContext(
                action="read_lead",
                mode=ActionMode.READ,
                resource=ResourceRef(system="odoo", resource_type="crm.lead", resource_id="1", tenant_id="t2"),
            ),
            policy=GovernancePolicy(tenant_id="t1"),
        )
