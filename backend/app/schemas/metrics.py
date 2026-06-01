from pydantic import BaseModel


class MetricsOut(BaseModel):
    success_rate: float
    avg_latency_ms: float
    token_usage: int
    failed_steps: int
    approval_count: int
