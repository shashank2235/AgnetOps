from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import checkpoint_service
from app.db.session import get_db
from app.models.entities import AgentRun
from app.schemas.agent import CheckpointOut

router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])


@router.get("/{run_id}", response_model=list[CheckpointOut])
async def get_checkpoints(run_id: str, db: AsyncSession = Depends(get_db)) -> list[CheckpointOut]:
    rows = await checkpoint_service().get_run_checkpoints(db, run_id)
    return [
        CheckpointOut(id=r.id, run_id=r.run_id, step_id=r.step_id, status=r.status, timestamp=r.timestamp)
        for r in rows
    ]


@router.post("/{checkpoint_id}/resume")
async def resume_from_checkpoint(checkpoint_id: str, db: AsyncSession = Depends(get_db)) -> dict:
    cp = await checkpoint_service().get_by_id(db, checkpoint_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    run = await db.get(AgentRun, cp.run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    run.status = "resumed"
    await db.commit()
    return {"message": f"Run {run.id} resumed from checkpoint {checkpoint_id}", "step_id": cp.step_id}
