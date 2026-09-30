from app.evaluation.models import (
    EvaluationFailure,
    EvaluationResult,
)
from app.evaluation.base import Evaluator
from app.models.trace import Trace


class EvaluationOrchestrator:
    def __init__(self, evaluators: list[Evaluator]):
        self.evaluators = evaluators

    def evaluate(self, trace: Trace) -> list[EvaluationResult]:
        results = []

        for evaluator in self.evaluators:
            try:
                result = evaluator.evaluate(trace)
            except Exception as exc:
                result = EvaluationFailure(
                    evaluator.name,
                    error=str(exc),
                )

            results.append(result)

        return results