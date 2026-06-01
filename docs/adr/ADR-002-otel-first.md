# ADR-002: OpenTelemetry-First Observability

## Status
Accepted

## Decision
Instrument runtime operations and export traces to Jaeger via OTLP as default.

## Consequences
- End-to-end run visibility with trace IDs surfaced in API/dashboard
- Easier post-incident analysis across retrieval, guardrails, and approvals
