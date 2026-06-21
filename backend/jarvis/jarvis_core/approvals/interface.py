from __future__ import annotations

from abc import ABC, abstractmethod
from .models import ApprovalDecision, ApprovalQuery, ApprovalRequest


class IApprovalRepository(ABC):
    @abstractmethod
    async def create(self, request: ApprovalRequest) -> ApprovalRequest:
        ...

    @abstractmethod
    async def get(self, tenant_id: str, approval_id: str) -> ApprovalRequest | None:
        ...

    @abstractmethod
    async def update(self, request: ApprovalRequest) -> ApprovalRequest:
        ...

    @abstractmethod
    async def list(self, query: ApprovalQuery) -> list[ApprovalRequest]:
        ...


class IApprovalService(ABC):
    @abstractmethod
    async def request_approval(self, request: ApprovalRequest) -> ApprovalRequest:
        ...

    @abstractmethod
    async def decide(self, decision: ApprovalDecision) -> ApprovalRequest:
        ...
