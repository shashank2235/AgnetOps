from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import AgentRun, AgentStep, ApprovalTask
from app.schemas.metrics import MetricsOut


class MetricsService:
    async def get_metrics(self, db: AsyncSession) -> MetricsOut:
        total_runs_q = await db.execute(select(func.count(AgentRun.id)))
        success_runs_q = await db.execute(select(func.count(AgentRun.id)).where(AgentRun.status == "completed"))
        latency_q = await db.execute(select(func.avg(AgentStep.latency_ms)))
        failed_steps_q = await db.execute(select(func.count(AgentStep.id)).where(AgentStep.status == "failed"))
        approvals_q = await db.execute(select(func.count(ApprovalTask.id)).where(ApprovalTask.status == "approved"))

        total_runs = int(total_runs_q.scalar_one() or 0)
        success_runs = int(success_runs_q.scalar_one() or 0)
        avg_latency = float(latency_q.scalar_one() or 0.0)
        failed_steps = int(failed_steps_q.scalar_one() or 0)
        approvals = int(approvals_q.scalar_one() or 0)

        success_rate = round(success_runs / total_runs, 3) if total_runs else 0.0

        return MetricsOut(
            success_rate=success_rate,
            avg_latency_ms=avg_latency,
            token_usage=0,
            failed_steps=failed_steps,
            approval_count=approvals,
        )
