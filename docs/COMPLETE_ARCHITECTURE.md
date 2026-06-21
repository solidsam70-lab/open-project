# JARVIS — Complete Architectural Documentation

> **Generated**: 2026-06-21  
> **Version**: 1.0.0  
> **Project**: JARVIS — AI Operating System for AKS Solutions  
> **Repository**: `https://github.com/aks-solutions/jarvis`

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Complete File Tree](#2-complete-file-tree)
3. [Layer Architecture](#3-layer-architecture)
4. [Database Schema](#4-database-schema)
5. [API Reference](#5-api-reference)
6. [Agent Framework](#6-agent-framework)
7. [MVP Agents](#7-mvp-agents)
8. [AKS Business Agents](#8-aks-business-agents)
9. [Connector Reference](#9-connector-reference)
10. [Revenue Workflows](#10-revenue-workflows)
11. [Multi-Tenant Design](#11-multi-tenant-design)
12. [Deployment](#12-deployment)
13. [Test Suite](#13-test-suite)

---

## 1. System Overview

**JARVIS** (Joint Automated Reasoning & Virtual Intelligence System) is an AI Operating System purpose-built for **AKS Solutions**. It sits on top of the Odoo ERP and becomes the primary interface employees use to access knowledge, execute workflows, receive recommendations, and interact with business systems.

### Mission

Empower **Egyptian SMEs** (Small and Medium Enterprises) with enterprise-grade AI capabilities by:

- Automating Odoo implementation, configuration, and support
- Ensuring Egypt ETA (Egyptian Tax Authority) e-invoicing compliance
- Delivering intelligent lead qualification, outreach, and sales workflows
- Providing real-time business intelligence and executive dashboards
- Integrating seamlessly with Odoo, Notion, Gmail, WhatsApp, and GitHub

### Target Market

- **Geography**: Egypt (primary), MENA region (expansion)
- **Company Size**: 20–500 employees
- **Industries**: Real Estate, Trading, Manufacturing, Construction, Healthcare, IT, F&B
- **Budget Range**: 15,000–250,000 EGP per engagement

### Architecture Visual

```
┌──────────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │  Auth    │ │  Agents  │ │Execution │ │Knowledge/Memory  │ │
│  │  Routes  │ │  Routes  │ │ Routes   │ │ Routes           │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
├──────────────────────────────────────────────────────────────┤
│                  Authentication Layer (JWT)                   │
│           Multi-tenant · Role-based · Token scoping           │
├──────────────────────────────────────────────────────────────┤
│                    Agent Registry                             │
│       Pydantic models · SQLAlchemy persistence · JSON load    │
├──────────────────────────────────────────────────────────────┤
│                    Workflow Engine                            │
│    LLM steps · Connector steps · Tool steps · Conditions      │
│      Step isolation · Escalation · Continue-on-failure        │
├──────────────────────┬───────────────────────────────────────┤
│    Knowledge Engine   │        Memory Engine                  │
│   RAG · Chunking      │  Importance scoring · TTL · Types    │
│   Vector + Keyword    │  Short-term · Long-term · Episodic   │
├──────────────────────┴───────────────────────────────────────┤
│                   Connector Layer                             │
│  Odoo (XML-RPC) · Notion · WhatsApp · Gmail · GitHub         │
├──────────────────────────────────────────────────────────────┤
│                  Odoo Integration Layer                       │
│        search · search_read · create · write · unlink         │
│        read · fields_get · call_method                        │
├──────────────────────────────────────────────────────────────┤
│                 Notification Layer (planned)                  │
│        Multi-channel routing: Slack, Email, WhatsApp          │
└──────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component       | Technology                                          |
|-----------------|-----------------------------------------------------|
| Backend         | Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic      |
| AI              | OpenAI (GPT-4o), Qdrant vector DB, LangChain        |
| Database        | PostgreSQL 16, Redis 7                              |
| Auth            | JWT (python-jose), bcrypt (passlib)                 |
| Task Queue      | Celery (configured)                                 |
| Monitoring      | Sentry, Prometheus, Loguru                          |
| Testing         | pytest, pytest-asyncio, pytest-cov                  |
| Deployment      | Docker, Docker Compose                              |

---

## 2. Complete File Tree

Every file in the project with a one-line description.

### Root

| #  | File Path                                         | Description                                      |
|----|---------------------------------------------------|--------------------------------------------------|
| 1  | `/home/amir/jarvis/README.md`                     | Project overview, architecture, quick start guide |
| 2  | `/home/amir/jarvis/docker-compose.yml`            | Multi-service Docker orchestration (4 services)  |

### Backend Root

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 3  | `/home/amir/jarvis/backend/__init__.py`                   | Empty package init                                |
| 4  | `/home/amir/jarvis/backend/Dockerfile`                    | Python 3.12-slim Docker build for API + worker   |
| 5  | `/home/amir/jarvis/backend/requirements.txt`              | Python dependencies (37 packages)                |
| 6  | `/home/amir/jarvis/backend/.env.example`                  | Environment variable template                    |
| 7  | `/home/amir/jarvis/backend/alembic.ini`                   | Alembic migration configuration                  |

### API Layer

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 8  | `/home/amir/jarvis/backend/api/__init__.py`               | Empty package init                                |
| 9  | `/home/amir/jarvis/backend/api/main.py`                   | FastAPI app factory, lifespan, CORS, global errors|
| 10 | `/home/amir/jarvis/backend/api/dependencies.py`           | Dependency injection: auth, registry, services    |
| 11 | `/home/amir/jarvis/backend/api/v1/__init__.py`            | APIRouter aggregator for all v1 routes            |
| 12 | `/home/amir/jarvis/backend/api/v1/auth.py`                | Login/register endpoints per tenant               |
| 13 | `/home/amir/jarvis/backend/api/v1/agents.py`              | Agent CRUD + load-config endpoints                |
| 14 | `/home/amir/jarvis/backend/api/v1/connectors.py`          | Connector configure/list/delete endpoints         |
| 15 | `/home/amir/jarvis/backend/api/v1/execution.py`           | Workflow execution run/get endpoints              |
| 16 | `/home/amir/jarvis/backend/api/v1/knowledge.py`           | Knowledge ingest/search/get/delete endpoints      |
| 17 | `/home/amir/jarvis/backend/api/v1/memory.py`              | Memory store/recent/search/forget endpoints       |

### Database

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 18 | `/home/amir/jarvis/backend/database/__init__.py`          | Re-exports engine, session, models               |
| 19 | `/home/amir/jarvis/backend/database/base.py`              | SQLAlchemy declarative base                       |
| 20 | `/home/amir/jarvis/backend/database/session.py`           | Async + sync engine, session factories, init_db  |
| 21 | `/home/amir/jarvis/backend/database/models.py`            | All 15 SQLAlchemy ORM models                     |

### Database Migrations

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 22 | `/home/amir/jarvis/backend/database/migrations/env.py`    | Alembic environment config                       |
| 23 | `/home/amir/jarvis/backend/database/migrations/script.py.mako` | Alembic migration template                 |

### Core (`jarvis_core`)

#### Agent Registry

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 24 | `/home/amir/jarvis/backend/jarvis_core/__init__.py`       | Top-level exports (Registry, Router, Engine, etc)|
| 25 | `/home/amir/jarvis/backend/jarvis_core/registry/__init__.py` | Exports AgentDefinition, AgentStatus, Service |
| 26 | `/home/amir/jarvis/backend/jarvis_core/registry/models.py`  | AgentDefinition Pydantic model with all fields |
| 27 | `/home/amir/jarvis/backend/jarvis_core/registry/interface.py` | IAgentRegistry abstract interface (7 methods)|
| 28 | `/home/amir/jarvis/backend/jarvis_core/registry/service.py`  | AgentRegistryService: register, get, list, update, delete, load_from_config, _to_definition |

#### Authentication

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 29 | `/home/amir/jarvis/backend/jarvis_core/auth/__init__.py`  | Exports all auth models + service                |
| 30 | `/home/amir/jarvis/backend/jarvis_core/auth/models.py`    | LoginRequest, RegisterRequest, TokenResponse, AuthContext, TenantAuth |
| 31 | `/home/amir/jarvis/backend/jarvis_core/auth/interface.py` | IAuthService abstract interface (3 methods)      |
| 32 | `/home/amir/jarvis/backend/jarvis_core/auth/service.py`   | AuthService: authenticate, validate_token, register_user, JWT creation |

#### Workflow Execution

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 33 | `/home/amir/jarvis/backend/jarvis_core/execution/__init__.py` | Exports ExecutionRequest, ExecutionResult, WorkflowStep, Engine |
| 34 | `/home/amir/jarvis/backend/jarvis_core/execution/models.py` | ExecutionRequest, ExecutionResult, WorkflowStep Pydantic models |
| 35 | `/home/amir/jarvis/backend/jarvis_core/execution/interface.py` | IExecutionEngine abstract interface (2 methods)|
| 36 | `/home/amir/jarvis/backend/jarvis_core/execution/engine.py` | ExecutionEngine: full workflow execution with LLM, connector, tool, condition steps; escalation checks |

#### Knowledge Engine

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 37 | `/home/amir/jarvis/backend/jarvis_core/knowledge/__init__.py` | Exports KnowledgeDocument, KnowledgeChunk, KnowledgeSearchResult, Service |
| 38 | `/home/amir/jarvis/backend/jarvis_core/knowledge/models.py` | KnowledgeDocument, KnowledgeChunk, KnowledgeSearchResult |
| 39 | `/home/amir/jarvis/backend/jarvis_core/knowledge/interface.py` | IKnowledgeService abstract interface (4 methods)|
| 40 | `/home/amir/jarvis/backend/jarvis_core/knowledge/loader.py` | KnowledgeService: ingest, chunk_text, vector/keyword search, delete, get_document |

#### Memory Engine

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 41 | `/home/amir/jarvis/backend/jarvis_core/memory/__init__.py` | Exports MemoryEntry, MemorySearchResult, Service |
| 42 | `/home/amir/jarvis/backend/jarvis_core/memory/models.py`  | MemoryEntry (with importance, TTL), MemorySearchResult |
| 43 | `/home/amir/jarvis/backend/jarvis_core/memory/interface.py` | IMemoryService abstract interface (4 methods)  |
| 44 | `/home/amir/jarvis/backend/jarvis_core/memory/service.py` | MemoryService: store, get_recent, search, forget |

#### Intent Router

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 45 | `/home/amir/jarvis/backend/jarvis_core/router/__init__.py` | Exports Intent, RouteMatch, IntentRouter        |
| 46 | `/home/amir/jarvis/backend/jarvis_core/router/models.py`  | Intent (patterns, priority) and RouteMatch      |
| 47 | `/home/amir/jarvis/backend/jarvis_core/router/interface.py` | IRouter abstract interface (3 methods)          |
| 48 | `/home/amir/jarvis/backend/jarvis_core/router/service.py` | IntentRouter: regex-based routing, intent classification (search/create/update/delete/analyze/compliance) |

#### Audit

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 49 | `/home/amir/jarvis/backend/jarvis_core/audit/__init__.py` | Exports AuditEntry, AuditService                 |
| 50 | `/home/amir/jarvis/backend/jarvis_core/audit/models.py`   | AuditEntry Pydantic model                        |
| 51 | `/home/amir/jarvis/backend/jarvis_core/audit/service.py`  | AuditService: log and query                      |

#### Prompts

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 52 | `/home/amir/jarvis/backend/jarvis_core/prompts/__init__.py` | System prompts for 6 MVP agents                  |

### Connectors

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 53 | `/home/amir/jarvis/backend/connectors/__init__.py`        | Exports ConnectorBase + all 5 connector classes  |
| 54 | `/home/amir/jarvis/backend/connectors/base.py`            | ConnectorBase ABC, ConnectorAuth, ConnectorResponse |
| 55 | `/home/amir/jarvis/backend/connectors/odoo/__init__.py`   | OdooConnector re-export                          |
| 56 | `/home/amir/jarvis/backend/connectors/odoo/connector.py`  | Odoo XML-RPC: search, search_read, create, write, unlink, read, fields_get, call_method |
| 57 | `/home/amir/jarvis/backend/connectors/notion/__init__.py` | NotionConnector re-export                        |
| 58 | `/home/amir/jarvis/backend/connectors/notion/connector.py`| Notion API: search, query_database, CRUD pages, list_databases, block children |
| 59 | `/home/amir/jarvis/backend/connectors/whatsapp/__init__.py` | WhatsAppConnector re-export                    |
| 60 | `/home/amir/jarvis/backend/connectors/whatsapp/connector.py` | WhatsApp Cloud API: send_text, send_template, send_image, send_document, send_button, mark_as_read, webhook verify, HMAC signature |
| 61 | `/home/amir/jarvis/backend/connectors/gmail/__init__.py`  | GmailConnector re-export                         |
| 62 | `/home/amir/jarvis/backend/connectors/gmail/connector.py` | Gmail API: send_email, list/get/search messages, create_draft, mark_as_read, trash, list_labels |
| 63 | `/home/amir/jarvis/backend/connectors/github/__init__.py` | GitHubConnector re-export                        |
| 64 | `/home/amir/jarvis/backend/connectors/github/connector.py`| GitHub API: repo ops, issues, PRs, file content, webhooks, commits, branches, code search |

### Tests

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 65 | `/home/amir/jarvis/backend/tests/__init__.py`             | Empty package init                                |
| 66 | `/home/amir/jarvis/backend/tests/conftest.py`             | Fixtures: sync_db (SQLite), agent_registry_data, tenant_data, user_data |
| 67 | `/home/amir/jarvis/backend/tests/test_auth.py`            | Tests for auth models (LoginRequest, RegisterRequest, TokenResponse, AuthContext) |
| 68 | `/home/amir/jarvis/backend/tests/test_registry.py`        | Tests for AgentDefinition, AgentRegistryService, serialization, validation |
| 69 | `/home/amir/jarvis/backend/tests/test_execution.py`       | Tests for ExecutionRequest, ExecutionResult, WorkflowStep models |
| 70 | `/home/amir/jarvis/backend/tests/test_knowledge.py`       | Tests for chunk_text logic and KnowledgeDocument model |
| 71 | `/home/amir/jarvis/backend/tests/test_memory.py`          | Tests for MemoryEntry model (importance, TTL, types) |
| 72 | `/home/amir/jarvis/backend/tests/test_router.py`          | Tests for IntentRouter: register, route, priority, inactive intents, classify_intent |
| 73 | `/home/amir/jarvis/backend/tests/test_connectors.py`      | Tests for ConnectorBase, ConnectorAuth, ConnectorResponse, Odoo/Notion/WhatsApp init |
| 74 | `/home/amir/jarvis/backend/tests/test_audit.py`           | Tests for AuditEntry creation, IP, defaults |

### Agent JSON Configurations (MVP)

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 75 | `/home/amir/jarvis/agents/chief_of_staff.json`            | Chief of Staff agent: coordination, delegation, daily briefing |
| 76 | `/home/amir/jarvis/agents/odooconsultant.json`            | Odoo Consultant: discovery, configuration, troubleshooting |
| 77 | `/home/amir/jarvis/agents/eta_compliance.json`            | ETA Compliance: submission validation, error diagnosis, audit |
| 78 | `/home/amir/jarvis/agents/lead_qualification.json`        | Lead Qualification: scoring, routing, discovery prep |
| 79 | `/home/amir/jarvis/agents/accountant_assistant.json`      | Accountant Assistant: financial reports, reconciliation, tax prep |
| 80 | `/home/amir/jarvis/agents/property_matching.json`         | Property Matching: real estate match, market analysis |

### Agent JSON Configurations (AKS Business)

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 81 | `/home/amir/jarvis/agents/aks_ceo_chief_of_staff.json`    | CEO Chief of Staff: executive briefing, strategic analysis |
| 82 | `/home/amir/jarvis/agents/aks_sdr.json`                   | SDR Agent: outbound prospecting, follow-up      |
| 83 | `/home/amir/jarvis/agents/aks_proposal.json`              | Proposal Agent: generate proposals with pricing |
| 84 | `/home/amir/jarvis/agents/aks_crm.json`                   | CRM Agent: pipeline management, forecasting     |
| 85 | `/home/amir/jarvis/agents/aks_content.json`               | Content Agent: article creation, SEO            |
| 86 | `/home/amir/jarvis/agents/aks_project_manager.json`       | Project Manager: project tracking, resource allocation |
| 87 | `/home/amir/jarvis/agents/aks_devops.json`                | DevOps Agent: deployment, monitoring, CI/CD     |

### Scripts

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 88 | `/home/amir/jarvis/scripts/setup.sh`                      | Full dev environment setup: venv, Docker infra, migrations |
| 89 | `/home/amir/jarvis/scripts/load_agents.sh`                | Load all agent JSON configs into JARVIS registry |

### Docs

| #  | File Path                                                 | Description                                      |
|----|-----------------------------------------------------------|--------------------------------------------------|
| 90 | `/home/amir/jarvis/docs/architecture.md`                  | 9-layer architecture overview + multi-tenant design |
| 91 | `/home/amir/jarvis/docs/revenue_workflows.md`             | Complete acquisition playbook with pricing       |
| 92 | `/home/amir/jarvis/docs/COMPLETE_ARCHITECTURE.md`         | **This document**                                |

---

## 3. Layer Architecture

### 3.1 API Layer (FastAPI)

**Location**: `/home/amir/jarvis/backend/api/`

The API layer is the entry point for all external communication. It is built with **FastAPI** and follows a versioned route structure.

**Key design decisions**:

- **Lifespan handler** (`api/main.py:19-28`): Async context manager that initializes database tables on startup.
- **CORS middleware**: Reads `JARVIS_CORS_ORIGINS` from environment, defaults to `*`.
- **Global exception handler** (`api/main.py:49-55`): Catches all unhandled exceptions, logs them, returns 500.
- **Health endpoint** (`/health`): Returns status, version, and environment name.
- **Root redirect** (`/`): Returns API metadata with docs link.
- **Versioned router**: All business logic under `/api/v1/`.

**Dependency injection** (`api/dependencies.py`):

| Dependency                 | Returns                    | Used By                          |
|----------------------------|----------------------------|----------------------------------|
| `get_current_user`         | `AuthContext`              | All protected endpoints          |
| `get_tenant_id`            | `str` (tenant_id)          | All scoped endpoints             |
| `get_agent_registry`       | `AgentRegistryService`     | Agent endpoints                  |
| `get_execution_engine`     | `ExecutionEngine`          | Execution endpoints              |
| `get_memory_service`       | `MemoryService`            | Memory endpoints                 |
| `get_knowledge_service`    | `KnowledgeService`         | Knowledge endpoints              |
| `get_audit_service`        | `AuditService`             | (available for future endpoints) |
| `get_auth_service`         | `AuthService`              | Auth endpoints                   |

### 3.2 Authentication Layer (JWT, Multi-Tenant)

**Location**: `/home/amir/jarvis/backend/jarvis_core/auth/`

**Models**:

| Model              | Fields                                                                 |
|--------------------|------------------------------------------------------------------------|
| `LoginRequest`     | `email: str`, `password: str`                                          |
| `RegisterRequest`  | `email: str`, `password: str`, `display_name: str`, `tenant_slug: str` |
| `TokenResponse`    | `access_token`, `token_type`, `expires_in`, `refresh_token`, `user_id`, `tenant_id`, `role` |
| `AuthContext`      | `user_id`, `tenant_id`, `tenant_slug`, `email`, `role`, `permissions`  |
| `TenantAuth`       | `tenant_id`, `tenant_slug`, `api_key`, `features`                      |

**Authentication flow**:

```
User → POST /auth/login/{tenant_slug}
        ↓
AuthService.authenticate()
  → Lookup tenant by slug
  → Lookup user by tenant_id + email
  → Verify password with bcrypt
  → Generate JWT with claims:
      sub, tenant_id, tenant_slug, role, exp, iat
        ↓
Return TokenResponse
```

**Token validation** (`dependencies.py:20-45`):

```
Request Header: Authorization: Bearer <token>
  → Extract token
  → AuthService.validate_token()
    → Decode JWT with HS256
    → Return AuthContext or None
```

**JWT configuration**:

| Variable                    | Default        | Description                |
|-----------------------------|----------------|----------------------------|
| `JARVIS_JWT_SECRET`         | dev-secret     | HMAC signing key           |
| `JARVIS_TOKEN_EXPIRE_MINUTES` | 1440 (24h)  | Token lifetime            |

**Password hashing**: bcrypt via `passlib` with `CryptContext(schemes=["bcrypt"])`.

### 3.3 Agent Registry

**Location**: `/home/amir/jarvis/backend/jarvis_core/registry/`

The Agent Registry is the central repository of all agent definitions. It follows a **configuration-driven design** where every agent is defined by a JSON file (see Section 6).

**Interface** (`IAgentRegistry`):

| Method              | Description                                    |
|---------------------|------------------------------------------------|
| `register(agent)`   | Create or update (by slug) an agent definition |
| `get(agent_id)`     | Fetch a single agent by ID                     |
| `get_by_slug(tenant_id, slug)` | Fetch agent by tenant + slug         |
| `list(tenant_id, status)`      | List agents for a tenant, optionally filter by status |
| `update(agent_id, updates)`    | Partial update of agent fields                 |
| `delete(agent_id)`  | Remove agent from registry                     |
| `load_from_config(tenant_id, config_path)` | Load agent from JSON file and register |

**Dynamic loading mechanism** (`service.py:98-109`):

```
load_from_config(tenant_id, config_path):
  1. Read JSON file from disk
  2. Inject tenant_id and config_path
  3. Parse into AgentDefinition (Pydantic validates)
  4. Call register() -> upserts into DB
```

**Agent lifecycle** (`AgentStatus` enum):

```
DRAFT -> ACTIVE -> INACTIVE -> ARCHIVED
        ^_________________________| (reactivate)
```

### 3.4 Workflow Engine

**Location**: `/home/amir/jarvis/backend/jarvis_core/execution/`

The Workflow Engine orchestrates multi-step agent workflows.

**Execution model** (`engine.py:41-153`):

```
ExecutionEngine.execute(request):
  1. Lookup agent from registry
  2. Find workflow by name in agent.workflows[]
  3. Create WorkflowExecution DB record (status: running)
  4. For each step in workflow.steps[]:
     a. Create ExecutionStep DB record (status: running)
     b. Execute step based on type:
        - "llm" -> _execute_llm_step()
        - "connector" -> _execute_connector_step()
        - "tool" -> _execute_tool_step()
        - "condition" -> _execute_condition_step()
     c. On success -> mark step completed
     d. On failure:
        - Mark step failed
        - Check escalation rules
        - If !continue_on_failure -> raise (stops workflow)
     e. Persist step to DB
  5. Update WorkflowExecution with final status + output
  6. Return ExecutionResult
```

**Step types**:

| Step Type    | Handler                | Purpose                                  |
|--------------|------------------------|------------------------------------------|
| `llm`        | `_execute_llm_step`    | Call LLM with system prompt + knowledge + memory context |
| `connector`  | `_execute_connector_step` | Execute connector action (Odoo, Gmail, etc.) |
| `tool`       | `_execute_tool_step`   | Call internal tool function              |
| `condition`  | `_execute_condition_step` | Evaluate Python expression against input_data |

**LLM step execution** (`engine.py:213-253`):

```
_execute_llm_step():
  1. Format system_prompt (from step or agent.goal)
  2. Format user_prompt with request.input_data
  3. Search knowledge for relevant context (top 5)
  4. Get recent memory for agent (last 10 entries)
  5. Construct messages: system + user (with knowledge + memory)
  6. Call llm_client.chat(model, temperature)
  7. Return response content + token count
```

**Error handling & escalation** (`engine.py:103-119, 283-288`):

```
On step failure:
  1. Mark step as "failed" with error message
  2. Call _check_escalation():
     - Iterate agent.escalation_rules
     - Match on error_types or conditions
     - Return escalate_to target
  3. If workflow.continue_on_failure -> continue to next step
  4. Otherwise -> re-raise exception (workflow fails)
```

### 3.5 Knowledge Engine (RAG)

**Location**: `/home/amir/jarvis/backend/jarvis_core/knowledge/`

The Knowledge Engine provides **Retrieval-Augmented Generation** capabilities.

**Ingestion pipeline** (`loader.py:21-66`):

```
KnowledgeService.ingest(document):
  1. Create KnowledgeDocument DB record
  2. Chunk content (if present):
     - _chunk_text(content, chunk_size=1000, overlap=200)
     - Smart splitting at sentence/newline boundaries
  3. Create KnowledgeChunk DB records
  4. If Qdrant + embedding client configured:
     - Generate embeddings for each chunk
     - Store in Qdrant collection: "jarvis_{tenant_id}"
     - Set embedding_status = "completed"
  5. Return document with id, chunk_count, embedding_status
```

**Chunking algorithm** (`loader.py:178-198`):

```
_chunk_text(text, chunk_size, overlap):
  While start < len(text):
    end = min(start + chunk_size, len)
    If end < len:
      Find last ". " or "\n" within [start, end]
      If found -> split at that boundary
    Append chunk
    start = end - overlap
```

**Search dual-mode** (`loader.py:68-126`):

| Mode           | Backend        | Query Method                              |
|----------------|----------------|-------------------------------------------|
| **Vector**     | Qdrant         | Embed query -> search_collection -> return scored contexts |
| **Keyword**    | PostgreSQL     | Word-match scoring: count query words present in each chunk content |

**Fallback**: If vector search fails (exception), automatically falls back to keyword search.

### 3.6 Memory Engine

**Location**: `/home/amir/jarvis/backend/jarvis_core/memory/`

The Memory Engine provides persistent context storage for agents.

**MemoryEntry model**:

| Field        | Type      | Default | Description                          |
|--------------|-----------|---------|--------------------------------------|
| `id`         | optional  | None    | Auto-generated UUID                  |
| `tenant_id`  | str       | required| Tenant isolation                     |
| `agent_id`   | optional  | None    | Associated agent                     |
| `user_id`    | optional  | None    | Associated user                      |
| `memory_type`| str       | conversation | Categorization (conversation, decision, preference, etc.) |
| `key`        | str       | required| Memory key for lookup               |
| `value`      | dict      | required| Memory payload                       |
| `importance` | float     | 0.5     | 0.0 (low) to 1.0 (critical)         |
| `context`    | dict      | {}      | Additional metadata                  |
| `expires_at` | optional  | None    | TTL-based expiration                 |

**Importance scoring**: Memories with higher `importance` float to the top in search results (results ordered by `importance DESC`).

**TTL (Time-To-Live)**: Set `expires_at` to auto-expire temporary memories. Expired entries remain in DB but can be pruned by background jobs.

**Memory types used across agents**:

| Type               | Retention | Used By                          |
|--------------------|-----------|----------------------------------|
| conversation       | 90 days   | All agents                       |
| decisions          | 365 days  | Chief of Staff                   |
| delegations        | 30 days   | Chief of Staff                   |
| client_context     | 365 days  | Odoo Consultant                  |
| configuration_history | 730 days | Odoo Consultant               |
| submission_history | 730 days  | ETA Compliance                   |
| error_patterns     | 365 days  | ETA Compliance                   |
| lead_history       | 365 days  | Lead Qualification                |
| client_preferences | 365 days  | Lead Qualification, Accountant, Property |
| financial_context  | 730 days  | Accountant Assistant              |
| report_templates   | 365 days  | Accountant Assistant              |
| search_history     | 90 days   | Property Matching                 |
| viewing_feedback   | 180 days  | Property Matching                 |

### 3.7 Connector Layer

**Location**: `/home/amir/jarvis/backend/connectors/`

**Base class** (`base.py`):

```python
class ConnectorBase(ABC):
    async def initialize(self) -> bool
    async def execute(self, action: str, params: dict) -> ConnectorResponse
    async def health_check(self) -> bool
    async def close(self) -> None
```

**Supporting models**:

| Model              | Fields                                                    |
|--------------------|-----------------------------------------------------------|
| `ConnectorAuth`    | `type` (api_key/oauth2/basic), `credentials: dict`, `config: dict` |
| `ConnectorResponse`| `success: bool`, `data: Any`, `error: str`, `metadata: dict` |

**Implemented connectors** (see [Section 9](#9-connector-reference) for full details):

1. Odoo (XML-RPC)
2. Notion (API)
3. WhatsApp Business (Cloud API)
4. Gmail (Google API)
5. GitHub (REST API)

### 3.8 Odoo Integration Layer

**Location**: `/home/amir/jarvis/backend/connectors/odoo/connector.py`

Built on **XML-RPC** protocol (`xmlrpc.client.ServerProxy`).

**Authentication**: Validates against Odoo's `xmlrpc/2/common` endpoint with username/password or API key.

**CRUD Operations**:

| Action         | Odoo Method     | Parameters                                         |
|----------------|-----------------|----------------------------------------------------|
| `search`       | `search`        | model, domain, offset, limit, order                |
| `search_read`  | `search_read`   | model, domain, fields, offset, limit, order        |
| `create`       | `create`        | model, values                                      |
| `write`        | `write`         | model, ids, values                                 |
| `unlink`       | `unlink`        | model, ids                                         |
| `read`         | `read`          | model, ids, fields                                 |
| `fields_get`   | `fields_get`    | model, attributes                                  |
| `call_method`  | execute_kw      | model, method, args, kwargs                        |

**Connection pooling**: Uses a single `ServerProxy` instance per connector instance.

**Error handling**: Catches all exceptions, returns `ConnectorResponse(success=False, error=str(e))`.

### 3.9 Notification Layer (Planned)

The notification layer is designed but not yet fully implemented as a standalone service. Current notification capabilities exist through:

- **Connector-based**: WhatsApp `send_text`, `send_template`; Gmail `send_email`; Slack connector (planned)
- **Workflow-based**: Steps with `type: "connector"` and `connector: "slack"` (Slack connector action referenced in chief_of_staff.json but not yet implemented)

**Planned architecture**:

- Multi-channel routing: Slack, Email, WhatsApp, Microsoft Teams
- Template-based message rendering
- Priority-based delivery ordering
- Delivery tracking with read receipts

---

## 4. Database Schema

**15 tables** defined in `/home/amir/jarvis/backend/database/models.py`.

### 4.1 `tenants`

| Column             | Type                  | Constraints                    | Description                       |
|--------------------|-----------------------|--------------------------------|-----------------------------------|
| `id`               | VARCHAR (PK)          | DEFAULT uuid4                  | Primary key                       |
| `name`             | VARCHAR(255)          | NOT NULL                       | Company name                      |
| `slug`             | VARCHAR(100)          | UNIQUE, NOT NULL, INDEX        | URL-friendly identifier           |
| `domain`           | VARCHAR(255)          | UNIQUE                         | Custom domain                     |
| `industry`         | VARCHAR(100)          |                                | Industry vertical                 |
| `employee_count`   | INTEGER               | DEFAULT 0                      | Number of employees               |
| `odoo_database_url`| VARCHAR(500)          |                                | Odoo database URL                 |
| `odoo_api_key`     | TEXT                  |                                | Odoo API key (encrypted)          |
| `status`           | ENUM(active,suspended,trial,cancelled) | DEFAULT 'active' | Tenant status          |
| `config`           | JSONB                 | DEFAULT {}                     | Tenant configuration              |
| `features`         | JSONB                 | DEFAULT []                     | Enabled features                  |
| `created_at`       | DATETIME(TZ)          | DEFAULT utcnow                 | Creation timestamp                |
| `updated_at`       | DATETIME(TZ)          | ON UPDATE utcnow               | Last update timestamp             |

**Relationships**: `users`, `agents`, `knowledge_documents`, `memory_entries`, `connector_configs`

### 4.2 `users`

| Column          | Type                  | Constraints                   | Description                    |
|-----------------|-----------------------|-------------------------------|--------------------------------|
| `id`            | VARCHAR (PK)          | DEFAULT uuid4                 | Primary key                    |
| `tenant_id`     | VARCHAR (FK->tenants)  | NOT NULL, INDEX               | Tenant scope                   |
| `email`         | VARCHAR(255)          | NOT NULL, INDEX               | Login email                    |
| `password_hash` | VARCHAR(255)          | NOT NULL                      | bcrypt hash                    |
| `display_name`  | VARCHAR(255)          |                               | Display name                   |
| `role`          | ENUM(admin,manager,member,agent) | DEFAULT 'member' | RBAC role            |
| `is_active`     | BOOLEAN               | DEFAULT true                  | Account active                 |
| `preferences`   | JSONB                 | DEFAULT {}                    | User preferences               |
| `odoo_user_id`  | INTEGER               |                               | Linked Odoo user ID            |
| `created_at`    | DATETIME(TZ)          | DEFAULT utcnow                |                                |
| `updated_at`    | DATETIME(TZ)          | ON UPDATE utcnow              |                                |

**Indexes**:
- `ix_users_tenant_email` on `(tenant_id, email)`
- Unique constraint: `uq_tenant_user_email` on `(tenant_id, email)`

**Relationships**: `tenant`, `conversations`, `audit_logs`

### 4.3 `agent_registry`

| Column              | Type                  | Constraints                   | Description                    |
|---------------------|-----------------------|-------------------------------|--------------------------------|
| `id`                | VARCHAR (PK)          | DEFAULT uuid4                 | Primary key                    |
| `tenant_id`         | VARCHAR (FK->tenants)  | NOT NULL, INDEX               | Tenant scope                   |
| `name`              | VARCHAR(255)          | NOT NULL                      | Agent display name             |
| `slug`              | VARCHAR(100)          | NOT NULL, INDEX               | URL-friendly unique ID         |
| `role`              | VARCHAR(255)          |                               | Role description               |
| `goal`              | TEXT                  |                               | Core mission                   |
| `model`             | VARCHAR(100)          | DEFAULT 'gpt-4o'              | LLM model                      |
| `temperature`       | FLOAT                 | DEFAULT 0.3                   | LLM temperature                |
| `status`            | ENUM(active,inactive,draft,archived) | DEFAULT 'draft' | Lifecycle state    |
| `agent_metadata`    | JSONB                 | DEFAULT {}                    | Arbitrary metadata             |
| `config_path`       | VARCHAR(500)          |                               | Path to JSON config file       |
| `kpis`              | JSONB                 | DEFAULT []                    | KPI definitions                |
| `knowledge_sources` | JSONB                 | DEFAULT []                    | Knowledge source configs       |
| `memory_sources`    | JSONB                 | DEFAULT []                    | Memory source configs          |
| `tools`             | JSONB                 | DEFAULT []                    | Tool definitions               |
| `workflows`         | JSONB                 | DEFAULT []                    | Workflow definitions           |
| `input_schema`      | JSONB                 | DEFAULT {}                    | JSON Schema for input          |
| `output_schema`     | JSONB                 | DEFAULT {}                    | JSON Schema for output         |
| `escalation_rules`  | JSONB                 | DEFAULT []                    | Error escalation rules         |
| `created_at`        | DATETIME(TZ)          | DEFAULT utcnow                |                                |
| `updated_at`        | DATETIME(TZ)          | ON UPDATE utcnow              |                                |

**Unique constraint**: `uq_tenant_agent_slug` on `(tenant_id, slug)`

**Relationships**: `tenant`, `sessions` (AgentSession), `executions` (WorkflowExecution)

### 4.4 `agent_sessions`

| Column       | Type                  | Constraints                   | Description               |
|--------------|-----------------------|-------------------------------|---------------------------|
| `id`         | VARCHAR (PK)          | DEFAULT uuid4                 |                           |
| `agent_id`   | VARCHAR (FK->agent_registry) | NOT NULL, INDEX          |                           |
| `tenant_id`  | VARCHAR (FK->tenants)  | NOT NULL, INDEX               |                           |
| `user_id`    | VARCHAR (FK->users)    | INDEX                         |                           |
| `context`    | JSONB                 | DEFAULT {}                    | Session context           |
| `metadata`   | JSONB                 | DEFAULT {}                    | Session metadata          |
| `is_active`  | BOOLEAN               | DEFAULT true                  |                           |
| `started_at` | DATETIME(TZ)          | DEFAULT utcnow                |                           |
| `ended_at`   | DATETIME(TZ)          |                               |                           |

### 4.5 `conversations`

| Column                  | Type                  | Constraints                   | Description               |
|-------------------------|-----------------------|-------------------------------|---------------------------|
| `id`                    | VARCHAR (PK)          | DEFAULT uuid4                 |                           |
| `tenant_id`             | VARCHAR (FK->tenants)  | NOT NULL, INDEX               |                           |
| `user_id`               | VARCHAR (FK->users)    | INDEX                         |                           |
| `agent_id`              | VARCHAR (FK->agent_registry) | INDEX                    |                           |
| `channel`               | VARCHAR(50)           | DEFAULT 'internal'            | internal, whatsapp, email |
| `channel_conversation_id`| VARCHAR(255)         |                               | External platform ID      |
| `title`                 | VARCHAR(500)          |                               |                           |
| `metadata`              | JSONB                 | DEFAULT {}                    |                           |
| `is_active`             | BOOLEAN               | DEFAULT true                  |                           |
| `created_at`            | DATETIME(TZ)          | DEFAULT utcnow                |                           |
| `updated_at`            | DATETIME(TZ)          | ON UPDATE utcnow              |                           |

**Index**: `ix_conversations_channel` on `(channel, channel_conversation_id)`

### 4.6 `messages`

| Column          | Type                  | Constraints                       | Description     |
|-----------------|-----------------------|-----------------------------------|-----------------|
| `id`            | VARCHAR (PK)          | DEFAULT uuid4                     |                 |
| `conversation_id`| VARCHAR (FK->conversations) | NOT NULL, INDEX               |                 |
| `role`          | VARCHAR(20)           | NOT NULL                          | user/agent/system |
| `content`       | TEXT                  | NOT NULL                          | Message body    |
| `content_type`  | VARCHAR(50)           | DEFAULT 'text'                    | text/image/file |
| `metadata`      | JSONB                 | DEFAULT {}                        |                 |
| `tokens_used`   | INTEGER               |                                   | LLM token count |
| `created_at`    | DATETIME(TZ)          | DEFAULT utcnow                    |                 |

### 4.7 `knowledge_documents`

| Column             | Type                  | Constraints                   | Description                    |
|--------------------|-----------------------|-------------------------------|--------------------------------|
| `id`               | VARCHAR (PK)          | DEFAULT uuid4                 |                                |
| `tenant_id`        | VARCHAR (FK->tenants)  | NOT NULL, INDEX               |                                |
| `title`            | VARCHAR(500)          | NOT NULL                      | Document title                 |
| `source_type`      | VARCHAR(50)           | NOT NULL                      | manual, notion, web, internal  |
| `source_id`        | VARCHAR(500)          |                               | External source ID             |
| `source_url`       | VARCHAR(1000)         |                               | External source URL            |
| `content_type`     | VARCHAR(50)           | DEFAULT 'text'                | text, markdown, html           |
| `content`          | TEXT                  |                               | Raw document content           |
| `metadata`         | JSONB                 | DEFAULT {}                    |                                |
| `embedding_status` | VARCHAR(20)           | DEFAULT 'pending'             | pending/completed/failed       |
| `chunk_count`      | INTEGER               | DEFAULT 0                     | Number of chunks               |
| `is_active`        | BOOLEAN               | DEFAULT true                  | Soft delete flag               |
| `created_at`       | DATETIME(TZ)          | DEFAULT utcnow                |                                |
| `updated_at`       | DATETIME(TZ)          | ON UPDATE utcnow              |                                |

### 4.8 `knowledge_chunks`

| Column           | Type                  | Constraints                       | Description               |
|------------------|-----------------------|-----------------------------------|---------------------------|
| `id`             | VARCHAR (PK)          | DEFAULT uuid4                     |                           |
| `document_id`    | VARCHAR (FK->knowledge_documents) | NOT NULL, INDEX         |                           |
| `tenant_id`      | VARCHAR (FK->tenants)  | NOT NULL, INDEX                   |                           |
| `chunk_index`    | INTEGER               | NOT NULL                          | Position in document      |
| `content`        | TEXT                  | NOT NULL                          | Chunk text                |
| `metadata`       | JSONB                 | DEFAULT {}                        |                           |
| `qdrant_point_id`| VARCHAR               |                                   | Qdrant point reference    |
| `created_at`     | DATETIME(TZ)          | DEFAULT utcnow                    |                           |

### 4.9 `memory_entries`

| Column        | Type                  | Constraints                       | Description               |
|---------------|-----------------------|-----------------------------------|---------------------------|
| `id`          | VARCHAR (PK)          | DEFAULT uuid4                     |                           |
| `tenant_id`   | VARCHAR (FK->tenants)  | NOT NULL, INDEX                   |                           |
| `agent_id`    | VARCHAR (FK->agent_registry) | INDEX                         |                           |
| `user_id`     | VARCHAR (FK->users)    | INDEX                             |                           |
| `memory_type` | VARCHAR(50)           | NOT NULL, INDEX                   | conversation, decision, etc. |
| `key`         | VARCHAR(255)          | NOT NULL                          | Memory key                |
| `value`       | JSONB                 | NOT NULL                          | Memory payload            |
| `importance`  | FLOAT                 | DEFAULT 0.5                       | 0.0-1.0                   |
| `context`     | JSONB                 | DEFAULT {}                        | Additional context        |
| `expires_at`  | DATETIME(TZ)          |                                   | TTL expiration             |
| `created_at`  | DATETIME(TZ)          | DEFAULT utcnow                    |                           |
| `updated_at`  | DATETIME(TZ)          | ON UPDATE utcnow                  |                           |

**Index**: `ix_memory_lookup` on `(tenant_id, agent_id, memory_type, key)`

### 4.10 `connector_configs`

| Column            | Type                  | Constraints                       | Description               |
|-------------------|-----------------------|-----------------------------------|---------------------------|
| `id`              | VARCHAR (PK)          | DEFAULT uuid4                     |                           |
| `tenant_id`       | VARCHAR (FK->tenants)  | NOT NULL, INDEX                   |                           |
| `connector_type`  | VARCHAR(50)           | NOT NULL                          | odoo, notion, whatsapp, etc. |
| `name`            | VARCHAR(255)          | NOT NULL                          | Configuration name        |
| `config`          | JSONB                 | NOT NULL                          | Connector configuration   |
| `credentials`     | JSONB                 | DEFAULT {}                        | Encrypted credentials     |
| `is_enabled`      | BOOLEAN               | DEFAULT true                      |                           |
| `last_sync_at`    | DATETIME(TZ)          |                                   | Last successful sync      |
| `created_at`      | DATETIME(TZ)          | DEFAULT utcnow                    |                           |
| `updated_at`      | DATETIME(TZ)          | ON UPDATE utcnow                  |                           |

**Unique constraint**: `uq_tenant_connector` on `(tenant_id, connector_type, name)`

### 4.11 `workflow_executions`

| Column          | Type                  | Constraints                       | Description               |
|-----------------|-----------------------|-----------------------------------|---------------------------|
| `id`            | VARCHAR (PK)          | DEFAULT uuid4                     |                           |
| `tenant_id`     | VARCHAR (FK->tenants)  | NOT NULL, INDEX                   |                           |
| `agent_id`      | VARCHAR (FK->agent_registry) | NOT NULL, INDEX               |                           |
| `workflow_name` | VARCHAR(255)          | NOT NULL                          |                           |
| `status`        | VARCHAR(20)           | DEFAULT 'pending'                 | pending/running/completed/failed |
| `input_data`    | JSONB                 | DEFAULT {}                        | Execution input           |
| `output_data`   | JSONB                 | DEFAULT {}                        | Execution output          |
| `error`         | TEXT                  |                                   | Error message if failed   |
| `started_at`    | DATETIME(TZ)          | DEFAULT utcnow                    |                           |
| `completed_at`  | DATETIME(TZ)          |                                   |                           |
| `duration_ms`   | INTEGER               |                                   | Execution duration        |

### 4.12 `execution_steps`

| Column          | Type                  | Constraints                       | Description               |
|-----------------|-----------------------|-----------------------------------|---------------------------|
| `id`            | VARCHAR (PK)          | DEFAULT uuid4                     |                           |
| `execution_id`  | VARCHAR (FK->workflow_executions) | NOT NULL, INDEX         |                           |
| `step_name`     | VARCHAR(255)          | NOT NULL                          |                           |
| `step_type`     | VARCHAR(50)           |                                   | llm/connector/tool/condition |
| `status`        | VARCHAR(20)           | DEFAULT 'pending'                 | pending/running/completed/failed |
| `input_data`    | JSONB                 | DEFAULT {}                        | Step input                |
| `output_data`   | JSONB                 | DEFAULT {}                        | Step output               |
| `error`         | TEXT                  |                                   |                           |
| `started_at`    | DATETIME(TZ)          |                                   |                           |
| `completed_at`  | DATETIME(TZ)          |                                   |                           |
| `duration_ms`   | INTEGER               |                                   |                           |

### 4.13 `audit_logs`

| Column          | Type                  | Constraints                       | Description               |
|-----------------|-----------------------|-----------------------------------|---------------------------|
| `id`            | VARCHAR (PK)          | DEFAULT uuid4                     |                           |
| `tenant_id`     | VARCHAR (FK->tenants)  | NOT NULL, INDEX                   |                           |
| `user_id`       | VARCHAR (FK->users)    | INDEX                             |                           |
| `action`        | VARCHAR(100)          | NOT NULL                          | user.login, api.call, etc. |
| `resource_type` | VARCHAR(50)           |                                   | session, document, etc.   |
| `resource_id`   | VARCHAR               |                                   | ID of affected resource   |
| `details`       | JSONB                 | DEFAULT {}                        | Action details            |
| `ip_address`    | VARCHAR(45)           |                                   | Client IP                 |
| `user_agent`    | VARCHAR(500)          |                                   | Client user agent         |
| `created_at`    | DATETIME(TZ)          | DEFAULT utcnow                    |                           |

**Index**: `ix_audit_logs_lookup` on `(tenant_id, action, created_at)`

---

## 5. API Reference

### 5.1 Authentication

#### `POST /api/v1/auth/login/{tenant_slug}`

Authenticate a user for a specific tenant.

| Parameter    | Type   | Location | Required | Description               |
|-------------|--------|----------|----------|---------------------------|
| tenant_slug | string | path     | yes      | Tenant URL identifier     |
| request body| JSON   | body     | yes      | `{email, password}`       |

**Request** (`LoginRequest`):
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response** (`TokenResponse`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600,
  "refresh_token": null,
  "user_id": "uuid",
  "tenant_id": "uuid",
  "role": "admin"
}
```

**Errors**: `401` Invalid credentials or tenant not found.

---

#### `POST /api/v1/auth/register/{tenant_slug}`

Register a new user within a tenant.

| Parameter    | Type   | Location | Required | Description               |
|-------------|--------|----------|----------|---------------------------|
| tenant_slug | string | path     | yes      | Tenant URL identifier     |
| request body| JSON   | body     | yes      | `{email, password, display_name}` |

**Response**:
```json
{
  "message": "User registered",
  "user_id": "uuid"
}
```

**Errors**: `400` User already exists or tenant not found.

---

### 5.2 Agents

All agent endpoints require `Authorization: Bearer <token>` header.

#### `POST /api/v1/agents/register`

Register a new agent or update an existing one (by slug).

**Request** (`AgentDefinition`):
```json
{
  "tenant_id": "t1",
  "name": "My Agent",
  "slug": "my-agent",
  "role": "Assistant",
  "goal": "Help users",
  "model": "gpt-4o",
  "temperature": 0.3,
  "status": "active",
  "kpis": [{"name": "accuracy", "target": 95}],
  "tools": ["tool1"],
  "workflows": [{"name": "wf1", "steps": []}],
  "escalation_rules": [],
  "input_schema": {},
  "output_schema": {}
}
```

**Response**: Returns the created/updated `AgentDefinition`.

**Errors**: `401` Unauthorized.

---

#### `GET /api/v1/agents/`

List all agents for the current tenant.

| Query Param | Type   | Required | Description          |
|-------------|--------|----------|----------------------|
| `status`    | string | no       | Filter: active, inactive, draft, archived |

**Response**: Array of `AgentDefinition`.

---

#### `GET /api/v1/agents/{agent_id}`

Get a single agent by ID.

**Response**: `AgentDefinition` or `404`.

---

#### `GET /api/v1/agents/slug/{slug}`

Get a single agent by slug within the tenant.

**Response**: `AgentDefinition` or `404`.

---

#### `PUT /api/v1/agents/{agent_id}`

Partial update of an agent.

**Request**: JSON object with fields to update.

**Response**: Updated `AgentDefinition`.

---

#### `DELETE /api/v1/agents/{agent_id}`

Delete an agent.

**Response**: `204 No Content`.

---

#### `POST /api/v1/agents/load-config`

Load an agent from a JSON configuration file.

| Body Param    | Type   | Required | Description               |
|---------------|--------|----------|---------------------------|
| `config_path` | string | yes      | Path to JSON file on disk |

**Response**: Created `AgentDefinition`.

---

### 5.3 Execution

#### `POST /api/v1/execution/run`

Execute a workflow for an agent.

**Request** (`ExecutionRequest`):
```json
{
  "tenant_id": "t1",
  "agent_slug": "my-agent",
  "workflow_name": "my_workflow",
  "input_data": {"key": "value"},
  "context": {},
  "session_id": null
}
```

**Response** (`ExecutionResult`):
```json
{
  "id": "exec-uuid",
  "tenant_id": "t1",
  "agent_slug": "my-agent",
  "workflow_name": "my_workflow",
  "status": "completed",
  "output_data": {"result": "..."},
  "steps": [
    {
      "name": "step1",
      "step_type": "llm",
      "status": "completed",
      "output_data": {"response": "..."},
      "duration_ms": 1500
    }
  ],
  "started_at": "2026-06-21T10:00:00Z",
  "completed_at": "2026-06-21T10:00:03Z",
  "duration_ms": 3000
}
```

**Errors**: `400` Agent or workflow not found. `500` Execution failure.

---

#### `GET /api/v1/execution/{execution_id}`

Get the result of a previous execution.

**Response**: `ExecutionResult` or `404`.

---

### 5.4 Knowledge

#### `POST /api/v1/knowledge/ingest`

Ingest a new document into the knowledge base.

**Request** (`KnowledgeDocument`):
```json
{
  "tenant_id": "t1",
  "title": "Odoo Guide",
  "source_type": "manual",
  "content": "Full text content...",
  "metadata": {"chunk_size": 1000, "chunk_overlap": 200}
}
```

**Response**: `KnowledgeDocument` with assigned `id` and `chunk_count`.

---

#### `GET /api/v1/knowledge/search`

Search the knowledge base.

| Query Param | Type   | Required | Default | Description          |
|-------------|--------|----------|---------|----------------------|
| `query`     | string | yes      |         | Search query         |
| `limit`     | int    | no       | 5       | Results (1-50)       |

**Response**:
```json
{
  "results": "[Score: 0.92]\nChunk content...\n\n---\n\n[Score: 0.85]\nAnother chunk..."
}
```

---

#### `GET /api/v1/knowledge/documents/{document_id}`

Get a document with all its chunks.

**Response**: Full `KnowledgeDocument` with `chunks` array.

---

#### `DELETE /api/v1/knowledge/documents/{document_id}`

Delete a document and all its chunks.

**Response**: `204 No Content`.

---

### 5.5 Memory

#### `POST /api/v1/memory/store`

Store a memory entry.

**Request** (`MemoryEntry`):
```json
{
  "tenant_id": "t1",
  "agent_id": "a1",
  "memory_type": "conversation",
  "key": "user_preference",
  "value": {"language": "Arabic"},
  "importance": 0.8,
  "expires_at": "2026-09-21T00:00:00Z"
}
```

**Response**: `MemoryEntry` with assigned `id` and `created_at`.

---

#### `GET /api/v1/memory/recent`

Get recent memory entries for an agent.

| Query Param | Type   | Required | Default | Description          |
|-------------|--------|----------|---------|----------------------|
| `agent_id`  | string | yes      |         | Agent ID             |
| `limit`     | int    | no       | 10      | Results (1-100)      |

**Response**: Array of memory objects.

---

#### `GET /api/v1/memory/search`

Search memory entries.

| Query Param    | Type   | Required | Description          |
|----------------|--------|----------|----------------------|
| `query`        | string | yes      | Search string        |
| `memory_type`  | string | no       | Filter by type       |

**Response**: Array of `MemorySearchResult`.

---

#### `DELETE /api/v1/memory/{entry_id}`

Delete (forget) a memory entry.

**Response**: `204 No Content`.

---

### 5.6 Connectors

#### `POST /api/v1/connectors/configure`

Create or update a connector configuration.

| Body Param        | Type   | Required | Description               |
|-------------------|--------|----------|---------------------------|
| `connector_type`  | string | yes      | odoo, notion, whatsapp, etc. |
| `name`            | string | yes      | Configuration name        |
| `config`          | JSON   | yes      | Connector parameters      |
| `credentials`     | JSON   | no       | Auth credentials          |

**Response**:
```json
{
  "message": "Connector odoo/my-odoo configured",
  "status": "ok"
}
```

---

#### `GET /api/v1/connectors/`

List all configured connectors for the tenant.

**Response**:
```json
[
  {
    "id": "uuid",
    "type": "odoo",
    "name": "my-odoo",
    "is_enabled": true,
    "last_sync": "2026-06-21T10:00:00Z"
  }
]
```

---

#### `DELETE /api/v1/connectors/{connector_id}`

Delete a connector configuration.

**Response**: `204 No Content`.

---

### 5.7 Utility

#### `GET /health`

```json
{
  "status": "ok",
  "service": "JARVIS",
  "version": "1.0.0",
  "environment": "development"
}
```

#### `GET /`

```json
{
  "message": "JARVIS AI Operating System",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## 6. Agent Framework

### 6.1 Agent Schema (`AgentDefinition`)

Every agent in JARVIS is defined by a Pydantic model (`/home/amir/jarvis/backend/jarvis_core/registry/models.py`):

| Field              | Type           | Default   | Description                                    |
|--------------------|----------------|-----------|------------------------------------------------|
| `id`               | Optional[str]  | None      | Auto-generated UUID                            |
| `tenant_id`        | str            | required  | Owner tenant                                   |
| `name`             | str            | required  | Display name                                   |
| `slug`             | str            | required  | Unique URL identifier within tenant            |
| `role`             | str            | required  | Role description (e.g., "Sales Representative")|
| `goal`             | str            | required  | Core mission statement                         |
| `model`            | str            | "gpt-4o"  | LLM model identifier                           |
| `temperature`      | float          | 0.3       | LLM creativity (0.0-1.0)                      |
| `status`           | AgentStatus    | DRAFT     | Lifecycle state                                |
| `config_path`      | Optional[str]  | None      | Path to JSON config file                       |
| `kpis`             | list[dict]     | []        | Key performance indicators                     |
| `knowledge_sources`| list[dict]     | []        | Knowledge base references                      |
| `memory_sources`   | list[dict]     | []        | Memory configuration                           |
| `tools`            | list[dict]     | []        | Available tools                                |
| `workflows`        | list[dict]     | []        | Workflow definitions with steps                |
| `input_schema`     | dict           | {}        | JSON Schema for expected input                 |
| `output_schema`    | dict           | {}        | JSON Schema for expected output                |
| `escalation_rules` | list[dict]     | []        | Error handling and escalation rules            |
| `agent_metadata`   | dict           | {}        | Arbitrary metadata                             |
| `created_at`       | Optional[datetime] | None | Creation timestamp                          |
| `updated_at`       | Optional[datetime] | None | Last update timestamp                       |

### 6.2 Configuration-Driven Design

Agents are defined as JSON files in `/home/amir/jarvis/agents/` and loaded via:

```
POST /api/v1/agents/load-config
Body: {"config_path": "/app/agents/chief_of_staff.json"}
```

Or via the batch script:
```bash
./scripts/load_agents.sh <tenant_slug> <api_token>
```

The JSON schema mirrors the `AgentDefinition` model. See the 13 JSON files in Section 2 for complete examples.

### 6.3 Dynamic Loading Mechanism

Implemented in `AgentRegistryService.load_from_config()` (`registry/service.py:98-109`):

1. **File resolution**: Path is resolved from the filesystem.
2. **JSON parsing**: File is read and parsed into a dictionary.
3. **Tenant injection**: `tenant_id` is set from the caller.
4. **Pydantic validation**: Dictionary is validated against `AgentDefinition`.
5. **Registration**: `register()` is called, which upserts (inserts or updates by slug).

This allows adding new agents without code changes -- just drop a new JSON file and call the endpoint.

---

## 7. MVP Agents

Six MVP agents defined in `/home/amir/jarvis/agents/`.

### 7.1 Chief of Staff

| Attribute       | Value                                                |
|-----------------|------------------------------------------------------|
| **Slug**        | `chief-of-staff`                                     |
| **Role**        | Chief of Staff - AKS Solutions Executive Coordinator |
| **Model**       | gpt-4o, temperature 0.2                              |
| **Goal**        | Coordinate operations, delegate tasks, ensure alignment with strategic goals |
| **KPIs**        | task_completion_rate (95%), response_time (2min), delegation_accuracy (90%), escalation_resolution_time (30min) |
| **Tools**       | get_agent_status, delegate_task, escalate_issue, schedule_meeting, send_notification, get_company_metrics |
| **Workflows**   | `task_delegation` (parse -> select agent -> delegate via Slack -> confirm), `daily_briefing` (gather metrics -> check Odoo projects -> summarize) |
| **Knowledge**   | Notion: Company Strategy, OKR Tracking, Project Registry; Internal: org_chart, SOPs |
| **Escalation**  | critical_priority -> CEO (5min), cross_department -> COO (30min), resource_bottleneck -> PM (60min) |

### 7.2 Odoo Consultant

| Attribute       | Value                                                |
|-----------------|------------------------------------------------------|
| **Slug**        | `odoo-consultant`                                    |
| **Role**        | Odoo ERP Implementation Consultant                   |
| **Model**       | gpt-4o, temperature 0.3                              |
| **Goal**        | Guide Odoo implementation, configuration, optimization |
| **KPIs**        | implementation_success_rate (90%), client_satisfaction (4.5), ticket_resolution_time (4h), module_configuration_accuracy (95%) |
| **Tools**       | search_odoo_modules, check_module_compatibility, generate_configuration_guide, validate_workflow, estimate_effort, generate_implementation_plan |
| **Workflows**   | `discovery` (gather -> analyze -> proposal), `configuration` (assess Odoo -> plan -> guide), `troubleshoot` (analyze -> search knowledge -> solution) |
| **Escalation**  | custom_module -> Solution Architect, data_migration -> Technical Lead, performance -> DevOps |

### 7.3 ETA Compliance

| Attribute       | Value                                                |
|-----------------|------------------------------------------------------|
| **Slug**        | `eta-compliance`                                     |
| **Role**        | Egyptian Tax Authority Compliance Specialist         |
| **Model**       | gpt-4o, temperature 0.1                              |
| **Goal**        | Ensure ETA e-invoicing/e-receipt compliance          |
| **KPIs**        | compliance_rate (100%), error_diagnosis_accuracy (98%), submission_success_rate (99%), response_time (5min) |
| **Tools**       | validate_invoice, check_eta_status, diagnose_error_code, generate_compliance_report, verify_code_signing, check_certificate_validity |
| **Workflows**   | `validate_submission` (parse -> validate -> check -> report), `diagnose_error` (get Odoo log -> diagnose -> fix), `compliance_audit` (check setup -> review invoices -> audit report) |
| **Escalation**  | eta_api_down -> Technical Team, certificate_expired -> Client Admin, legal_ambiguity -> ETA Legal Team |

### 7.4 Lead Qualification

| Attribute       | Value                                                |
|-----------------|------------------------------------------------------|
| **Slug**        | `lead-qualification`                                 |
| **Role**        | Sales Development Representative                     |
| **Model**       | gpt-4o, temperature 0.3                              |
| **Goal**        | Quality inbound leads, score, route to sales         |
| **KPIs**        | leads_qualified_per_day (20), qualification_accuracy (85%), response_time (5min), handoff_success_rate (90%) |
| **Tools**       | score_lead, check_budget_fit, check_industry_fit, check_timeline, send_qualification_email, route_to_sales_channel, schedule_discovery_call |
| **Workflows**   | `qualify_lead` (extract -> ICP fit -> score -> route), `discovery_prep` (research -> questions -> brief) |
| **Routing**     | Hot -> Sales Manager, Warm -> SDR, Cold -> Nurture     |
| **Escalation**  | high_value (>50k) -> Sales Manager, strategic_account -> CEO, complex -> Solution Architect |

### 7.5 Accountant Assistant

| Attribute       | Value                                                |
|-----------------|------------------------------------------------------|
| **Slug**        | `accountant-assistant`                               |
| **Role**        | Financial Operations Assistant                       |
| **Model**       | gpt-4o, temperature 0.1                              |
| **Goal**        | Financial analysis, reconciliation, reporting, tax   |
| **KPIs**        | report_accuracy (99%), reconciliation_speed (60min), query_resolution_time (10min), error_detection_rate (95%) |
| **Tools**       | generate_report, reconcile_accounts, analyze_financials, detect_anomalies, calculate_tax, validate_transactions |
| **Workflows**   | `generate_financial_report` (Odoo fetch -> analyze -> report), `reconciliation` (bank -> books -> match -> flag), `tax_preparation` (tax data -> calculate -> return) |
| **Escalation**  | major_discrepancy (>100k) -> Senior Accountant, tax_audit -> Tax Advisor, system_inconsistency -> Odoo Consultant |

### 7.6 Property Matching

| Attribute       | Value                                                |
|-----------------|------------------------------------------------------|
| **Slug**        | `property-matching`                                  |
| **Role**        | Real Estate Property Matching Specialist             |
| **Model**       | gpt-4o, temperature 0.2                              |
| **Goal**        | Match properties with buyers/tenants via multi-criteria scoring |
| **KPIs**        | match_accuracy (90%), response_time (30s), client_satisfaction (4.5), viewing_conversion (40%) |
| **Tools**       | search_properties, score_match, compare_properties, generate_comparison_report, estimate_market_value, check_availability |
| **Workflows**   | `match_properties` (parse -> Odoo search -> score -> rank), `market_analysis` (gather -> analyze -> report) |
| **Escalation**  | no_matches -> Real Estate Manager, exclusive_listing -> Senior Broker, price_dispute -> Valuation Team |

---

## 8. AKS Business Agents

Seven agents organized by business function, defined in JSON files with `aks_` prefix.

### 8.1 Sales Team

#### SDR Agent (`aks_sdr.json`)

| Attribute   | Value                                                |
|-------------|------------------------------------------------------|
| **Slug**    | `aks-sdr`                                            |
| **Role**    | Sales Development Representative - AKS Solutions     |
| **Goal**    | Generate/qualify outbound leads, book discovery calls|
| **Model**   | gpt-4o, temperature 0.4                              |
| **KPIs**    | outbound_activities/day (50), meetings/week (8), lead_response_rate (15%), qualified_leads/month (40) |
| **Tools**   | search_linkedin, find_company_contacts, send_email, send_linkedin_message, log_activity_odoo |
| **Workflows**| `outbound_prospecting` (find -> enrich -> craft -> email -> log to Odoo CRM), `follow_up` (check Odoo -> draft -> send) |
| **Escalation**| meeting_requested -> Sales Manager (15min), budget_confirmed -> Proposal Agent (30min), competitor_mentioned -> Solution Architect (60min) |

#### Proposal Agent (`aks_proposal.json`)

| Attribute   | Value                                                |
|-------------|------------------------------------------------------|
| **Slug**    | `aks-proposal`                                       |
| **Role**    | Proposal Generation Specialist                       |
| **Goal**    | Generate professional proposals for Odoo, ETA, AI    |
| **Model**   | gpt-4o, temperature 0.2                              |
| **KPIs**    | quality_score (4.5), generation_time (30min), win_rate (40%), revision_cycles (2) |
| **Knowledge**| Notion: Proposal Templates, Pricing Matrix; Internal: case_studies, service_catalog |
| **Tools**   | generate_proposal_pdf, calculate_pricing, fetch_template, validate_proposal |
| **Workflows**| `generate_proposal` (analyze -> pricing -> template -> generate -> validate) |
| **Escalation**| custom_pricing -> Sales Manager, complex_scope -> Solution Architect |

#### CRM Agent (`aks_crm.json`)

| Attribute   | Value                                                |
|-------------|------------------------------------------------------|
| **Slug**    | `aks-crm`                                            |
| **Role**    | CRM Operations Agent                                 |
| **Goal**    | Manage sales pipeline, track opportunities, automate follow-ups |
| **Model**   | gpt-4o, temperature 0.2                              |
| **KPIs**    | pipeline_accuracy (95%), opportunity_update_time (5min), forecast_accuracy (85%), automation_coverage (70%) |
| **Workflows**| `update_pipeline` (fetch Odoo opportunities -> analyze -> write stages), `forecast` (gather Odoo -> generate forecast) |
| **Escalation**| pipeline_stagnation -> Sales Manager, forecast_miss -> Revenue Analyst |

### 8.2 Marketing Team

#### Content Agent (`aks_content.json`)

| Attribute   | Value                                                |
|-------------|------------------------------------------------------|
| **Slug**    | `aks-content`                                        |
| **Role**    | Content Marketing Specialist                          |
| **Goal**    | Create/distribute content about Odoo, ETA, AI for Egyptian SMEs |
| **Model**   | gpt-4o, temperature 0.5                              |
| **KPIs**    | articles/week (3), engagement_rate (5%), lead_gen_from_content (10%), seo_ranking_improvement (20%) |
| **Workflows**| `create_article` (research topic -> draft -> review SEO -> publish to Notion) |
| **Escalation**| content_strategy_change -> Marketing Manager |

### 8.3 Operations Team

#### Project Manager Agent (`aks_project_manager.json`)

| Attribute   | Value                                                |
|-------------|------------------------------------------------------|
| **Slug**    | `aks-project-manager`                                |
| **Role**    | Project Manager - AKS Solutions                      |
| **Goal**    | Manage Odoo implementation projects, track milestones, allocate resources |
| **Model**   | gpt-4o, temperature 0.2                              |
| **KPIs**    | on_time_delivery (90%), budget_adherence (95%), resource_utilization (80%), client_satisfaction (4.5) |
| **Workflows**| `track_project` (fetch Odoo tasks -> assess -> status report), `allocate_resources` (check Odoo HR -> optimize) |
| **Escalation**| critical_delay (>14d) -> COO, budget_overrun (>20%) -> Finance, resource_conflict -> Operations Director |

### 8.4 Technical Team

#### DevOps Agent (`aks_devops.json`)

| Attribute   | Value                                                |
|-------------|------------------------------------------------------|
| **Slug**    | `aks-devops`                                         |
| **Role**    | DevOps Engineer - AKS Solutions                      |
| **Goal**    | Manage infrastructure, deployments, monitoring, CI/CD |
| **Model**   | gpt-4o, temperature 0.1                              |
| **KPIs**    | uptime (99.9%), deployment_success (98%), incident_response (15min), cost_optimization (15%) |
| **Connectors**| github, docker, odoo                                |
| **Workflows**| `deploy` (check GitHub PRs -> CI webhook -> docker deploy -> health check), `monitor` (health -> analyze logs -> report) |
| **Escalation**| production_outage -> CTO (5min), security_vulnerability -> Security Team (30min) |

### 8.5 Executive Team

#### CEO Chief of Staff (`aks_ceo_chief_of_staff.json`)

| Attribute   | Value                                                |
|-------------|------------------------------------------------------|
| **Slug**    | `ceo-chief-of-staff`                                 |
| **Role**    | CEO Executive Chief of Staff                         |
| **Goal**    | Executive coordination, strategic analysis, operational oversight |
| **Model**   | gpt-4o, temperature 0.2                              |
| **KPIs**    | revenue_tracking_accuracy (100%), strategic_initiative_progress (90%), board_report_quality (5), decision_support_accuracy (95%) |
| **Workflows**| `weekly_briefing` (Odoo revenue -> Odoo pipeline -> Odoo projects -> generate briefing), `strategic_analysis` (collect -> trends -> recommendations) |
| **Escalation**| revenue_shortfall (>20%) -> CEO Personal, client_churn_risk -> CEO Personal (60min), strategic_opportunity -> CEO Personal (240min) |

---

## 9. Connector Reference

### 9.1 Odoo Connector

| Property       | Value                                              |
|----------------|----------------------------------------------------|
| **Class**      | `OdooConnector`                                    |
| **Auth type**  | basic (username/password) or api_key               |
| **Protocol**   | XML-RPC (`/xmlrpc/2/common`, `/xmlrpc/2/object`)   |
| **Init config**| `url`, `db`, `username`, `password`, `api_key`     |
| **Health**     | Calls `common.version()` -- must return truthy      |

**Actions**:

| Action          | Parameters                                    | Description                        |
|-----------------|-----------------------------------------------|------------------------------------|
| `search`        | model, domain, offset, limit, order           | Search records by domain           |
| `search_read`   | model, domain, fields, offset, limit, order   | Search and read fields             |
| `create`        | model, values                                 | Create new record                  |
| `write`         | model, ids, values                            | Update existing records            |
| `unlink`        | model, ids                                    | Delete records                     |
| `read`          | model, ids, fields                            | Read records by ID                 |
| `fields_get`    | model, attributes                             | Get model field definitions        |
| `call_method`   | model, method, args, kwargs                   | Call any Odoo model method         |

### 9.2 Notion Connector

| Property       | Value                                              |
|----------------|----------------------------------------------------|
| **Class**      | `NotionConnector`                                  |
| **Auth type**  | api_key (Integration Token)                         |
| **Library**    | `notion_client` (optional -- mock fallback)          |
| **Init config**| `api_key`                                           |
| **Health**     | Checks if `_client` is not None                     |

**Actions**:

| Action            | Parameters                                | Description                        |
|-------------------|-------------------------------------------|------------------------------------|
| `search`          | query, kwargs                             | Search Notion                      |
| `query_database`  | database_id, kwargs                       | Query a database                   |
| `get_page`        | page_id                                   | Retrieve a page                    |
| `create_page`     | parent, properties, children              | Create a new page                  |
| `update_page`     | page_id, properties                       | Update page properties             |
| `get_database`    | database_id                               | Retrieve database metadata         |
| `list_databases`  | (none)                                    | List all databases                 |
| `get_block_children`| block_id                                | Get block children                 |

### 9.3 WhatsApp Connector

| Property       | Value                                              |
|----------------|----------------------------------------------------|
| **Class**      | `WhatsAppConnector`                                |
| **Auth type**  | access_token (Meta/WhatsApp Cloud API)             |
| **Protocol**   | HTTPS (graph.facebook.com/v18.0)                   |
| **Init config**| `phone_number_id`, `access_token`, `webhook_verify_token`, `app_secret` |
| **Health**     | GET request to phone messages endpoint (status < 500) |
| **Signature**  | HMAC-SHA256 verification for webhooks              |

**Actions**:

| Action            | Parameters                                | Description                        |
|-------------------|-------------------------------------------|------------------------------------|
| `send_text`       | to, text, preview_url                     | Send text message                  |
| `send_template`   | to, template_name, language, components   | Send template message              |
| `send_image`      | to, image_url/image_id, caption           | Send image                         |
| `send_document`   | to, document_url/doc_id, filename, caption| Send document                      |
| `send_button`     | to, text, buttons                         | Send interactive button message    |
| `mark_as_read`    | message_id                                | Mark message as read               |
| `get_messages`    | (none)                                    | Returns note about webhook-based receiving |
| `verify_webhook`  | hub_mode, hub_verify_token, hub_challenge | Webhook verification               |

### 9.4 Gmail Connector

| Property       | Value                                              |
|----------------|----------------------------------------------------|
| **Class**      | `GmailConnector`                                   |
| **Auth type**  | OAuth 2.0 (Google API)                             |
| **Library**    | `google-api-python-client`, `google-auth-oauthlib` |
| **Init config**| `token_path`, `credentials_path`                   |
| **Scopes**     | `https://www.googleapis.com/auth/gmail.modify`     |
| **Mock fallback**| Returns mock data if libraries not installed     |
| **Health**     | Always returns `True`                               |

**Actions**:

| Action            | Parameters                                | Description                        |
|-------------------|-------------------------------------------|------------------------------------|
| `send_email`      | to, cc, bcc, subject, body, body_type    | Send email (plain/html)            |
| `list_messages`   | max_results, label_ids                    | List messages in mailbox           |
| `get_message`     | message_id                                | Get full message content           |
| `search_messages` | query, max_results                        | Search messages by query           |
| `create_draft`    | to, subject, body                         | Create email draft                 |
| `mark_as_read`    | message_id                                | Remove UNREAD label                |
| `trash_message`   | message_id                                | Move message to trash              |
| `list_labels`     | (none)                                    | List all mailbox labels            |

### 9.5 GitHub Connector

| Property       | Value                                              |
|----------------|----------------------------------------------------|
| **Class**      | `GitHubConnector`                                  |
| **Auth type**  | token (Personal Access Token)                      |
| **Protocol**   | HTTPS (api.github.com)                             |
| **Init config**| `token`                                             |
| **Health**     | GET `/` returns 200                                 |
| **User-Agent** | `JARVIS-AKS/1.0` (required by GitHub API)          |

**Actions**:

| Action              | Parameters                        | Description                        |
|---------------------|-----------------------------------|------------------------------------|
| `get_repo`          | repo (owner/repo)                 | Get repository details             |
| `list_repos`        | username, type, per_page          | List repositories                  |
| `create_issue`      | repo, title, body, labels         | Create an issue                    |
| `list_issues`       | repo, state, labels               | List issues                        |
| `create_pull_request`| repo, title, head, base, body    | Create pull request                |
| `list_pull_requests`| repo, state                       | List pull requests                 |
| `get_file`          | repo, path, ref                   | Get file contents                  |
| `create_webhook`    | repo, url, events, secret         | Create repository webhook          |
| `list_commits`      | repo, branch, per_page            | List commits on branch             |
| `create_branch`     | repo, branch_name, sha            | Create a new branch                |
| `search_code`       | query, per_page                   | Search code across repositories    |

---

## 10. Revenue Workflows

### 10.1 Lead Generation

**Inbound pipeline**:

```
Website Form / Email / WhatsApp / Referral
        |
Odoo CRM (capture)
        |
Lead Qualification Agent (score)
        |
Route:
  Hot  -> Sales Manager (immediate call)
  Warm -> SDR Agent (within 1 hour)
  Cold -> Nurture Campaign (automated sequence)
```

**Outbound prospecting**:

| Element       | Details                                            |
|---------------|----------------------------------------------------|
| Targets       | Egyptian SMEs, 20-500 employees                    |
| Industries    | Real Estate, Trading, Manufacturing, Construction, Healthcare, IT, F&B |
| Current ERP   | None, Excel, legacy systems                        |
| Sources       | LinkedIn, Egypt Business Directory, Industry Events|
| Sequence      | Day 1: LinkedIn + Email -> Day 3: Case study -> Day 7: Video -> Day 14: Final CTA |

### 10.2 Outreach

**Email templates**:

- **Odoo Implementation**: "Modernize your {industry} operations with Odoo"
- **ETA Compliance**: "ETA E-Invoicing Compliance Check"

**Channels**: Gmail, LinkedIn (manual + automation), WhatsApp Business, Phone (manual)

### 10.3 Proposals

**Generation workflow**:

```
Qualified lead requests proposal
  -> Collect requirements from discovery notes
  -> Map requirements to services
  -> Calculate effort and pricing tier
  -> Generate: Executive Summary, SOW, Module List, Timeline, Investment, Terms
  -> Proposal Agent QC check
  -> Send via email with PDF + calendar link
  -> Track proposal view status
```

### 10.4 Pricing Framework

| Service             | Tier       | Price (EGP)          | Scope                                    |
|---------------------|------------|----------------------|------------------------------------------|
| **Odoo Implementation** | Starter    | 15,000-30,000        | Core modules, 2 users                    |
|                     | Business   | 40,000-80,000        | Full modules, 5-10 users                 |
|                     | Enterprise | 100,000-250,000      | Custom modules, unlimited users          |
| **ETA Compliance**  | Audit      | 5,000-10,000         | Compliance audit + report                |
|                     | Setup      | 20,000-50,000        | Full ETA integration + testing           |
|                     | Managed    | 5,000/month          | Ongoing compliance management            |
| **AI Automation**   | Per Agent  | 10,000-25,000        | Single agent + 3 months support          |
|                     | Package    | 50,000-150,000       | Multi-agent system + integration         |

### 10.5 Discovery Call Workflow

```
Pre-call:  SDR gathers company info, pain points -> Proposal Agent prepares agenda -> Knowledge fetches case studies
During:    Introduction -> Discovery -> Demo -> Next steps
Post-call:  Summary within 2h -> Proposal within 24h -> Follow-up scheduled -> CRM updated
```

### 10.6 Client Onboarding

```
Phase 1 - Kickoff:     Assign PM, kickoff meeting, provision Odoo, collect docs
Phase 2 - Configuration: Configure modules, migrate data, integrate, ETA setup
Phase 3 - Testing:     QA scenarios, UAT, feedback iterations
Phase 4 - Go-Live:     Training, production deployment, 2-week hypercare, L1 handover
Phase 5 - Optimization: Monthly review, process improvements, expansion
```

### 10.7 Revenue Targets

| Metric                  | Target                 |
|-------------------------|------------------------|
| Monthly leads           | 100                    |
| Qualified opportunities | 25                     |
| Closed-won per month    | 5-8                    |
| Average deal size       | 75,000 EGP             |
| Monthly revenue target  | 500,000 EGP            |

---

## 11. Multi-Tenant Design

### 11.1 Tenancy Model

JARVIS uses a **shared-schema with tenant isolation** pattern. Every tenant (company) gets:

1. A `tenants` record with unique slug, domain, and configuration.
2. Data scoping via `tenant_id` column on all business tables.
3. Separate Qdrant vector collection per tenant: `jarvis_{tenant_id}`.
4. Tenant-scoped connector configurations in `connector_configs`.
5. Tenant-scoped agent registry with unique slug enforcement.
6. Tenant-scoped knowledge base and memory store.
7. Tenant-scoped audit logs.

### 11.2 Data Isolation

| Table              | Isolation via `tenant_id` | Unique Constraint                |
|--------------------|---------------------------|----------------------------------|
| `users`            | Yes                       | `(tenant_id, email)`             |
| `agent_registry`   | Yes                       | `(tenant_id, slug)`              |
| `agent_sessions`   | Yes                       |                                  |
| `conversations`    | Yes                       |                                  |
| `messages`         | (via conversation)        |                                  |
| `knowledge_documents` | Yes                    |                                  |
| `knowledge_chunks` | Yes                       |                                  |
| `memory_entries`   | Yes                       |                                  |
| `connector_configs`| Yes                       | `(tenant_id, connector_type, name)` |
| `workflow_executions` | Yes                    |                                  |
| `execution_steps`  | (via execution)           |                                  |
| `audit_logs`       | Yes                       |                                  |

### 11.3 JWT Tenant Scoping

All protected API endpoints extract `tenant_id` from the JWT and inject it into service calls:

```python
# dependencies.py
async def get_tenant_id(current_user: AuthContext) -> str:
    return current_user.tenant_id
```

Services then scope all queries:

```python
select(AgentRegistryDB).where(
    AgentRegistryDB.tenant_id == tenant_id,
    AgentRegistryDB.slug == slug,
)
```

### 11.4 Qdrant Collections

Each tenant gets an isolated vector collection named `jarvis_{tenant_id}`:

```python
# knowledge/loader.py:78
search_result = self.qdrant_client.search(
    collection_name=f"jarvis_{tenant_id}",
    query_vector=query_embedding,
    limit=limit,
)
```

### 11.5 Auth Isolation

- Login is scoped to `tenant_slug` via route parameter.
- Users cannot log into a different tenant even with valid credentials.
- JWT contains `tenant_id` which is validated on every request.
- Registration is also tenant-scoped.

---

## 12. Deployment

### 12.1 Docker Services (`docker-compose.yml`)

Four services orchestrated with Docker Compose:

| Service          | Image                      | Ports            | Depends On                      |
|------------------|----------------------------|------------------|---------------------------------|
| `postgres`       | postgres:16-alpine         | 5432             | --                              |
| `qdrant`         | qdrant/qdrant:latest       | 6333, 6334       | --                              |
| `redis`          | redis:7-alpine             | 6379             | --                              |
| `api`            | (built from ./backend)     | 8000             | postgres (healthy), qdrant, redis |
| `celery-worker`  | (built from ./backend)     | --               | postgres, redis                 |

**API service environment**:

| Variable                    | Value                                                           |
|-----------------------------|-----------------------------------------------------------------|
| `JARVIS_ENV`                | production                                                      |
| `JARVIS_DATABASE_URL`       | `postgresql+asyncpg://jarvis:jarvis@postgres:5432/jarvis`       |
| `JARVIS_DATABASE_URL_SYNC`  | `postgresql+psycopg2://jarvis:jarvis@postgres:5432/jarvis`      |
| `JARVIS_REDIS_URL`          | `redis://redis:6379/0`                                          |
| `JARVIS_QDRANT_URL`         | `http://qdrant:6333`                                            |
| `JARVIS_JWT_SECRET`         | `${JARVIS_JWT_SECRET}` (required in production)                 |
| `JARVIS_CORS_ORIGINS`       | `${JARVIS_CORS_ORIGINS}` (e.g., http://localhost:3000)          |

**Volumes**:

- `postgres_data` -> `/var/lib/postgresql/data`
- `qdrant_data` -> `/qdrant/storage`
- `redis_data` -> `/data`

### 12.2 Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "jarvis.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 12.3 Local Development

**Setup** (`scripts/setup.sh`):

1. Creates Python virtual environment
2. Installs pip dependencies from `requirements.txt`
3. Copies `.env.example` to `.env`
4. Creates data directories for PostgreSQL, Qdrant, Redis
5. Starts infrastructure with `docker-compose up -d postgres qdrant redis`
6. Runs Alembic migrations: `alembic upgrade head`

**Start API**:
```bash
cd backend && uvicorn jarvis.api.main:app --reload --port 8000
```

### 12.4 Alembic Migrations

- **Config file**: `/home/amir/jarvis/backend/alembic.ini`
- **Migrations directory**: `/home/amir/jarvis/backend/database/migrations/`
- **Environment**: `env.py` configures auto-detection of all models via `Base.metadata`
- **Sync connection**: Uses `psycopg2` (synchronous driver)
- **Template**: `script.py.mako` provides standard migration skeleton

### 12.5 Environment Configuration (`.env.example`)

| Variable                        | Default                                       | Description                    |
|---------------------------------|-----------------------------------------------|--------------------------------|
| `JARVIS_ENV`                    | `development`                                 | Environment name               |
| `JARVIS_DATABASE_URL`           | `postgresql+asyncpg://jarvis:jarvis@localhost:5432/jarvis` | Async DB URL |
| `JARVIS_DATABASE_URL_SYNC`      | `postgresql+psycopg2://jarvis:jarvis@localhost:5432/jarvis` | Sync DB URL  |
| `JARVIS_REDIS_URL`              | `redis://localhost:6379/0`                    | Redis URL                     |
| `JARVIS_QDRANT_URL`             | `http://localhost:6333`                       | Qdrant URL                    |
| `JARVIS_JWT_SECRET`             | `dev-secret-key`                              | JWT signing key               |
| `JARVIS_CORS_ORIGINS`           | `http://localhost:3000,http://localhost:8000` | Allowed CORS origins          |
| `JARVIS_TOKEN_EXPIRE_MINUTES`   | `1440`                                        | JWT token lifetime (minutes)  |
| `OPENAI_API_KEY`                | (empty)                                       | OpenAI API key                |

### 12.6 Agent Loading

**Manual**:
```bash
curl -X POST http://localhost:8000/api/v1/agents/load-config \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "/app/agents/chief_of_staff.json"}'
```

**Batch**:
```bash
./scripts/load_agents.sh <tenant_slug> <api_token>
```
The script iterates all JSON files in the `agents/` directory.

---

## 13. Test Suite

**Location**: `/home/amir/jarvis/backend/tests/`

**Framework**: pytest 8.3.3 with pytest-asyncio and pytest-cov.

**Runner**: `conftest.py` provides:
- `sync_db` fixture: SQLite in-memory database for fast testing.
- `agent_registry_data`, `tenant_data`, `user_data` fixtures: reusable test data.

### 13.1 `test_auth.py` -- Authentication Models

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_login_request`              | `LoginRequest` field validation                          |
| `test_register_request`           | `RegisterRequest` with tenant_slug                       |
| `test_token_response`             | `TokenResponse` defaults (token_type, expires_in)        |
| `test_auth_context`               | `AuthContext` with permissions list                      |

### 13.2 `test_registry.py` -- Agent Registry

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_register_agent`             | Registration persistence to DB                           |
| `test_agent_definition_validation`| Default values for status, model, temperature            |
| `test_agent_kpis`                 | KPI structure in agent definition                        |
| `test_agent_workflows_default`    | Workflows default to empty list                          |
| `test_agent_serialization`        | `model_dump()` correctness                               |
| `test_create_with_minimal_fields` | Agent with only required fields                          |
| `test_create_with_full_fields`    | Agent with all optional fields                           |

### 13.3 `test_execution.py` -- Execution Models

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_execution_request_creation` | `ExecutionRequest` field assignment                      |
| `test_execution_result_defaults`  | `ExecutionResult` default values (output_data, steps, error, duration_ms) |
| `test_workflow_step_defaults`     | `WorkflowStep` defaults (input_data, output_data, status, error) |
| `test_execution_with_steps`       | Result with step list                                    |

### 13.4 `test_knowledge.py` -- Knowledge Engine

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_chunk_text_basic`           | Text chunking algorithm produces multiple chunks          |
| `test_chunk_text_short`           | Short text returns single chunk                          |
| `test_chunk_text_empty`           | Empty string returns empty list                          |
| `test_chunk_text_none`            | None input returns empty list                            |
| `test_create_document`            | Document default values (embedding_status, is_active, chunk_count) |
| `test_document_with_chunks`       | Document with explicit chunk_count                       |
| `test_document_metadata`          | Document metadata dictionary                             |

### 13.5 `test_memory.py` -- Memory Engine

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_create_memory`              | Memory default importance and context                    |
| `test_memory_importance`          | Importance field assignment                              |
| `test_memory_expiry`              | TTL via expires_at                                       |
| `test_memory_entry_creation`      | Full memory entry creation                               |

### 13.6 `test_router.py` -- Intent Router

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_register_and_route`         | Regex pattern matching and agent slug resolution         |
| `test_no_match_returns_default`   | Fallback to default intent when no pattern matches       |
| `test_higher_priority_wins`       | Priority-based intent selection                          |
| `test_inactive_intent_not_matched`| Inactive intents are skipped                             |
| `test_classify_intent`            | Keyword-based intent classification (search/create/update/delete/analyze/compliance/query) |

### 13.7 `test_connectors.py` -- Connectors

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_connector_base_abstract`    | `ConnectorBase` cannot be instantiated directly          |
| `test_connector_auth_creation`    | `ConnectorAuth` with api_key type                        |
| `test_connector_response_success` | Success response structure                               |
| `test_connector_response_error`   | Error response structure                                 |
| `test_odoo_initialization`        | OdooConnector config/auth assignment                     |
| `test_odoo_health_check_false`    | Odoo health check returns false when uninitialized       |
| `test_notion_initialization`      | NotionConnector auth assignment                          |
| `test_whatsapp_initialization`    | WhatsAppConnector config assignment                      |
| `test_whatsapp_health_check_false`| WhatsApp health check returns false when uninitialized   |

### 13.8 `test_audit.py` -- Audit

| Test                              | What it covers                                           |
|-----------------------------------|----------------------------------------------------------|
| `test_create_audit_entry`         | AuditEntry with action, resource_type, resource_id, details |
| `test_audit_with_ip`              | AuditEntry with ip_address and user_agent                |
| `test_audit_defaults`             | Default values for details, user_id, resource_id         |

---

> **End of JARVIS Complete Architectural Documentation**
>
> This document covers 92 source files across all layers of the JARVIS AI Operating System.
