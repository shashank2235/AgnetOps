import pytest

from app.services.evaluation_service import EvaluationService


@pytest.mark.asyncio
async def test_evaluation_scores() -> None:
    svc = EvaluationService()
    result = await svc.evaluate("run-1", "policy", "policy answer", ["chunk-1"])
    assert result.overall_score > 0
