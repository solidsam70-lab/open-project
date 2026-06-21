from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from .exceptions import ApprovalNotFoundError, InvalidApprovalDecisionError
from .interface import IApprovalRepository, IApprovalService
from .models import ApprovalDecision, ApprovalQuery, ApprovalRequest, ApprovalStatus

logger = logging.getLogger("jarvis.approvals")


class ApprovalService(IApprovalService):
    def __init__(self, repository: IApprovalRepository, audit_service=None):
        self.repository = repository
        self.audit_service = audit_service

    async def request_approval(self, request: ApprovalRequest) -> ApprovalRequest:
        if request.id is None:
            request.id = str(uuid.uuid4())
        request.status = ApprovalStatus.PENDING
        created = await self.repository.create(request)
        logger.info("Approval requested id=%s tenant=%s action=%s", created.id, created.tenant_id, created.action_type)
        await self._audit("approval.requested", created)
        return created

    async def decide(self, decision: ApprovalDecision) -> ApprovalRequest:
        approval = await self.repository.get(decision.tenant_id, decision.approval_id)
        if not approval:
            raise ApprovalNotFoundError(f"Approval not found: {decision.approval_id}")

        if approval.status != ApprovalStatus.PENDING:
            raise InvalidApprovalDecisionError(
                f"Approval {approval.id} is {approval.status}; only pending approvals can be decided."
            )

        if decision.decision not in {ApprovalStatus.APPROVED, ApprovalStatus.REJECTED}:
            raise InvalidApprovalDecisionError("Decision must be approved or rejected")

        approval.status = decision.decision
        approval.decision_note = decision.note
        approval.decided_by_user_id = decision.decided_by_user_id
        approval.decided_at = datetime.now(timezone.utc)
        updated = await self.repository.update(approval)
        logger.info("Approval decided id=%s decision=%s", approval.id, approval.status)
        await self._audit(f"approval.{approval.status.value}", updated)
        return updated

    async def _audit(self, action: str, approval: ApprovalRequest) -> None:
        if not self.audit_service:
            return
        await self.audit_service.log({
            "tenant_id": approval.tenant_id,
            "user_id": approval.decided_by_user_id or approval.requested_by_user_id,
            "action": action,
            "resource_type": "approval",
            "resource_id": approval.id,
            "details": approval.model_dump(mode="json"),
        })


class InMemoryApprovalRepository(IApprovalRepository):

    def __init__(self):
        self._items: dict[str, ApprovalRequest] = {}

    async def create(self, request: ApprovalRequest) -> ApprovalRequest:
        if request.id is None:
            request.id = str(uuid.uuid4())
        self._items[request.id] = request
        return request

    async def get(self, tenant_id: str, approval_id: str) -> ApprovalRequest | None:
        item = self._items.get(approval_id)
        if item and item.tenant_id == tenant_id:
            return item
        return None

    async def update(self, request: ApprovalRequest) -> ApprovalRequest:
        self._items[request.id] = request
        return request

    async def list(self, query: ApprovalQuery) -> list[ApprovalRequest]:
        items = [item for item in self._items.values() if item.tenant_id == query.tenant_id]
        if query.status:
            items = [item for item in items if item.status == query.status]
        if query.assigned_to_user_id:
            items = [item for item in items if item.assigned_to_user_id == query.assigned_to_user_id]
        if query.workflow_execution_id:
            items = [item for item in items if item.workflow_execution_id == query.workflow_execution_id]
        return items[query.offset: query.offset + query.limit]
