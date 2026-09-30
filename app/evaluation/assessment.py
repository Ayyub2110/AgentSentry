from app.evaluation.models import (
    Assessment,
    Decision,
    EvaluationResult,
    GroundingEvaluation,
    GroundingLabel,
    RiskLevel,
)


class AssessmentEngine:

    def assess(
        self,
        results: list[EvaluationResult],
    ) -> Assessment:

        risk = RiskLevel.LOW
        decision = Decision.PASS

        for result in results:

            if isinstance(result, GroundingEvaluation):

                if result.label == GroundingLabel.UNGROUNDED:
                    risk = RiskLevel.HIGH
                    decision = Decision.HUMAN_REVIEW

                elif result.label == GroundingLabel.PARTIALLY_GROUNDED:
                    risk = RiskLevel.MEDIUM
                    decision = Decision.WARN

        return Assessment(
            risk=risk,
            decision=decision,
            results=results,
        )