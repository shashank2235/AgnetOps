from app.schemas.agent import EvaluationOut


class EvaluationService:
    async def evaluate(self, run_id: str, query: str, answer: str, contexts: list[str]) -> EvaluationOut:
        groundedness = 0.9 if contexts else 0.5
        answer_relevance = 0.88 if query.lower().split()[0] in answer.lower() else 0.8
        context_precision = 0.86 if len(contexts) > 0 else 0.4
        overall = round((groundedness + answer_relevance + context_precision) / 3, 3)
        return EvaluationOut(
            run_id=run_id,
            groundedness=groundedness,
            answer_relevance=answer_relevance,
            context_precision=context_precision,
            overall_score=overall,
        )
