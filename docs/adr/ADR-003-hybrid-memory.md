# ADR-003: Hybrid Memory (Vector + Graph)

## Status
Accepted

## Decision
Use Qdrant-style retrieval for semantic chunks and Neo4j for entity/relationship context.

## Consequences
- Improved grounding quality and explainability
- Explicit linking between structured graph entities and unstructured chunks
