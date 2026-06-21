import logging
from typing import Optional

from jarvis.connectors.base import ConnectorBase, ConnectorAuth, ConnectorResponse

logger = logging.getLogger("jarvis.connector.notion")


class NotionConnector(ConnectorBase):

    def __init__(self, config: dict = None, auth: ConnectorAuth = None):
        super().__init__(config, auth)
        self._client = None

    async def initialize(self) -> bool:
        try:
            api_key = None
            if self.auth:
                api_key = self.auth.credentials.get("api_key")
            if not api_key:
                api_key = self.config.get("api_key")

            if not api_key:
                logger.error("Notion API key not configured")
                return False

            try:
                from notion_client import Client
                self._client = Client(auth=api_key)
                logger.info("Notion connector initialized")
                return True
            except ImportError:
                logger.warning("notion-client not installed, using mock")
                self._client = None
                return True

        except Exception as e:
            logger.error("Notion initialization failed: %s", e)
            return False

    async def execute(self, action: str, params: dict) -> ConnectorResponse:
        try:
            action_map = {
                "search": self._search,
                "query_database": self._query_database,
                "get_page": self._get_page,
                "create_page": self._create_page,
                "update_page": self._update_page,
                "get_database": self._get_database,
                "list_databases": self._list_databases,
                "get_block_children": self._get_block_children,
            }

            handler = action_map.get(action)
            if not handler:
                return ConnectorResponse(success=False, error=f"Unknown Notion action: {action}")

            result = await handler(params)
            return ConnectorResponse(success=True, data=result)

        except Exception as e:
            logger.error("Notion action '%s' failed: %s", action, e)
            return ConnectorResponse(success=False, error=str(e))

    async def health_check(self) -> bool:
        return self._client is not None

    async def close(self) -> None:
        self._client = None

    async def _search(self, params: dict) -> dict:
        query = params.get("query", "")
        if not self._client:
            return {"results": [], "note": "notion-client not installed"}
        return self._client.search(query=query, **params.get("kwargs", {}))

    async def _query_database(self, params: dict) -> dict:
        database_id = params.get("database_id")
        if not database_id:
            raise ValueError("database_id required")
        if not self._client:
            return {"results": [], "note": "notion-client not installed"}
        return self._client.databases.query(
            database_id=database_id,
            **params.get("kwargs", {})
        )

    async def _get_page(self, params: dict) -> dict:
        page_id = params.get("page_id")
        if not page_id:
            raise ValueError("page_id required")
        if not self._client:
            return {"note": "notion-client not installed"}
        return self._client.pages.retrieve(page_id=page_id)

    async def _create_page(self, params: dict) -> dict:
        parent = params.get("parent")
        properties = params.get("properties", {})
        if not parent:
            raise ValueError("parent required")
        if not self._client:
            return {"note": "notion-client not installed"}
        return self._client.pages.create(
            parent=parent,
            properties=properties,
            children=params.get("children"),
        )

    async def _update_page(self, params: dict) -> dict:
        page_id = params.get("page_id")
        properties = params.get("properties", {})
        if not page_id:
            raise ValueError("page_id required")
        if not self._client:
            return {"note": "notion-client not installed"}
        return self._client.pages.update(page_id=page_id, properties=properties)

    async def _get_database(self, params: dict) -> dict:
        database_id = params.get("database_id")
        if not database_id:
            raise ValueError("database_id required")
        if not self._client:
            return {"note": "notion-client not installed"}
        return self._client.databases.retrieve(database_id=database_id)

    async def _list_databases(self, params: dict) -> dict:
        if not self._client:
            return {"results": [], "note": "notion-client not installed"}
        return self._client.search(filter={"value": "database", "property": "object"})

    async def _get_block_children(self, params: dict) -> dict:
        block_id = params.get("block_id")
        if not block_id:
            raise ValueError("block_id required")
        if not self._client:
            return {"results": [], "note": "notion-client not installed"}
        return self._client.blocks.children.list(block_id=block_id)
