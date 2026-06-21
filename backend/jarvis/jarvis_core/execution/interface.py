from abc import ABC, abstractmethod
from typing import Optional
from jarvis.jarvis_core.execution.models import ExecutionRequest, ExecutionResult


class IExecutionEngine(ABC):

    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...

    @abstractmethod
    async def get_result(self, execution_id: str) -> Optional[ExecutionResult]:
        ...
