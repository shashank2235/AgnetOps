from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import ApprovalTask


class ApprovalService:
    async def list_pending(self, db: AsyncSession) -> list[ApprovalTask]:
        rows = await db.execute(select(ApprovalTask).order_by(ApprovalTask.created_at.desc()))
        return list(rows.scalars().all())

    async def create(self, db: AsyncSession, run_id: str, reason: str, proposed_response: str) -> ApprovalTask:
        task = ApprovalTask(run_id=run_id, reason=reason, proposed_response=proposed_response)
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task

    async def decide(
        self,
        db: AsyncSession,
        approval_id: str,
        approved: bool,
        reviewer_notes: str | None,
        edited_response: str | None,
    ) -> ApprovalTask | None:
        task = await db.get(ApprovalTask, approval_id)
        if task is None:
            return None
        task.status = "approved" if approved else "rejected"
        task.reviewer_notes = reviewer_notes
        task.reviewed_response = edited_response
        await db.commit()
        await db.refresh(task)
        return task
