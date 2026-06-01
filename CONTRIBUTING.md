# Contributing to AgentOps Runtime

Thank you for helping improve AgentOps Runtime.

## Development Setup

1. Clone the repository.
2. Copy .env.example to .env and fill in your values.
3. Start dependencies with docker compose up -d postgres redis qdrant neo4j jaeger.
4. Run backend locally:
   - cd backend
   - pip install -e .[dev]
   - uvicorn app.main:app --reload --port 8000
5. Run frontend locally:
   - cd frontend
   - npm install
   - npm run dev

## Pull Request Guidelines

1. Open an issue first for large feature or architecture changes.
2. Keep PR scope narrow and include tests.
3. Follow existing module boundaries and service patterns.
4. Update README and ADRs when behavior or architecture changes.
5. Do not commit .env, secrets, keys, or generated folders.

## Commit Convention

Use conventional commits when possible:
- feat: new feature
- fix: bug fix
- docs: documentation changes
- test: test updates
- chore: maintenance

## Test Commands

Backend:
- cd backend
- pytest -q

Frontend:
- cd frontend
- npm run build

## Security

If you discover a vulnerability, do not open a public issue. See SECURITY.md.
