from __future__ import annotations

from abc import ABC, abstractmethod
from .models import ActorContext, ActionContext, GovernanceDecision, GovernancePolicy


class IGovernanceService(ABC):
    @abstractmethod
    async def evaluate(
        self,
        *,
        actor: ActorContext,
        action: ActionContext,
        policy: GovernancePolicy,
    ) -> GovernanceDecision:
        ...
