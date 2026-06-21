import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

Base = declarative_base()

DATABASE_URL = os.getenv(
    "JARVIS_DATABASE_URL",
    "postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis"
)
DATABASE_URL_SYNC = os.getenv(
    "JARVIS_DATABASE_URL_SYNC",
    "postgresql+psycopg2://jarvis:jarvis@localhost:5432/jarvis"
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_size=20, max_overflow=10)
sync_engine = create_engine(DATABASE_URL_SYNC, echo=False, pool_size=20, max_overflow=10)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
SyncSession = sessionmaker(bind=sync_engine)


async def get_db():
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_db():
    session = SyncSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_db():
    async with engine.begin() as conn:
        from jarvis.database.models import (
            Tenant, User, AgentRegistry, AgentSession,
            KnowledgeDocument, KnowledgeChunk,
            MemoryEntry, Conversation, Message,
            ConnectorConfig, AuditLog, WorkflowExecution,
            ExecutionStep
        )
        await conn.run_sync(Base.metadata.create_all)
