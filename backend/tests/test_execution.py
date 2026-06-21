import pytest
from jarvis.jarvis_core.execution import ExecutionRequest, ExecutionResult, WorkflowStep


class TestExecutionModels:

    def test_execution_request_creation(self):
        request = ExecutionRequest(
            tenant_id="t1",
            agent_slug="test-agent",
            workflow_name="test_workflow",
            input_data={"key": "value"},
        )
        assert request.tenant_id == "t1"
        assert request.agent_slug == "test-agent"
        assert request.input_data["key"] == "value"

    def test_execution_result_defaults(self):
        from datetime import datetime
        result = ExecutionResult(
            id="exec-1",
            tenant_id="t1",
            agent_slug="agent",
            workflow_name="wf",
            status="pending",
            started_at=datetime.now(),
        )
        assert result.output_data == {}
        assert result.steps == []
        assert result.error is None
        assert result.duration_ms is None

    def test_workflow_step_defaults(self):
        step = WorkflowStep(
            name="test_step",
            step_type="action",
        )
        assert step.input_data == {}
        assert step.output_data == {}
        assert step.status == "pending"
        assert step.error is None

    def test_execution_with_steps(self):
        from datetime import datetime
        step = WorkflowStep(name="step1", status="completed")
        result = ExecutionResult(
            id="exec-2",
            tenant_id="t1",
            agent_slug="agent",
            workflow_name="wf",
            status="completed",
            steps=[step],
            started_at=datetime.now(),
            completed_at=datetime.now(),
        )
        assert len(result.steps) == 1
        assert result.steps[0].name == "step1"
