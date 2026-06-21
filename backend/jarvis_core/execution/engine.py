import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from jarvis.database.models import WorkflowExecution as WorkflowExecutionDB, ExecutionStep as ExecutionStepDB
from jarvis.jarvis_core.execution.models import ExecutionRequest, ExecutionResult, WorkflowStep
from jarvis.jarvis_core.execution.interface import IExecutionEngine
from jarvis.jarvis_core.registry import AgentRegistryService
from jarvis.jarvis_core.router import IntentRouter
from jarvis.jarvis_core.memory import MemoryService
from jarvis.jarvis_core.knowledge import KnowledgeService
from jarvis.connectors.base import ConnectorBase

logger = logging.getLogger("jarvis.execution")


class ExecutionEngine(IExecutionEngine):

    def __init__(
        self,
        db: AsyncSession,
        agent_registry: AgentRegistryService,
        router: IntentRouter,
        memory: MemoryService,
        knowledge: KnowledgeService,
        connectors: dict[str, ConnectorBase],
        llm_client=None,
    ):
        self.db = db
        self.agent_registry = agent_registry
        self.router = router
        self.memory = memory
        self.knowledge = knowledge
        self.connectors = connectors
        self.llm_client = llm_client

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        execution_id = str(uuid.uuid4())
        start_time = time.time()

        agent = await self.agent_registry.get_by_slug(request.tenant_id, request.agent_slug)
        if not agent:
            raise ValueError(f"Agent not found: {request.agent_slug}")

        workflow = None
        for w in agent.workflows:
            if w.get("name") == request.workflow_name:
                workflow = w
                break

        if not workflow:
            raise ValueError(
                f"Workflow '{request.workflow_name}' not found for agent '{request.agent_slug}'"
            )

        db_execution = WorkflowExecutionDB(
            id=execution_id,
            tenant_id=request.tenant_id,
            agent_id=agent.id,
            workflow_name=request.workflow_name,
            status="running",
            input_data=request.input_data,
        )
        self.db.add(db_execution)
        await self.db.flush()

        steps = []
        try:
            for step_def in workflow.get("steps", []):
                step_start = time.time()
                step = WorkflowStep(
                    name=step_def.get("name", "unnamed"),
                    step_type=step_def.get("type", "action"),
                    status="running",
                    started_at=datetime.now(timezone.utc),
                )

                db_step = ExecutionStepDB(
                    execution_id=execution_id,
                    step_name=step.name,
                    step_type=step.step_type,
                    status="running",
                    started_at=datetime.now(timezone.utc),
                )
                self.db.add(db_step)
                await self.db.flush()

                try:
                    output = await self._execute_step(step_def, request, agent)
                    step.status = "completed"
                    step.output_data = output or {}
                    step.completed_at = datetime.now(timezone.utc)
                    step.duration_ms = int((time.time() - step_start) * 1000)

                    db_step.status = "completed"
                    db_step.output_data = output or {}
                    db_step.completed_at = step.completed_at
                    db_step.duration_ms = step.duration_ms
                except Exception as e:
                    step.status = "failed"
                    step.error = str(e)
                    step.completed_at = datetime.now(timezone.utc)
                    step.duration_ms = int((time.time() - step_start) * 1000)

                    db_step.status = "failed"
                    db_step.error = str(e)
                    db_step.completed_at = step.completed_at
                    db_step.duration_ms = step.duration_ms

                    escalation = await self._check_escalation(agent, step_def, e)
                    if escalation:
                        logger.warning("Escalation triggered for step %s: %s", step.name, escalation)

                    if not workflow.get("continue_on_failure", False):
                        raise

                finally:
                    steps.append(step)
                    await self.db.flush()

            status = "completed"
            output_data = steps[-1].output_data if steps else {}
        except Exception as e:
            status = "failed"
            output_data = {}
            logger.error("Workflow %s failed: %s", request.workflow_name, str(e))

            db_execution.error = str(e)

        duration = int((time.time() - start_time) * 1000)
        db_execution.status = status
        db_execution.output_data = output_data
        db_execution.completed_at = datetime.now(timezone.utc)
        db_execution.duration_ms = duration
        await self.db.flush()

        return ExecutionResult(
            id=execution_id,
            tenant_id=request.tenant_id,
            agent_slug=request.agent_slug,
            workflow_name=request.workflow_name,
            status=status,
            output_data=output_data,
            steps=steps,
            error=db_execution.error,
            started_at=db_execution.started_at,
            completed_at=db_execution.completed_at,
            duration_ms=duration,
        )

    async def get_result(self, execution_id: str) -> Optional[ExecutionResult]:
        from sqlalchemy import select

        result = await self.db.execute(
            select(WorkflowExecutionDB).where(WorkflowExecutionDB.id == execution_id)
        )
        db_exec = result.scalar_one_or_none()
        if not db_exec:
            return None

        steps_result = await self.db.execute(
            select(ExecutionStepDB)
            .where(ExecutionStepDB.execution_id == execution_id)
            .order_by(ExecutionStepDB.started_at)
        )
        steps = [
            WorkflowStep(
                name=s.step_name,
                step_type=s.step_type or "action",
                input_data=s.input_data or {},
                output_data=s.output_data or {},
                status=s.status,
                error=s.error,
                started_at=s.started_at,
                completed_at=s.completed_at,
                duration_ms=s.duration_ms,
            )
            for s in steps_result.scalars().all()
        ]

        return ExecutionResult(
            id=db_exec.id,
            tenant_id=db_exec.tenant_id,
            agent_slug=db_exec.agent_id,
            workflow_name=db_exec.workflow_name,
            status=db_exec.status,
            output_data=db_exec.output_data or {},
            steps=steps,
            error=db_exec.error,
            started_at=db_exec.started_at,
            completed_at=db_exec.completed_at,
            duration_ms=db_exec.duration_ms,
        )

    async def _execute_step(self, step_def: dict, request: ExecutionRequest, agent) -> dict:
        step_type = step_def.get("type", "action")

        if step_type == "llm":
            return await self._execute_llm_step(step_def, request, agent)
        elif step_type == "connector":
            return await self._execute_connector_step(step_def, request)
        elif step_type == "tool":
            return await self._execute_tool_step(step_def, request)
        elif step_type == "condition":
            return await self._execute_condition_step(step_def, request)
        else:
            return {"status": "skipped", "reason": f"Unknown step type: {step_type}"}

    async def _execute_llm_step(self, step_def: dict, request: ExecutionRequest, agent) -> dict:
        if not self.llm_client:
            return {"status": "skipped", "reason": "No LLM client configured"}

        system_prompt = step_def.get("system_prompt", agent.goal)
        user_prompt = step_def.get("user_prompt", "")
        formatted_prompt = user_prompt.format(**request.input_data)

        relevant_knowledge = await self.knowledge.search(
            tenant_id=request.tenant_id,
            query=formatted_prompt,
            limit=5,
        )

        context_memory = await self.memory.get_recent(
            tenant_id=request.tenant_id,
            agent_id=agent.id,
            limit=10,
        )

        full_context = (
            f"Agent Role: {agent.role}\n\n"
            f"Knowledge:\n{relevant_knowledge}\n\n"
            f"Recent Context:\n{context_memory}\n\n"
            f"Input: {formatted_prompt}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_context},
        ]

        response = await self.llm_client.chat(
            messages=messages,
            model=agent.model,
            temperature=agent.temperature,
        )

        return {
            "response": response.get("content", ""),
            "tokens_used": response.get("tokens", 0),
        }

    async def _execute_connector_step(self, step_def: dict, request: ExecutionRequest) -> dict:
        connector_type = step_def.get("connector")
        action = step_def.get("action")
        params = step_def.get("params", {})

        connector = self.connectors.get(connector_type)
        if not connector:
            raise ValueError(f"Connector not found: {connector_type}")

        merged_params = {**params, **request.input_data.get(connector_type, {})}
        result = await connector.execute(action, merged_params)
        return {"connector": connector_type, "action": action, "result": result}

    async def _execute_tool_step(self, step_def: dict, request: ExecutionRequest) -> dict:
        tool_name = step_def.get("tool")
        params = step_def.get("params", {})
        merged_params = {**params, **request.input_data.get("tool_params", {})}
        return {"tool": tool_name, "result": merged_params}

    async def _execute_condition_step(self, step_def: dict, request: ExecutionRequest) -> dict:
        condition = step_def.get("condition", "")
        try:
            result = eval(condition, {"__builtins__": {}}, request.input_data)
            return {"condition": condition, "result": bool(result)}
        except Exception as e:
            return {"condition": condition, "result": False, "error": str(e)}

    async def _check_escalation(self, agent, step_def: dict, error: Exception) -> Optional[str]:
        for rule in agent.escalation_rules:
            if rule.get("on_error") and error.__class__.__name__ in rule.get("error_types", []):
                logger.warning("Escalating to %s: %s", rule.get("escalate_to"), error)
                return rule.get("escalate_to")
        return None
