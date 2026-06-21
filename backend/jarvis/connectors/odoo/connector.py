import logging
from typing import Any, Optional
import xmlrpc.client

from jarvis.connectors.base import ConnectorBase, ConnectorAuth, ConnectorResponse

logger = logging.getLogger("jarvis.connector.odoo")


class OdooConnector(ConnectorBase):

    def __init__(self, config: dict = None, auth: ConnectorAuth = None):
        super().__init__(config, auth)
        self._models = None
        self._uid = None
        self._url = None
        self._db = None
        self._common = None

    async def initialize(self) -> bool:
        try:
            creds = self.auth.credentials if self.auth else {}
            self._url = creds.get("url") or self.config.get("url", "http://localhost:8069")
            self._db = creds.get("db") or self.config.get("db", "")
            username = creds.get("username") or self.config.get("username", "")
            password = creds.get("password") or self.config.get("password", "")
            api_key = creds.get("api_key") or self.config.get("api_key", "")

            self._common = xmlrpc.client.ServerProxy(f"{self._url}/xmlrpc/2/common")

            if api_key:
                self._uid = self._common.authenticate(self._db, username, api_key, {})
            else:
                self._uid = self._common.authenticate(self._db, username, password, {})

            if not self._uid:
                logger.error("Odoo authentication failed for %s", username)
                return False

            self._models = xmlrpc.client.ServerProxy(f"{self._url}/xmlrpc/2/object")
            logger.info("Odoo connected: %s (uid: %s)", self._url, self._uid)
            return True

        except Exception as e:
            logger.error("Odoo initialization failed: %s", e)
            return False

    async def execute(self, action: str, params: dict) -> ConnectorResponse:
        if not self._models:
            success = await self.initialize()
            if not success:
                return ConnectorResponse(success=False, error="Odoo not initialized")

        try:
            action_map = {
                "search": self._search,
                "search_read": self._search_read,
                "create": self._create,
                "write": self._write,
                "unlink": self._unlink,
                "read": self._read,
                "fields_get": self._fields_get,
                "call_method": self._call_method,
            }

            handler = action_map.get(action)
            if not handler:
                return ConnectorResponse(success=False, error=f"Unknown Odoo action: {action}")

            result = await handler(params)
            return ConnectorResponse(success=True, data=result)

        except Exception as e:
            logger.error("Odoo action '%s' failed: %s", action, e)
            return ConnectorResponse(success=False, error=str(e))

    async def health_check(self) -> bool:
        try:
            if not self._common:
                return False
            version = self._common.version()
            return bool(version)
        except Exception:
            return False

    async def close(self) -> None:
        self._models = None
        self._uid = None

    async def _search(self, params: dict) -> list:
        model = params.get("model")
        domain = params.get("domain", [])
        offset = params.get("offset", 0)
        limit = params.get("limit", 80)
        order = params.get("order", None)

        args = [self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
                model, "search", domain, offset, limit]
        if order:
            args.append({"order": order})

        return self._models.execute_kw(*args)

    async def _search_read(self, params: dict) -> list[dict]:
        model = params.get("model")
        domain = params.get("domain", [])
        fields = params.get("fields", [])
        offset = params.get("offset", 0)
        limit = params.get("limit", 80)
        order = params.get("order", None)

        kwargs = {"offset": offset, "limit": limit}
        if fields:
            kwargs["fields"] = fields
        if order:
            kwargs["order"] = order

        return self._models.execute_kw(
            self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
            model, "search_read", [domain], kwargs
        )

    async def _create(self, params: dict) -> int:
        model = params.get("model")
        values = params.get("values", {})

        return self._models.execute_kw(
            self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
            model, "create", [values]
        )

    async def _write(self, params: dict) -> bool:
        model = params.get("model")
        ids = params.get("ids", [])
        values = params.get("values", {})

        return self._models.execute_kw(
            self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
            model, "write", [ids, values]
        )

    async def _unlink(self, params: dict) -> bool:
        model = params.get("model")
        ids = params.get("ids", [])

        return self._models.execute_kw(
            self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
            model, "unlink", [ids]
        )

    async def _read(self, params: dict) -> list:
        model = params.get("model")
        ids = params.get("ids", [])
        fields = params.get("fields", [])

        return self._models.execute_kw(
            self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
            model, "read", [ids], {"fields": fields} if fields else {}
        )

    async def _fields_get(self, params: dict) -> dict:
        model = params.get("model")
        attributes = params.get("attributes", ["string", "type", "required", "readonly"])

        return self._models.execute_kw(
            self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
            model, "fields_get", [], {"attributes": attributes}
        )

    async def _call_method(self, params: dict) -> Any:
        model = params.get("model")
        method = params.get("method")
        args = params.get("args", [])
        kwargs = params.get("kwargs", {})

        return self._models.execute_kw(
            self._db, self._uid, params.get("password", self.auth.credentials.get("password")),
            model, method, args, kwargs
        )
