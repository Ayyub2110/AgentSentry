from app.evaluation.models import ClaimStatus, GroundingLabel
from app.evaluation.grounding import GroundingEvaluator
from app.models.trace import (
    GenerationTrace,
    PerformanceTrace,
    RetrievedChunk,
    RetrievalTrace,
    Trace,
)
from app.evaluation.evidence import ExactEvidenceMatcher


def create_grounding_trace(answer: str, evidence: str) -> Trace:
    return Trace(
        trace_id="grounding_test_001",
        timestamp=None,
        application_id="test-app",
        user_query="How many days can employees carry forward?",
        retrieval=RetrievalTrace(
            query="How many days can employees carry forward?",
            retriever="test-retriever",
            chunks=[
                RetrievedChunk(
                    chunk_id="chunk_001",
                    document_id="doc_001",
                    text=evidence,
                    score=0.95,
                )
            ],
        ),
        generation=GenerationTrace(
            model="test-model",
            answer=answer,
        ),
        performance=PerformanceTrace(
            latency_ms=100,
            input_tokens=100,
            output_tokens=20,
            estimated_cost=0.001,
        ),
    )


def test_supported_claim():
    trace = create_grounding_trace(
        answer="Employees can carry forward up to 5 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    result = evaluator.evaluate(trace)

    assert result.label == GroundingLabel.GROUNDED
    assert result.score == 1.0
    assert len(result.claims) == 1

    claim_evaluation = result.claims[0]

    assert claim_evaluation.status == ClaimStatus.SUPPORTED
    assert claim_evaluation.evidence[0].chunk_id == "chunk_001"


def test_contradicted_claim():
    trace = create_grounding_trace(
        answer="Employees can carry forward up to 10 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    result = evaluator.evaluate(trace)

    assert result.label == GroundingLabel.UNGROUNDED
    assert result.score == 0.0
    assert len(result.claims) == 1

    claim_evaluation = result.claims[0]

    assert claim_evaluation.status == ClaimStatus.NOT_SUPPORTED
    assert claim_evaluation.evidence[0].chunk_id == "chunk_001"


def test_not_supported_claim():
    trace = create_grounding_trace(
        answer="Employees receive 30 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    result = evaluator.evaluate(trace)

    assert result.label == GroundingLabel.UNGROUNDED
    assert result.score == 0.0
    assert len(result.claims) == 1

    claim_evaluation = result.claims[0]

    assert claim_evaluation.status == ClaimStatus.NOT_SUPPORTED


def test_partially_grounded_answer():
    trace = create_grounding_trace(
        answer=(
            "Employees can carry forward up to 5 days of annual leave. "
            "Employees receive a 30% bonus."
        ),
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    result = evaluator.evaluate(trace)

    assert result.label == GroundingLabel.PARTIALLY_GROUNDED
    assert result.score == 0.5
    assert len(result.claims) == 2

    assert result.claims[0].status == ClaimStatus.SUPPORTED
    assert result.claims[1].status == ClaimStatus.NOT_SUPPORTED


def test_grounding_evaluator_uses_evidence_matcher():
    trace = create_grounding_trace(
        answer="Employees can carry forward up to 5 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    matcher = ExactEvidenceMatcher()
    evaluator = GroundingEvaluator(matcher=matcher)

    result = evaluator.evaluate(trace)

    assert result.label == GroundingLabel.GROUNDED
    assert result.score == 1.0
    assert result.claims[0].status == ClaimStatus.SUPPORTED
    assert result.claims[0].evidence[0].chunk_id == "chunk_001"