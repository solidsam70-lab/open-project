import pytest
from jarvis.jarvis_core.auth import LoginRequest, RegisterRequest, TokenResponse, AuthContext


class TestAuthModels:

    def test_login_request(self):
        req = LoginRequest(email="test@example.com", password="secret123")
        assert req.email == "test@example.com"
        assert req.password == "secret123"

    def test_register_request(self):
        req = RegisterRequest(
            email="new@example.com",
            password="pass123",
            display_name="New User",
            tenant_slug="test-company",
        )
        assert req.tenant_slug == "test-company"
        assert req.display_name == "New User"

    def test_token_response(self):
        resp = TokenResponse(
            access_token="eyJhbGciOiJIUzI1NiJ9.token",
            user_id="u1",
            tenant_id="t1",
            role="admin",
        )
        assert resp.token_type == "bearer"
        assert resp.expires_in == 3600

    def test_auth_context(self):
        ctx = AuthContext(
            user_id="u1",
            tenant_id="t1",
            tenant_slug="acme",
            email="admin@acme.com",
            role="admin",
            permissions=["read", "write", "admin"],
        )
        assert len(ctx.permissions) == 3
        assert "admin" in ctx.permissions
