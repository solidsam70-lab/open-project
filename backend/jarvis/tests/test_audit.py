import pytest
from jarvis.jarvis_core.audit import AuditEntry


class TestAudit:

    def test_create_audit_entry(self):
        entry = AuditEntry(
            tenant_id="t1",
            user_id="u1",
            action="user.login",
            resource_type="session",
            resource_id="sess-1",
            details={"ip": "192.168.1.1"},
        )
        assert entry.action == "user.login"
        assert entry.details["ip"] == "192.168.1.1"

    def test_audit_with_ip(self):
        entry = AuditEntry(
            tenant_id="t1",
            action="api.call",
            ip_address="10.0.0.1",
            user_agent="JARVIS-Test/1.0",
        )
        assert entry.ip_address == "10.0.0.1"
        assert entry.user_agent == "JARVIS-Test/1.0"

    def test_audit_defaults(self):
        entry = AuditEntry(
            tenant_id="t1",
            action="test.action",
        )
        assert entry.details == {}
        assert entry.user_id is None
        assert entry.resource_id is None
