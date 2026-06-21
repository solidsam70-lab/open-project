# JARVIS Architecture

## System Architecture

### Layer Description

#### 1. API Layer (FastAPI)
- RESTful API endpoints
- WebSocket support for real-time communication
- Request validation via Pydantic
- Rate limiting and throttling
- API versioning (/api/v1/)

#### 2. Authentication Layer
- JWT-based authentication
- Multi-tenant isolation
- Role-based access control (Admin, Manager, Member, Agent)
- API key support for machine-to-machine
- Session management

#### 3. Agent Registry
- Central registry of all agents
- Configuration-driven agent definitions
- Dynamic agent loading from JSON/YAML
- Agent lifecycle management (draft, active, inactive, archived)
- Version tracking for agent configurations

#### 4. Workflow Engine
- Step-based workflow execution
- Support for LLM, Connector, Tool, and Condition step types
- Parallel step execution
- Retry and error handling
- Escalation triggers
- Execution audit trail

#### 5. Knowledge Engine (RAG)
- Document ingestion and chunking
- Vector embeddings with Qdrant
- Keyword search fallback
- Multi-source knowledge (Notion, Drive, Web, Internal)
- Source attribution in responses

#### 6. Memory Engine
- Short-term (conversation context)
- Long-term (user preferences, decisions)
- Importance-based retrieval
- TTL-based expiration
- Memory consolidation

#### 7. Connector Layer
- Abstract base class for all connectors
- Standardized execute(action, params) interface
- Health check capability
- OAuth2 and API key auth support
- Rate limiting and retry logic

#### 8. Odoo Integration Layer
- XML-RPC client for Odoo
- Model-agnostic CRUD operations
- Method call support
- Connection pooling
- Error mapping to Odoo exceptions

#### 9. Notification Layer
- Multi-channel notifications
- Slack, Email, WhatsApp, Teams
- Template-based messages
- Priority-based routing
- Delivery tracking

## Data Flow

```
User Request
    │
    ▼
API Layer ──► Auth Layer ──► Intent Router
                                    │
                                    ▼
                            Agent Registry
                                    │
                                    ▼
                            Workflow Engine
                            │     │     │
                    ┌───────┘     │     └───────┐
                    ▼             ▼             ▼
              Knowledge      Memory       Connectors
              Engine         Engine        (Odoo, Gmail,
                                              WhatsApp, etc.)
                    │             │             │
                    └───────┬─────┴─────────────┘
                            ▼
                      LLM Call
                            │
                            ▼
                      Response
```

## Multi-Tenant Design

### Data Isolation
- All database tables have `tenant_id` column
- Row-Level Security (RLS) ready
- Separate Qdrant collections per tenant: `jarvis_{tenant_id}`
- Redis namespace isolation: `jarvis:{tenant_id}:*`

### Configuration Isolation
- Per-tenant connector configurations
- Per-tenant agent registry
- Per-tenant knowledge base
- Per-tenant memory store

### Authentication Flow
```
User Login → Validate credentials → Generate JWT (contains tenant_id)
                                       │
                                       ▼
Each request → Validate JWT → Extract tenant_id → Scope all queries
```

## Agent Configuration Schema

Every agent is defined by a JSON configuration file:

```json
{
  "name": "Agent Name",
  "slug": "agent-slug",
  "role": "Role description",
  "goal": "Core mission",
  "model": "gpt-4o",
  "temperature": 0.3,
  "kpis": [{"name": "kpi_name", "target": 95, "unit": "percent"}],
  "knowledge_sources": [{"type": "notion", "database": "..."}],
  "memory_sources": [{"type": "conversation", "retention": 90}],
  "tools": ["tool_name"],
  "workflows": [{"name": "workflow_name", "steps": [...]}],
  "input_schema": {"type": "object", "properties": {...}},
  "output_schema": {"type": "object", "properties": {...}},
  "escalation_rules": [{"condition": "...", "escalate_to": "...", "timeout_minutes": 30}]
}
```

## Error Handling Strategy

### Layer-Specific Errors
- **Connector Layer**: Retry with exponential backoff, circuit breaker
- **Knowledge Layer**: Fallback from vector to keyword search
- **Workflow Engine**: Step-level error isolation, continue/stop on failure
- **LLM Layer**: Token limit handling, response validation

### Escalation Chain
```
Agent → Supervisor Agent → Human Manager → CEO
```

### Logging
- Structured JSON logging via Loguru
- Audit trail for all business actions
- Performance metrics for workflow execution
- Error aggregation for pattern detection
