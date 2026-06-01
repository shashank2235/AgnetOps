# AgentOps Runtime

![CI](https://img.shields.io/badge/CI-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Release](https://img.shields.io/badge/release-v0.1.0-orange)

Enterprise-grade runtime for reliable AI agents with first-class disaster recovery, replay, and human-in-the-loop governance.

## Why This Project

- Built for production incidents, not only happy paths
- Replay and rollback from checkpoint with root-cause traceability
- Hybrid memory architecture: vector context and knowledge graph context
- Guardrails plus approval workflows for regulated domains
- OpenTelemetry-first design for debuggability and auditability

## Open Source Quality

- MIT License
- Contributing guide
- Security policy
- Code of conduct
- Issue and PR templates
- CI workflow for backend tests and frontend build
- Dependabot updates

Production-grade open-source AgentOps platform focused on enterprise agent reliability:
- Agent disaster recovery
- Replay from checkpoint
- Human-in-the-loop recovery
- AI incident root cause analysis
- Enterprise guardrails
- OpenTelemetry-first tracing
- Hybrid memory with Knowledge Graph + Vector DB

## Architecture

```mermaid
flowchart LR
  UI[React Dashboard] --> API[FastAPI AgentOps API]
  API --> RT[Agent Runtime LangGraph]
  RT --> CP[Checkpoint Service]
  RT --> GR[Guardrails Service]
  RT --> AP[Human Approval Service]
  RT --> EV[Evaluation Service]
  RT --> RC[Recovery Service]
  RT --> KG[Knowledge Graph Service]
  RT --> OBS[Observability Service]
  RT --> QV[Qdrant Vector Search]
  KG --> N4J[Neo4j]
  API --> PG[(PostgreSQL)]
  RT --> RS[(Redis Streams)]
  OBS --> JG[Jaeger OTLP]
```

## Dashboard Preview

![AgentOps Runtime Dashboard](docs/assets/dashboard.png)

## Folder Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── workflows/
│   ├── alembic/versions/
│   ├── tests/unit/
│   └── tests/integration/
├── frontend/
├── docs/adr/
├── k8s/
├── docker-compose.yml
└── .env.example
```

## Implemented Modules

1. agent-runtime: multi-step workflow execution and tool call lifecycle
2. checkpoint-service: step-level persistence and resume points
3. recovery-service: retry, rollback, replay metadata, root-cause summaries
4. guardrails-service: prompt injection, PII, unsafe domain checks from YAML policy
5. observability-service: OpenTelemetry spans and Jaeger export
6. evaluation-service: ragas-style groundedness/relevance/precision scoring
7. knowledge-graph-service: Neo4j context facade + vector link IDs
8. human-approval-service: pending queue + approve/reject/edit decision APIs
9. frontend-dashboard: runs, approvals, statuses, trace IDs

## API Endpoints

- `POST /api/v1/agents/run`
- `GET /api/v1/agents/runs/{run_id}`
- `POST /api/v1/agents/runs/{run_id}/resume`
- `POST /api/v1/agents/runs/{run_id}/retry`
- `POST /api/v1/agents/runs/{run_id}/rollback`
- `POST /api/v1/agents/runs/{run_id}/replay`
- `GET /api/v1/checkpoints/{run_id}`
- `POST /api/v1/checkpoints/{checkpoint_id}/resume`
- `GET /api/v1/approvals`
- `POST /api/v1/approvals/{approval_id}/approve`
- `POST /api/v1/approvals/{approval_id}/reject`
- `POST /api/v1/guardrails/check`
- `GET /api/v1/evaluations/{run_id}`
- `GET /api/v1/graph/context?query=...`
- `GET /api/v1/metrics`

## Quick Start

1. Copy env file:
```bash
cp .env.example .env
```

2. Start stack:
```bash
docker compose up --build
```

This starts a dedicated `recovery-worker` that consumes Redis Stream events for retry, rollback, and replay jobs.

3. Open services:
- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Jaeger: http://localhost:16686
- Neo4j: http://localhost:7474

## Sample Workflow: Medical Document Review Agent

1. User submits medical policy question
2. Runtime retrieves context chunks (Qdrant facade)
3. Runtime queries related entities (Neo4j facade)
4. Guardrail checks unsafe medical claims
5. Risky outputs are routed to human approval
6. Approved response is returned with citations
7. Evaluation scores are computed
8. OTel traces are exported to Jaeger

## Sample API Requests

Run an agent:
```bash
curl -X POST http://localhost:8000/api/v1/agents/run \
  -H "Content-Type: application/json" \
  -d '{"workflow_id":"medical_document_review","agent_name":"Medical Document Review Agent","query":"Can you prescribe dosage for this patient?"}'
```

List approvals:
```bash
curl http://localhost:8000/api/v1/approvals
```

Approve task:
```bash
curl -X POST http://localhost:8000/api/v1/approvals/<approval_id>/approve \
  -H "Content-Type: application/json" \
  -d '{"reviewer_notes":"Approved by medical reviewer","edited_response":"Consult licensed physician and follow policy 101."}'
```

## Test Commands

```bash
cd backend
pip install -e .[dev]
pytest -q
```

Run recovery worker locally:
```bash
cd backend
python worker.py
```

## Database Schema

Tables:
- agent_runs
- agent_steps
- checkpoints
- tool_calls
- guardrail_events
- approval_tasks
- evaluation_results
- trace_events
- recovery_actions

## Future Roadmap

1. Native Azure OpenAI and OpenAI tool-call adapters with token accounting
2. Real Qdrant retrieval and Neo4j graph write-back for agent decisions
3. Redis consumer workers for async replay/recovery execution
4. Multi-tenant RBAC, SSO, and audit-grade immutable event logs
5. Incident timeline UI and run-diff replay visualizations
6. Policy DSL with versioned rollout and canary guardrails
7. Kubernetes Helm chart with HPA, PDB, and secrets integration

See the expanded roadmap in docs/ROADMAP.md.
