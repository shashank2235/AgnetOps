from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import guardrails_service, graph_service, metrics_service
from app.db.session import get_db
from app.models.entities import EvaluationResult
from app.schemas.agent import EvaluationOut, GuardrailCheckIn, GuardrailCheckOut

router = APIRouter(tags=["platform"])


@router.post("/guardrails/check", response_model=GuardrailCheckOut)
async def guardrail_check(payload: GuardrailCheckIn) -> GuardrailCheckOut:
    return guardrails_service().check(payload.text)


@router.get("/evaluations/{run_id}", response_model=EvaluationOut)
async def get_evaluation(run_id: str, db: AsyncSession = Depends(get_db)) -> EvaluationOut:
    row = await db.execute(select(EvaluationResult).where(EvaluationResult.run_id == run_id))
    eval_result = row.scalar_one_or_none()
    if eval_result is None:
        return EvaluationOut(
            run_id=run_id,
            groundedness=0,
            answer_relevance=0,
            context_precision=0,
            overall_score=0,
        )
    return EvaluationOut(
        run_id=run_id,
        groundedness=eval_result.groundedness,
        answer_relevance=eval_result.answer_relevance,
        context_precision=eval_result.context_precision,
        overall_score=eval_result.overall_score,
    )


@router.get("/graph/context")
async def graph_context(query: str = "medical policy") -> dict:
    ctx = await graph_service().get_related_context(query)
    return ctx.model_dump()


@router.get("/metrics")
async def metrics(db: AsyncSession = Depends(get_db)) -> dict:
    return (await metrics_service().get_metrics(db)).model_dump()
