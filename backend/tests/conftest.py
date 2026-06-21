import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from jarvis.database.base import Base


@pytest.fixture
def sync_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def agent_registry_data():
    return {
        "tenant_id": "test-tenant-1",
        "name": "Test Agent",
        "slug": "test-agent",
        "role": "Test Role",
        "goal": "Test goal",
        "status": "active",
        "kpis": [{"name": "test_kpi", "target": 100}],
        "tools": ["test_tool"],
        "workflows": [],
    }


@pytest.fixture
def tenant_data():
    return {
        "id": "test-tenant-1",
        "name": "Test Company",
        "slug": "test-company",
        "industry": "Technology",
    }


@pytest.fixture
def user_data():
    return {
        "tenant_id": "test-tenant-1",
        "email": "test@example.com",
        "password_hash": "$2b$12$test",
        "display_name": "Test User",
        "role": "admin",
    }
