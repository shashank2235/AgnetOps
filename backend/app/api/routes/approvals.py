from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import approval_service
from app.db.session import get_db
from app.schemas.agent import ApprovalDecisionIn

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("")
async def list_approvals(db: AsyncSession = Depends(get_db)) -> list[dict]:
    tasks = await approval_service().list_pending(db)
    return [
        {
            "id": t.id,
            "run_id": t.run_id,
            "status": t.status,
            "reason": t.reason,
            "proposed_response": t.proposed_response,
            "reviewed_response": t.reviewed_response,
            "reviewer_notes": t.reviewer_notes,
            "created_at": t.created_at,
        }
        for t in tasks
    ]


@router.post("/{approval_id}/approve")
async def approve_task(approval_id: str, payload: ApprovalDecisionIn, db: AsyncSession = Depends(get_db)) -> dict:
    task = await approval_service().decide(
        db, approval_id, True, payload.reviewer_notes, payload.edited_response
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Approval task not found")
    return {"id": task.id, "status": task.status}


@router.post("/{approval_id}/reject")
async def reject_task(approval_id: str, payload: ApprovalDecisionIn, db: AsyncSession = Depends(get_db)) -> dict:
    task = await approval_service().decide(
        db, approval_id, False, payload.reviewer_notes, payload.edited_response
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Approval task not found")
    return {"id": task.id, "status": task.status}
