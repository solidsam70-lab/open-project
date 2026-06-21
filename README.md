# JARVIS - AI Operating System for AKS Solutions

JARVIS is an AI Operating System that sits on top of Odoo ERP and becomes the primary interface employees use to access knowledge, execute workflows, receive recommendations, and interact with business systems.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                   │
├─────────────────────────────────────────────────────────┤
│                  Authentication Layer                     │
├─────────────────────────────────────────────────────────┤
│                    Agent Registry                         │
├─────────────────────────────────────────────────────────┤
│                    Workflow Engine                        │
├─────────────────────────────────────────────────────────┤
│    Knowledge Engine    │    Memory Engine                  │
├─────────────────────────────────────────────────────────┤
│                   Connector Layer                         │
├─────────────────────────────────────────────────────────┤
│               Odoo Integration Layer                      │
├─────────────────────────────────────────────────────────┤
│                 Notification Layer                        │
└─────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Alembic
- **AI**: OpenAI/Ollama, Qdrant, RAG, Multi-Agent
- **Database**: PostgreSQL, Redis
- **Frontend**: Next.js, React, TypeScript, Tailwind (future)
- **Deployment**: Docker, Docker Compose

## Project Structure

```
jarvis/
├── backend/
│   ├── jarvis_core/           # Core platform
│   │   ├── registry/          # Agent registry (models, service, interface)
│   │   ├── router/            # Intent router
│   │   ├── execution/         # Workflow execution engine
│   │   ├── memory/            # Memory layer
│   │   ├── knowledge/         # Knowledge/RAG layer
│   │   ├── auth/              # Authentication & multi-tenant
│   │   ├── audit/             # Audit logging
│   │   └── prompts/           # System prompts
│   ├── connectors/
│   │   ├── odoo/              # Odoo ERP connector
│   │   ├── notion/            # Notion connector
│   │   ├── whatsapp/          # WhatsApp Business connector
│   │   ├── gmail/             # Gmail connector
│   │   └── github/            # GitHub connector
│   ├── api/                   # FastAPI routes (v1)
│   ├── database/              # SQLAlchemy models & session
│   ├── tests/                 # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── agents/                    # Agent JSON configurations
├── docker-compose.yml
└── docs/
    ├── revenue_workflows.md
    └── architecture.md
```

## MVP Agents

1. **Chief of Staff** - Executive coordination and task delegation
2. **Odoo Consultant** - Odoo implementation and configuration
3. **ETA Compliance** - Egyptian Tax Authority compliance
4. **Lead Qualification** - Lead scoring and routing
5. **Accountant Assistant** - Financial operations support
6. **Property Matching** - Real estate matching

### AKS Business Agents

**Sales**: SDR, Proposal, CRM
**Marketing**: Content, LinkedIn, SEO
**Operations**: Project Manager, Client Success
**Technical**: Odoo Consultant, Solution Architect, QA, DevOps
**Executive**: CEO Chief of Staff, Business Analyst, Revenue Analyst

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL 16+
- Docker & Docker Compose (optional)

### Local Development

```bash
# Clone the repository
git clone https://github.com/aks-solutions/jarvis.git
cd jarvis

# Set up Python environment
python -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn jarvis.api.main:app --reload --port 8000
```

### Docker Deployment

```bash
docker-compose up -d
```

### Load Agent Configurations

```bash
curl -X POST http://localhost:8000/api/v1/agents/load-config \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"config_path": "/app/agents/chief_of_staff.json"}'
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/{tenant_slug}` - Login
- `POST /api/v1/auth/register/{tenant_slug}` - Register

### Agents
- `POST /api/v1/agents/register` - Register agent
- `GET /api/v1/agents/` - List agents
- `GET /api/v1/agents/{id}` - Get agent
- `GET /api/v1/agents/slug/{slug}` - Get agent by slug
- `PUT /api/v1/agents/{id}` - Update agent
- `DELETE /api/v1/agents/{id}` - Delete agent

### Execution
- `POST /api/v1/execution/run` - Execute workflow
- `GET /api/v1/execution/{id}` - Get execution result

### Knowledge
- `POST /api/v1/knowledge/ingest` - Ingest document
- `GET /api/v1/knowledge/search` - Search knowledge
- `GET /api/v1/knowledge/documents/{id}` - Get document
- `DELETE /api/v1/knowledge/documents/{id}` - Delete document

### Memory
- `POST /api/v1/memory/store` - Store memory
- `GET /api/v1/memory/recent` - Get recent memory
- `GET /api/v1/memory/search` - Search memory

### Connectors
- `POST /api/v1/connectors/configure` - Configure connector
- `GET /api/v1/connectors/` - List connectors

## Multi-Tenant Architecture

Each tenant (company) has:
- Isolated data scope (tenant_id on all records)
- Separate Qdrant collection for vector search
- Configurable connector configurations
- Custom agent registry
- Audit log isolation

## Connectors

| Connector | Type | Status |
|-----------|------|--------|
| Odoo | ERP | Production Ready |
| PostgreSQL | Database | Production Ready |
| Qdrant | Vector DB | Production Ready |
| Notion | Knowledge | Production Ready |
| Gmail | Communication | Production Ready |
| WhatsApp Business | Communication | Production Ready |
| GitHub | Development | Production Ready |
| Google Drive | Storage | Ready |
| Outlook | Communication | Ready |
| Slack | Communication | Ready |
| Microsoft Teams | Communication | Ready |
| Google Calendar | Meetings | Ready |
| Zoom | Meetings | Ready |

## License

Proprietary - AKS Solutions
