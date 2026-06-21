import pytest
from sqlalchemy import select

from jarvis.database.models import AgentRegistry as AgentRegistryDB, Tenant
from jarvis.jarvis_core.registry import AgentDefinition, AgentRegistryService


class TestAgentRegistry:

    @pytest.mark.asyncio
    async def test_register_agent(self, sync_db):
        agent_def = AgentDefinition(
            tenant_id="tenant-1",
            name="Sales Agent",
            slug="sales-agent",
            role="Sales Representative",
            goal="Close deals",
            status="active",
            kpis=[{"name": "deals_closed", "target": 10}],
            workflows=[{"name": "qualify_lead", "steps": []}],
        )

        result = sync_db.execute(select(AgentRegistryDB).where(
            AgentRegistryDB.slug == "sales-agent",
            AgentRegistryDB.tenant_id == "tenant-1",
        ))
        assert result.scalar_one_or_none() is not None

    @pytest.mark.asyncio
    async def test_agent_definition_validation(self):
        agent = AgentDefinition(
            tenant_id="t1",
            name="Test",
            slug="test",
            role="Tester",
            goal="Test things",
        )
        assert agent.status.value == "draft"
        assert agent.model == "gpt-4o"
        assert agent.temperature == 0.3

    def test_agent_kpis(self, agent_registry_data):
        agent = AgentDefinition(**agent_registry_data)
        assert len(agent.kpis) == 1
        assert agent.kpis[0]["name"] == "test_kpi"
        assert agent.kpis[0]["target"] == 100

    def test_agent_workflows_default(self):
        agent = AgentDefinition(
            tenant_id="t1", name="T", slug="t", role="R", goal="G"
        )
        assert agent.workflows == []

    def test_agent_serialization(self, agent_registry_data):
        agent = AgentDefinition(**agent_registry_data)
        data = agent.model_dump()
        assert data["name"] == "Test Agent"
        assert data["status"] == "active"


class TestAgentDefinition:

    def test_create_with_minimal_fields(self):
        agent = AgentDefinition(
            tenant_id="tenant-1",
            name="Minimal Agent",
            slug="minimal",
            role="Assistant",
            goal="Help users",
        )
        assert agent.id is None
        assert agent.kpis == []
        assert agent.tools == []
        assert agent.workflows == []
        assert agent.input_schema == {}
        assert agent.output_schema == {}
        assert agent.escalation_rules == []

    def test_create_with_full_fields(self):
        agent = AgentDefinition(
            tenant_id="tenant-1",
            name="Full Agent",
            slug="full",
            role="Full Role",
            goal="Full goal with detailed description",
            model="gpt-4",
            temperature=0.5,
            status="active",
            kpis=[{"name": "kpi1", "target": 90, "unit": "percent"}],
            tools=["tool1", "tool2"],
            workflows=[{"name": "wf1", "steps": [{"name": "step1"}]}],
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            escalation_rules=[{"condition": "error", "escalate_to": "admin"}],
        )
        assert agent.model == "gpt-4"
        assert agent.temperature == 0.5
        assert len(agent.tools) == 2
        assert len(agent.workflows) == 1
        assert len(agent.escalation_rules) == 1
