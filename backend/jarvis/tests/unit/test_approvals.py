import pytest

from jarvis.jarvis_core.approvals import (
    ApprovalDecision,
    ApprovalRequest,
    ApprovalService,
    ApprovalStatus,
    InMemoryApprovalRepository,
)
from jarvis.jarvis_core.approvals.exceptions import InvalidApprovalDecisionError
from jarvis.jarvis_core.governance import RiskLevel


@pytest.mark.asyncio
async def test_approval_request_and_approve():
    service = ApprovalService(InMemoryApprovalRepository())
    approval = await service.request_approval(
        ApprovalRequest(
            tenant_id="t1",
            action_type="odoo.write",
            resource_system="odoo",
            resource_type="crm.lead",
            resource_id="1",
            proposed_payload={"stage_id": 3},
            risk_level=RiskLevel.MEDIUM,
            reason="CRM stage update requires approval",
        )
    )

    decided = await service.decide(
        ApprovalDecision(
            approval_id=approval.id,
            tenant_id="t1",
            decided_by_user_id="manager1",
            decision=ApprovalStatus.APPROVED,
            note="Approved",
        )
    )

    assert decided.status == ApprovalStatus.APPROVED
    assert decided.decided_by_user_id == "manager1"


@pytest.mark.asyncio
async def test_cannot_decide_approval_twice():
    service = ApprovalService(InMemoryApprovalRepository())
    approval = await service.request_approval(
        ApprovalRequest(
            tenant_id="t1",
            action_type="send.whatsapp",
            resource_system="whatsapp",
            resource_type="message",
            risk_level=RiskLevel.HIGH,
            reason="External message",
        )
    )
    decision = ApprovalDecision(
        approval_id=approval.id,
        tenant_id="t1",
        decided_by_user_id="manager1",
        decision=ApprovalStatus.REJECTED,
    )
    await service.decide(decision)
    with pytest.raises(InvalidApprovalDecisionError):
        await service.decide(decision)
