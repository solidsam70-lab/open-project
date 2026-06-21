import pytest
from jarvis.jarvis_core.router import IntentRouter, Intent, RouteMatch


class TestIntentRouter:

    @pytest.mark.asyncio
    async def test_register_and_route(self):
        router = IntentRouter()
        intent = Intent(
            name="test_intent",
            description="Test intent",
            agent_slug="test-agent",
            patterns=[r"test.*query", r"hello"],
            priority=5,
        )
        await router.register_intent(intent)

        match = await router.route("tenant-1", "this is a test query", {})
        assert match.agent_slug == "test-agent"
        assert match.confidence > 0
        assert match.intent.name == "test_intent"

    @pytest.mark.asyncio
    async def test_no_match_returns_default(self):
        router = IntentRouter()
        default = Intent(
            name="default",
            description="Default fallback",
            agent_slug="fallback-agent",
            patterns=["."],
            priority=0,
        )
        await router.register_intent(default)

        match = await router.route("tenant-1", "something random", {})
        assert match.agent_slug == "fallback-agent"

    @pytest.mark.asyncio
    async def test_higher_priority_wins(self):
        router = IntentRouter()
        low = Intent(name="low", description="Low priority", agent_slug="low-agent",
                     patterns=[r"help"], priority=1)
        high = Intent(name="high", description="High priority", agent_slug="high-agent",
                      patterns=[r"help"], priority=10)

        await router.register_intent(low)
        await router.register_intent(high)

        match = await router.route("tenant-1", "I need help", {})
        assert match.agent_slug == "high-agent"

    @pytest.mark.asyncio
    async def test_inactive_intent_not_matched(self):
        router = IntentRouter()
        intent = Intent(
            name="inactive",
            description="Inactive intent",
            agent_slug="ghost",
            patterns=[r"test"],
            is_active=False,
        )
        await router.register_intent(intent)

        with pytest.raises(ValueError):
            await router.route("tenant-1", "this is a test", {})

    def test_classify_intent(self):
        router = IntentRouter()

        assert router.classify_intent("find customer", "agent") == "search"
        assert router.classify_intent("create new invoice", "agent") == "create"
        assert router.classify_intent("update contact info", "agent") == "update"
        assert router.classify_intent("delete record", "agent") == "delete"
        assert router.classify_intent("show me the report", "agent") == "analyze"
        assert router.classify_intent("ETA compliance check", "comp") == "compliance"
        assert router.classify_intent("how are you", "agent") == "query"
