import pytest

from app.evaluation.base import Evaluator
from app.evaluation.models import GroundingEvaluation
from app.evaluation.grounding import GroundingEvaluator

from app.evaluation.models import (
    CitationValidationResult,
    EvaluationResult,
    GroundingEvaluation,
)

def test_evaluator_is_abstract():
    with pytest.raises(TypeError):
        Evaluator()


def test_grounding_evaluator_implements_evaluator():
    assert issubclass(
        GroundingEvaluator,
        Evaluator,
    )


def test_evaluation_results_share_common_type():
    assert issubclass(
        GroundingEvaluation,
        EvaluationResult,
    )

    assert issubclass(
        CitationValidationResult,
        EvaluationResult,
    )