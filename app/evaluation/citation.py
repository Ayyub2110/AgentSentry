from app.evaluation.base import Evaluator
from app.evaluation.models import (
    CitationEvaluation,
    CitationValidationResult,
)
from app.models.trace import Trace


class CitationEvaluator(Evaluator[CitationValidationResult]):

    @property
    def name(self) -> str:
        return "citation"

    def evaluate(self, trace: Trace) -> CitationValidationResult:
        retrieved_chunk_ids = {
            chunk.chunk_id
            for chunk in trace.retrieval.chunks
        }

        evaluations = []

        for citation in trace.generation.citations:
            if citation in retrieved_chunk_ids:
                evaluations.append(
                    CitationEvaluation(
                        valid=True,
                        citation=citation,
                        reason="Citation refers to a retrieved chunk.",
                    )
                )
            else:
                evaluations.append(
                    CitationEvaluation(
                        valid=False,
                        citation=citation,
                        reason="Citation does not refer to any retrieved chunk.",
                    )
                )

        score = self._calculate_score(evaluations)

        return CitationValidationResult(
            score=score,
            citations=evaluations,
        )

    def _calculate_score(
        self,
        evaluations: list[CitationEvaluation],
    ) -> float:
        if not evaluations:
            return 1.0

        valid_citations = sum(
            evaluation.valid
            for evaluation in evaluations
        )

        return valid_citations / len(evaluations)