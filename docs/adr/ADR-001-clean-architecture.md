# ADR-001: Clean Architecture with Service Modules

## Status
Accepted

## Decision
Use FastAPI route layer + service layer + persistence models to isolate orchestration from storage and HTTP.

## Consequences
- Easier module ownership per AgentOps capability
- Better testability with service-level unit tests
- Simplifies future worker extraction
