from functools import lru_cache

from app.services.approval_service import ApprovalService
from app.services.checkpoint_service import CheckpointService
from app.services.event_bus_service import EventBusService
from app.services.evaluation_service import EvaluationService
from app.services.guardrails_service import GuardrailsService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.llm_service import LLMService
from app.services.metrics_service import MetricsService
from app.services.recovery_service import RecoveryService
from app.services.runtime_service import RuntimeService


@lru_cache
def checkpoint_service() -> CheckpointService:
    return CheckpointService()


@lru_cache
def recovery_service() -> RecoveryService:
    return RecoveryService()


@lru_cache
def guardrails_service() -> GuardrailsService:
    return GuardrailsService()


@lru_cache
def evaluation_service() -> EvaluationService:
    return EvaluationService()


@lru_cache
def graph_service() -> KnowledgeGraphService:
    return KnowledgeGraphService()


@lru_cache
def approval_service() -> ApprovalService:
    return ApprovalService()


@lru_cache
def metrics_service() -> MetricsService:
    return MetricsService()


@lru_cache
def event_bus_service() -> EventBusService:
    return EventBusService()


@lru_cache
def llm_service() -> LLMService:
    return LLMService()


def runtime_service() -> RuntimeService:
    return RuntimeService(
        checkpoint_service=checkpoint_service(),
        recovery_service=recovery_service(),
        guardrails_service=guardrails_service(),
        evaluation_service=evaluation_service(),
        graph_service=graph_service(),
        approval_service=approval_service(),
        event_bus_service=event_bus_service(),
        llm_service=llm_service(),
    )
