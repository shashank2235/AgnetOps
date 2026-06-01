from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AgentRunCreate(BaseModel):
    workflow_id: str = Field(default="medical_document_review")
    agent_name: str = Field(default="Medical Document Review Agent")
    query: str


class AgentRunResume(BaseModel):
    checkpoint_id: str | None = None


class AgentRunRollback(BaseModel):
    checkpoint_id: str


class AgentRunOut(BaseModel):
    run_id: str
    workflow_id: str
    agent_name: str
    status: str
    final_response: str | None = None
    trace_id: str | None = None
    created_at: datetime


class StepOut(BaseModel):
    id: str
    step_id: str
    status: str
    created_at: datetime


class RunDetailOut(AgentRunOut):
    steps: list[StepOut]


class CheckpointOut(BaseModel):
    id: str
    run_id: str
    step_id: str
    status: str
    timestamp: datetime


class GuardrailCheckIn(BaseModel):
    run_id: str | None = None
    text: str


class GuardrailCheckOut(BaseModel):
    action: Literal["allow", "warn", "block", "human_approval"]
    violations: list[str]


class ApprovalDecisionIn(BaseModel):
    reviewer_notes: str | None = None
    edited_response: str | None = None


class EvaluationOut(BaseModel):
    run_id: str
    groundedness: float
    answer_relevance: float
    context_precision: float
    overall_score: float
