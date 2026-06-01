from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import RecoveryAction


class RecoveryService:
    async def record_action(
        self,
        db: AsyncSession,
        run_id: str,
        action_type: str,
        from_step: str | None,
        to_step: str | None,
        root_cause_summary: str,
        metadata: dict,
    ) -> RecoveryAction:
        action = RecoveryAction(
            run_id=run_id,
            action_type=action_type,
            from_step=from_step,
            to_step=to_step,
            root_cause_summary=root_cause_summary,
            metadata_=metadata,
        )
        db.add(action)
        await db.commit()
        await db.refresh(action)
        return action

    async def summarize_failure(self, error: Exception) -> str:
        return f"Run failed due to: {error.__class__.__name__}: {error}"
