from datetime import datetime
from time import perf_counter
from uuid import uuid4

from opentelemetry import trace
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.entities import AgentRun, AgentStep, EvaluationResult, GuardrailEvent
from app.schemas.agent import EvaluationOut, GuardrailCheckOut
from app.services.approval_service import ApprovalService
from app.services.checkpoint_service import CheckpointService
from app.services.event_bus_service import EventBusService
from app.services.evaluation_service import EvaluationService
from app.services.guardrails_service import GuardrailsService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.llm_service import LLMService
from app.services.recovery_service import RecoveryService
from app.workflows.medical_workflow import build_medical_workflow


class RuntimeService:
    def __init__(
        self,
        checkpoint_service: CheckpointService,
        recovery_service: RecoveryService,
        guardrails_service: GuardrailsService,
        evaluation_service: EvaluationService,
        graph_service: KnowledgeGraphService,
        approval_service: ApprovalService,
        event_bus_service: EventBusService,
        llm_service: LLMService,
    ) -> None:
        self.checkpoint_service = checkpoint_service
        self.recovery_service = recovery_service
        self.guardrails_service = guardrails_service
        self.evaluation_service = evaluation_service
        self.graph_service = graph_service
        self.approval_service = approval_service
        self.event_bus_service = event_bus_service
        self.llm_service = llm_service
        self.tracer = trace.get_tracer("agentops.runtime")
        self.workflow = build_medical_workflow()

    async def start_run(self, db: AsyncSession, workflow_id: str, agent_name: str, query: str) -> AgentRun:
        run = AgentRun(
            id=str(uuid4()),
            workflow_id=workflow_id,
            agent_name=agent_name,
            user_query=query,
            trace_id=uuid4().hex,
            status="running",
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)
        await self.event_bus_service.publish("run_started", {"run_id": run.id, "workflow_id": workflow_id})

        try:
            with self.tracer.start_as_current_span("agent_execution"):
                workflow_state = self.workflow.invoke(
                    {"query": query, "contexts": [], "graph_entities": [], "guardrail_action": "", "answer": ""}
                )
                contexts = await self._retrieve_context(db, run, query)
                graph_context = await self._query_knowledge_graph(db, run, query)
                guardrail = await self._check_guardrails(db, run, query)

            draft = workflow_state.get("answer") or ""
            with self.tracer.start_as_current_span("llm_call"):
                model_draft = await self.llm_service.generate_medical_response(
                    query=query,
                    context_chunks=contexts,
                    graph_entities=graph_context.entities,
                )
            if model_draft:
                draft = model_draft
            elif not draft:
                draft = f"Based on medical policy context, answer to '{query}': review by clinician required."
            if guardrail.action == "block":
                run.status = "blocked"
                run.final_response = "Request blocked by guardrails."
            elif guardrail.action == "human_approval":
                task = await self.approval_service.create(
                    db, run.id, "Unsafe medical claim detected", draft
                )
                run.status = "awaiting_approval"
                run.final_response = f"Pending human approval task {task.id}."
            else:
                run.status = "completed"
                run.final_response = draft
                eval_result = await self.evaluation_service.evaluate(run.id, query, run.final_response, contexts)
                await self._store_eval(db, eval_result)
                await self.event_bus_service.publish("evaluation_completed", {"run_id": run.id, "score": eval_result.overall_score})

            await db.commit()
            await db.refresh(run)
            await self.event_bus_service.publish("run_finished", {"run_id": run.id, "status": run.status})
            return run
        except Exception as exc:  # pragma: no cover
            run.status = "failed"
            summary = await self.recovery_service.summarize_failure(exc)
            await self.recovery_service.record_action(
                db=db,
                run_id=run.id,
                action_type="failure_detected",
                from_step=None,
                to_step=None,
                root_cause_summary=summary,
                metadata={"error": str(exc)},
            )
            await db.commit()
            await db.refresh(run)
            await self.event_bus_service.publish("run_failed", {"run_id": run.id, "error": str(exc)})
            return run

    async def _retrieve_context(self, db: AsyncSession, run: AgentRun, query: str) -> list[str]:
        start = perf_counter()
        with self.tracer.start_as_current_span("retrieval"):
            contexts = ["chunk-001", "chunk-002", "chunk-003"]
        await self._record_step(db, run.id, "retrieval", 1, {"query": query}, {"chunks": contexts}, start)
        await self.checkpoint_service.save(
            db=db,
            run_id=run.id,
            workflow_id=run.workflow_id,
            step_id="retrieval",
            agent_name=run.agent_name,
            input_payload={"query": query},
            output_payload={"chunks": contexts},
            tool_calls=[{"tool": "qdrant_search"}],
            model_name=settings.llm_model,
            prompt_version=settings.prompt_version,
            vector_context_ids=contexts,
            status="completed",
        )
        await self.event_bus_service.publish("step_completed", {"run_id": run.id, "step_id": "retrieval"})
        return contexts

    async def _query_knowledge_graph(self, db: AsyncSession, run: AgentRun, query: str):
        start = perf_counter()
        with self.tracer.start_as_current_span("knowledge_graph"):
            context = await self.graph_service.get_related_context(query)
        await self._record_step(
            db,
            run.id,
            "knowledge_graph",
            2,
            {"query": query},
            {"entities": context.entities, "relations": context.relations},
            start,
        )
        await self.event_bus_service.publish("step_completed", {"run_id": run.id, "step_id": "knowledge_graph"})
        await self.checkpoint_service.save(
            db=db,
            run_id=run.id,
            workflow_id=run.workflow_id,
            step_id="knowledge_graph",
            agent_name=run.agent_name,
            input_payload={"query": query},
            output_payload={"entities": context.entities},
            tool_calls=[{"tool": "neo4j_query"}],
            model_name=settings.llm_model,
            prompt_version=settings.prompt_version,
            vector_context_ids=context.linked_chunk_ids,
            status="completed",
        )
        return context

    async def _check_guardrails(self, db: AsyncSession, run: AgentRun, query: str) -> GuardrailCheckOut:
        start = perf_counter()
        with self.tracer.start_as_current_span("guardrail_check"):
            guardrail = self.guardrails_service.check(query)
        await self._record_step(
            db,
            run.id,
            "guardrails",
            3,
            {"query": query},
            {"action": guardrail.action, "violations": guardrail.violations},
            start,
        )
        for violation in guardrail.violations:
            db.add(
                GuardrailEvent(
                    run_id=run.id,
                    category=violation,
                    action=guardrail.action,
                    severity="high" if guardrail.action in {"block", "human_approval"} else "medium",
                    details={"query": query},
                )
            )
        await self.checkpoint_service.save(
            db=db,
            run_id=run.id,
            workflow_id=run.workflow_id,
            step_id="guardrails",
            agent_name=run.agent_name,
            input_payload={"query": query},
            output_payload={"action": guardrail.action},
            tool_calls=[{"tool": "policy_engine"}],
            model_name=settings.llm_model,
            prompt_version=settings.prompt_version,
            vector_context_ids=[],
            status="completed",
        )
        await self.event_bus_service.publish(
            "step_completed",
            {"run_id": run.id, "step_id": "guardrails", "action": guardrail.action},
        )
        return guardrail

    async def _record_step(
        self,
        db: AsyncSession,
        run_id: str,
        step_id: str,
        order: int,
        input_payload: dict,
        output_payload: dict,
        start: float,
    ) -> None:
        latency_ms = int((perf_counter() - start) * 1000)
        db.add(
            AgentStep(
                run_id=run_id,
                step_id=step_id,
                step_order=order,
                input_payload=input_payload,
                output_payload=output_payload,
                status="completed",
                latency_ms=latency_ms,
                created_at=datetime.utcnow(),
            )
        )

    async def _store_eval(self, db: AsyncSession, result: EvaluationOut) -> None:
        db.add(
            EvaluationResult(
                run_id=result.run_id,
                groundedness=result.groundedness,
                answer_relevance=result.answer_relevance,
                context_precision=result.context_precision,
                overall_score=result.overall_score,
            )
        )

    async def get_run(self, db: AsyncSession, run_id: str) -> AgentRun | None:
        return await db.get(AgentRun, run_id)

    async def list_steps(self, db: AsyncSession, run_id: str) -> list[AgentStep]:
        rows = await db.execute(select(AgentStep).where(AgentStep.run_id == run_id).order_by(AgentStep.step_order))
        return list(rows.scalars().all())
