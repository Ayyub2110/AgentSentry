from app.evaluation.models import (
    Assessment,
    Decision,
    RiskLevel,
)


def test_assessment_can_be_created():
    assessment = Assessment(
        risk=RiskLevel.LOW,
        decision=Decision.PASS,
    )

    assert assessment.risk == RiskLevel.LOW
    assert assessment.decision == Decision.PASS
    assert assessment.results == []
    assert assessment.reasons == []


def test_assessment_can_contain_reasons():
    assessment = Assessment(
        risk=RiskLevel.HIGH,
        decision=Decision.HUMAN_REVIEW,
        reasons=[
            "Grounding score is below the acceptable threshold.",
            "Citation validation failed.",
        ],
    )

    assert assessment.risk == RiskLevel.HIGH
    assert assessment.decision == Decision.HUMAN_REVIEW
    assert len(assessment.reasons) == 2


def test_assessment_can_contain_evaluation_results():
    assessment = Assessment(
        risk=RiskLevel.LOW,
        decision=Decision.PASS,
        results=[],
    )

    assert assessment.results == []