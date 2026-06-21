import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Float, Integer,
    ForeignKey, JSON, Enum as SAEnum, UniqueConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from jarvis.database.base import Base
import enum


def utcnow():
    return datetime.now(timezone.utc)


def new_uuid():
    return str(uuid.uuid4())


class TenantStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=new_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    domain = Column(String(255), unique=True)
    industry = Column(String(100))
    employee_count = Column(Integer, default=0)
    odoo_database_url = Column(String(500))
    odoo_api_key = Column(Text)
    status = Column(SAEnum(TenantStatus), default=TenantStatus.ACTIVE)
    config = Column(JSONB, default=dict)
    features = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    agents = relationship("AgentRegistry", back_populates="tenant", cascade="all, delete-orphan")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="tenant")
    memory_entries = relationship("MemoryEntry", back_populates="tenant")
    connector_configs = relationship("ConnectorConfig", back_populates="tenant")


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    AGENT = "agent"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255))
    role = Column(SAEnum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    preferences = Column(JSONB, default=dict)
    odoo_user_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tenant = relationship("Tenant", back_populates="users")
    conversations = relationship("Conversation", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_tenant_user_email"),
        Index("ix_users_tenant_email", "tenant_id", "email"),
    )


class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    ARCHIVED = "archived"


class AgentRegistry(Base):
    __tablename__ = "agent_registry"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, index=True)
    role = Column(String(255))
    goal = Column(Text)
    model = Column(String(100), default="gpt-4o")
    temperature = Column(Float, default=0.3)
    status = Column(SAEnum(AgentStatus), default=AgentStatus.DRAFT)
    agent_metadata = Column(JSONB, default=dict)
    config_path = Column(String(500))
    kpis = Column(JSONB, default=list)
    knowledge_sources = Column(JSONB, default=list)
    memory_sources = Column(JSONB, default=list)
    tools = Column(JSONB, default=list)
    workflows = Column(JSONB, default=list)
    input_schema = Column(JSONB, default=dict)
    output_schema = Column(JSONB, default=dict)
    escalation_rules = Column(JSONB, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tenant = relationship("Tenant", back_populates="agents")
    sessions = relationship("AgentSession", back_populates="agent", cascade="all, delete-orphan")
    executions = relationship("WorkflowExecution", back_populates="agent")

    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_tenant_agent_slug"),
    )


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(String, primary_key=True, default=new_uuid)
    agent_id = Column(String, ForeignKey("agent_registry.id"), nullable=False, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    context = Column(JSONB, default=dict)
    metadata_ = Column("metadata", JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), default=utcnow)
    ended_at = Column(DateTime(timezone=True))

    agent = relationship("AgentRegistry", back_populates="sessions")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    agent_id = Column(String, ForeignKey("agent_registry.id"), index=True)
    channel = Column(String(50), default="internal")
    channel_conversation_id = Column(String(255))
    title = Column(String(500))
    metadata_ = Column("metadata", JSONB, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_conversations_channel", "channel", "channel_conversation_id"),
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=new_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text")
    metadata_ = Column("metadata", JSONB, default=dict)
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(500))
    source_url = Column(String(1000))
    content_type = Column(String(50), default="text")
    content = Column(Text)
    metadata_ = Column("metadata", JSONB, default=dict)
    embedding_status = Column(String(20), default="pending")
    chunk_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tenant = relationship("Tenant", back_populates="knowledge_documents")
    chunks = relationship("KnowledgeChunk", back_populates="document", cascade="all, delete-orphan")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String, primary_key=True, default=new_uuid)
    document_id = Column(String, ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, default=dict)
    qdrant_point_id = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    document = relationship("KnowledgeDocument", back_populates="chunks")


class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agent_registry.id"), index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    memory_type = Column(String(50), nullable=False, index=True)
    key = Column(String(255), nullable=False)
    value = Column(JSONB, nullable=False)
    importance = Column(Float, default=0.5)
    context = Column(JSONB, default=dict)
    expires_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tenant = relationship("Tenant", back_populates="memory_entries")

    __table_args__ = (
        Index("ix_memory_lookup", "tenant_id", "agent_id", "memory_type", "key"),
    )


class ConnectorConfig(Base):
    __tablename__ = "connector_configs"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    connector_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    config = Column(JSONB, nullable=False)
    credentials = Column(JSONB, default=dict)
    is_enabled = Column(Boolean, default=True)
    last_sync_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    tenant = relationship("Tenant", back_populates="connector_configs")

    __table_args__ = (
        UniqueConstraint("tenant_id", "connector_type", "name", name="uq_tenant_connector"),
    )


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    agent_id = Column(String, ForeignKey("agent_registry.id"), nullable=False, index=True)
    workflow_name = Column(String(255), nullable=False)
    status = Column(String(20), default="pending")
    input_data = Column(JSONB, default=dict)
    output_data = Column(JSONB, default=dict)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True), default=utcnow)
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)

    agent = relationship("AgentRegistry", back_populates="executions")
    steps = relationship("ExecutionStep", back_populates="execution", cascade="all, delete-orphan")


class ExecutionStep(Base):
    __tablename__ = "execution_steps"

    id = Column(String, primary_key=True, default=new_uuid)
    execution_id = Column(String, ForeignKey("workflow_executions.id"), nullable=False, index=True)
    step_name = Column(String(255), nullable=False)
    step_type = Column(String(50))
    status = Column(String(20), default="pending")
    input_data = Column(JSONB, default=dict)
    output_data = Column(JSONB, default=dict)
    error = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    duration_ms = Column(Integer)

    execution = relationship("WorkflowExecution", back_populates="steps")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String)
    details = Column(JSONB, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    created_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_lookup", "tenant_id", "action", "created_at"),
    )
