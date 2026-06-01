from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Checkpoint


class CheckpointService:
    async def save(
        self,
        db: AsyncSession,
        run_id: str,
        workflow_id: str,
        step_id: str,
        agent_name: str,
        input_payload: dict,
        output_payload: dict,
        tool_calls: list,
        model_name: str,
        prompt_version: str,
        vector_context_ids: list[str],
        status: str,
    ) -> Checkpoint:
        checkpoint = Checkpoint(
            run_id=run_id,
            workflow_id=workflow_id,
            step_id=step_id,
            agent_name=agent_name,
            input=input_payload,
            output=output_payload,
            tool_calls=tool_calls,
            model_name=model_name,
            prompt_version=prompt_version,
            vector_context_ids=vector_context_ids,
            status=status,
        )
        db.add(checkpoint)
        await db.commit()
        await db.refresh(checkpoint)
        return checkpoint

    async def get_run_checkpoints(self, db: AsyncSession, run_id: str) -> list[Checkpoint]:
        rows = await db.execute(select(Checkpoint).where(Checkpoint.run_id == run_id).order_by(Checkpoint.timestamp))
        return list(rows.scalars().all())

    async def get_by_id(self, db: AsyncSession, checkpoint_id: str) -> Checkpoint | None:
        return await db.get(Checkpoint, checkpoint_id)
