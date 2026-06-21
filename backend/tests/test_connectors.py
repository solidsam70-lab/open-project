import pytest
from jarvis.connectors.base import ConnectorBase, ConnectorAuth, ConnectorResponse
from jarvis.connectors.odoo import OdooConnector
from jarvis.connectors.notion import NotionConnector
from jarvis.connectors.whatsapp import WhatsAppConnector


class TestConnectorFramework:

    def test_connector_base_abstract(self):
        with pytest.raises(TypeError):
            ConnectorBase()

    def test_connector_auth_creation(self):
        auth = ConnectorAuth(
            type="api_key",
            credentials={"api_key": "test-key-123"},
        )
        assert auth.type == "api_key"
        assert auth.credentials["api_key"] == "test-key-123"

    def test_connector_response_success(self):
        response = ConnectorResponse(success=True, data={"result": "ok"})
        assert response.success is True
        assert response.data["result"] == "ok"
        assert response.error is None

    def test_connector_response_error(self):
        response = ConnectorResponse(success=False, error="Something failed")
        assert response.success is False
        assert response.error == "Something failed"


class TestOdooConnector:

    def test_initialization(self):
        config = {"url": "http://localhost:8069", "db": "test_db"}
        auth = ConnectorAuth(type="basic", credentials={"username": "admin", "password": "admin"})
        connector = OdooConnector(config=config, auth=auth)
        assert connector.config["url"] == "http://localhost:8069"
        assert connector.auth.credentials["username"] == "admin"

    @pytest.mark.asyncio
    async def test_health_check_false(self):
        connector = OdooConnector()
        health = await connector.health_check()
        assert health is False


class TestNotionConnector:

    def test_initialization(self):
        auth = ConnectorAuth(type="api_key", credentials={"api_key": "secret"})
        connector = NotionConnector(auth=auth)
        assert connector.auth.credentials["api_key"] == "secret"


class TestWhatsAppConnector:

    def test_initialization(self):
        config = {"phone_number_id": "123", "access_token": "token"}
        connector = WhatsAppConnector(config=config)
        assert connector.config["phone_number_id"] == "123"

    @pytest.mark.asyncio
    async def test_health_check_false(self):
        connector = WhatsAppConnector()
        health = await connector.health_check()
        assert health is False
