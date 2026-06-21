import logging
import re
from typing import Optional

from jarvis.jarvis_core.router.models import Intent, RouteMatch
from jarvis.jarvis_core.router.interface import IRouter

logger = logging.getLogger("jarvis.router")


class IntentRouter(IRouter):

    def __init__(self):
        self._intents: dict[str, Intent] = {}

    async def register_intent(self, intent: Intent) -> Intent:
        self._intents[intent.name] = intent
        logger.info("Registered intent: %s -> agent: %s", intent.name, intent.agent_slug)
        return intent

    async def route(self, tenant_id: str, query: str, context: dict) -> RouteMatch:
        best_match = None
        best_confidence = 0.0

        for intent in self._intents.values():
            if not intent.is_active:
                continue

            confidence = self._match_intent(query, intent, context)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = intent

        if not best_match:
            logger.warning("No intent matched for query: %s", query[:100])
            default_intent = self._intents.get("default")
            if default_intent:
                best_match = default_intent

        if best_match:
            return RouteMatch(
                intent=best_match,
                agent_slug=best_match.agent_slug,
                confidence=best_confidence,
                query=query,
                context=context,
            )

        raise ValueError(f"Unable to route query: no matching intent and no fallback")

    def _match_intent(self, query: str, intent: Intent, context: dict) -> float:
        query_lower = query.lower()

        for pattern in intent.patterns:
            try:
                if re.search(pattern, query_lower):
                    return intent.priority + 0.5
            except re.error:
                if pattern.lower() in query_lower:
                    return intent.priority + 0.3

        return 0.0

    async def classify_intent(self, query: str, agent_role: str) -> str:
        query_lower = query.lower()
        keywords = {
            "search": ["find", "search", "lookup", "get", "show"],
            "create": ["create", "new", "make", "add", "schedule"],
            "update": ["update", "change", "modify", "edit"],
            "delete": ["delete", "remove", "cancel"],
            "analyze": ["analyze", "report", "summary", "overview"],
            "compliance": ["compliance", "eta", "tax", "invoice"],
        }

        for intent_name, words in keywords.items():
            if any(w in query_lower for w in words):
                return intent_name

        return "query"
