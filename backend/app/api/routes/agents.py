from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import checkpoint_service, event_bus_service, recovery_service, runtime_service
from app.db.session import get_db
from app.models.entities import AgentRun
from app.schemas.agent import AgentRunCreate, AgentRunOut, AgentRunResume, AgentRunRollback, RunDetailOut, StepOut

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/run", response_model=AgentRunOut)
async def run_agent(payload: AgentRunCreate, db: AsyncSession = Depends(get_db)) -> AgentRunOut:
    svc = runtime_service()
    run = await svc.start_run(db, payload.workflow_id, payload.agent_name, payload.query)
    return AgentRunOut(
        run_id=run.id,
        workflow_id=run.workflow_id,
        agent_name=run.agent_name,
        status=run.status,
        final_response=run.final_response,
        trace_id=run.trace_id,
        created_at=run.created_at,
    )


@router.get("/runs/{run_id}", response_model=RunDetailOut)
async def get_run(run_id: str, db: AsyncSession = Depends(get_db)) -> RunDetailOut:
    svc = runtime_service()
    run = await svc.get_run(db, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    steps = await svc.list_steps(db, run_id)
    return RunDetailOut(
        run_id=run.id,
        workflow_id=run.workflow_id,
        agent_name=run.agent_name,
        status=run.status,
        final_response=run.final_response,
        trace_id=run.trace_id,
        created_at=run.created_at,
        steps=[StepOut(id=s.id, step_id=s.step_id, status=s.status, created_at=s.created_at) for s in steps],
    )


@router.post("/runs/{run_id}/resume", response_model=AgentRunOut)
async def resume_run(run_id: str, payload: AgentRunResume, db: AsyncSession = Depends(get_db)) -> AgentRunOut:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")

    if payload.checkpoint_id:
        cp = await checkpoint_service().get_by_id(db, payload.checkpoint_id)
        if cp is None:
            raise HTTPException(status_code=404, detail="Checkpoint not found")

    run.status = "resumed"
    await db.commit()
    await db.refresh(run)
    return AgentRunOut(
        run_id=run.id,
        workflow_id=run.workflow_id,
        agent_name=run.agent_name,
        status=run.status,
        final_response=run.final_response,
        trace_id=run.trace_id,
        created_at=run.created_at,
    )


@router.post("/runs/{run_id}/retry", response_model=AgentRunOut)
async def retry_run(run_id: str, db: AsyncSession = Depends(get_db)) -> AgentRunOut:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    await event_bus_service().publish("retry_requested", {"run_id": run_id})
    run.status = "retry_queued"
    await db.commit()
    await db.refresh(run)
    return AgentRunOut(
        run_id=run.id,
        workflow_id=run.workflow_id,
        agent_name=run.agent_name,
        status=run.status,
        final_response=run.final_response,
        trace_id=run.trace_id,
        created_at=run.created_at,
    )


@router.post("/runs/{run_id}/rollback", response_model=AgentRunOut)
async def rollback_run(run_id: str, payload: AgentRunRollback, db: AsyncSession = Depends(get_db)) -> AgentRunOut:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    cp = await checkpoint_service().get_by_id(db, payload.checkpoint_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    await event_bus_service().publish(
        "rollback_requested",
        {"run_id": run_id, "checkpoint_id": cp.id, "target_step": cp.step_id},
    )
    run.status = "rollback_queued"
    await db.commit()
    await db.refresh(run)
    return AgentRunOut(
        run_id=run.id,
        workflow_id=run.workflow_id,
        agent_name=run.agent_name,
        status=run.status,
        final_response=run.final_response,
        trace_id=run.trace_id,
        created_at=run.created_at,
    )


@router.post("/runs/{run_id}/replay", response_model=AgentRunOut)
async def replay_run(run_id: str, db: AsyncSession = Depends(get_db)) -> AgentRunOut:
    run = await db.get(AgentRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    await event_bus_service().publish("replay_requested", {"run_id": run_id, "same_input": True})
    run.status = "replay_queued"
    await recovery_service().record_action(
        db=db,
        run_id=run_id,
        action_type="replay_requested",
        from_step=None,
        to_step=None,
        root_cause_summary="Replay with same inputs requested",
        metadata={"same_input": True},
    )
    await db.commit()
    await db.refresh(run)
    return AgentRunOut(
        run_id=run.id,
        workflow_id=run.workflow_id,
        agent_name=run.agent_name,
        status=run.status,
        final_response=run.final_response,
        trace_id=run.trace_id,
        created_at=run.created_at,
    )
