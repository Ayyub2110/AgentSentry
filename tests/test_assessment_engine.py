from app.evaluation.assessment import AssessmentEngine
from app.evaluation.models import (
    Decision,
    GroundingEvaluation,
    GroundingLabel,
    RiskLevel,
)


def test_assessment_engine_returns_assessment():
    engine = AssessmentEngine()

    assessment = engine.assess([])

    assert assessment.risk == RiskLevel.LOW
    assert assessment.decision == Decision.PASS
    assert assessment.results == []


def test_fully_grounded_result_is_low_risk():
    engine = AssessmentEngine()

    result = GroundingEvaluation(
        score=1.0,
        label=GroundingLabel.GROUNDED,
        claims=[],
    )

    assessment = engine.assess([result])

    assert assessment.risk == RiskLevel.LOW
    assert assessment.decision == Decision.PASS


def test_partially_grounded_result_is_medium_risk():
    engine = AssessmentEngine()

    result = GroundingEvaluation(
        score=0.5,
        label=GroundingLabel.PARTIALLY_GROUNDED,
        claims=[],
    )

    assessment = engine.assess([result])

    assert assessment.risk == RiskLevel.MEDIUM
    assert assessment.decision == Decision.WARN


def test_ungrounded_result_is_high_risk():
    engine = AssessmentEngine()

    result = GroundingEvaluation(
        score=0.0,
        label=GroundingLabel.UNGROUNDED,
        claims=[],
    )

    assessment = engine.assess([result])

    assert assessment.risk == RiskLevel.HIGH
    assert assessment.decision == Decision.HUMAN_REVIEW