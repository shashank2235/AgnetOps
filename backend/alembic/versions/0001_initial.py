"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-01
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("workflow_id", sa.String(100), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("user_query", sa.Text(), nullable=False),
        sa.Column("final_response", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("trace_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "agent_steps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column("step_id", sa.String(100), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "checkpoints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), nullable=False),
        sa.Column("workflow_id", sa.String(100), nullable=False),
        sa.Column("step_id", sa.String(100), nullable=False),
        sa.Column("agent_name", sa.String(100), nullable=False),
        sa.Column("input", sa.JSON(), nullable=False),
        sa.Column("output", sa.JSON(), nullable=False),
        sa.Column("tool_calls", sa.JSON(), nullable=False),
        sa.Column("model_name", sa.String(100), nullable=False),
        sa.Column("prompt_version", sa.String(50), nullable=False),
        sa.Column("vector_context_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
    )
    op.create_table("tool_calls", sa.Column("id", sa.String(36), primary_key=True), sa.Column("run_id", sa.String(36), nullable=False), sa.Column("step_id", sa.String(100), nullable=False), sa.Column("tool_name", sa.String(100), nullable=False), sa.Column("args", sa.JSON(), nullable=False), sa.Column("result", sa.JSON(), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("guardrail_events", sa.Column("id", sa.String(36), primary_key=True), sa.Column("run_id", sa.String(36), nullable=False), sa.Column("category", sa.String(50), nullable=False), sa.Column("action", sa.String(20), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("details", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("approval_tasks", sa.Column("id", sa.String(36), primary_key=True), sa.Column("run_id", sa.String(36), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("reason", sa.Text(), nullable=False), sa.Column("proposed_response", sa.Text(), nullable=False), sa.Column("reviewer_notes", sa.Text(), nullable=True), sa.Column("reviewed_response", sa.Text(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("evaluation_results", sa.Column("id", sa.String(36), primary_key=True), sa.Column("run_id", sa.String(36), nullable=False), sa.Column("groundedness", sa.Float(), nullable=False), sa.Column("answer_relevance", sa.Float(), nullable=False), sa.Column("context_precision", sa.Float(), nullable=False), sa.Column("overall_score", sa.Float(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("trace_events", sa.Column("id", sa.String(36), primary_key=True), sa.Column("run_id", sa.String(36), nullable=False), sa.Column("trace_id", sa.String(64), nullable=False), sa.Column("span_name", sa.String(150), nullable=False), sa.Column("attributes", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_table("recovery_actions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("run_id", sa.String(36), nullable=False), sa.Column("action_type", sa.String(30), nullable=False), sa.Column("from_step", sa.String(100), nullable=True), sa.Column("to_step", sa.String(100), nullable=True), sa.Column("root_cause_summary", sa.Text(), nullable=False), sa.Column("metadata", sa.JSON(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_table("recovery_actions")
    op.drop_table("trace_events")
    op.drop_table("evaluation_results")
    op.drop_table("approval_tasks")
    op.drop_table("guardrail_events")
    op.drop_table("tool_calls")
    op.drop_table("checkpoints")
    op.drop_table("agent_steps")
    op.drop_table("agent_runs")
