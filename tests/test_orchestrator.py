from app.evaluation.grounding import GroundingEvaluator
from app.evaluation.orchestrator import EvaluationOrchestrator
from app.evaluation.evidence import ExactEvidenceMatcher
from app.evaluation.base import Evaluator
from app.evaluation.citation import CitationEvaluator
from app.evaluation.models import EvaluationFailure

from app.models.trace import (
    GenerationTrace,
    PerformanceTrace,
    RetrievedChunk,
    RetrievalTrace,
    Trace,
)


def create_grounding_trace(answer: str, evidence: str) -> Trace:
    return Trace(
        trace_id="orchestrator_test_001",
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


def test_orchestrator_accepts_evaluators():
    evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    orchestrator = EvaluationOrchestrator(
        evaluators=[evaluator]
    )

    assert len(orchestrator.evaluators) == 1
    assert orchestrator.evaluators[0] is evaluator


def test_orchestrator_runs_evaluators():
    evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    orchestrator = EvaluationOrchestrator(
        evaluators=[evaluator]
    )

    trace = create_grounding_trace(
        answer="Employees can carry forward up to 5 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    results = orchestrator.evaluate(trace)

    assert len(results) == 1
    assert results[0].score == 1.0


def test_orchestrator_runs_multiple_evaluators():
    class FakeEvaluator(Evaluator[str]):

        @property
        def name(self) -> str:
            return "fake"

        def evaluate(self, trace: Trace) -> str:
            return "fake-result"

    grounding_evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    fake_evaluator = FakeEvaluator()

    orchestrator = EvaluationOrchestrator(
        evaluators=[
            grounding_evaluator,
            fake_evaluator,
        ]
    )

    trace = create_grounding_trace(
        answer="Employees can carry forward up to 5 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    results = orchestrator.evaluate(trace)

    assert len(results) == 2
    assert results[0].score == 1.0
    assert results[1] == "fake-result"


def test_orchestrator_runs_grounding_and_citation_evaluators():
    grounding_evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    citation_evaluator = CitationEvaluator()

    orchestrator = EvaluationOrchestrator(
        evaluators=[
            grounding_evaluator,
            citation_evaluator,
        ]
    )

    trace = create_grounding_trace(
        answer="Employees can carry forward up to 5 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    trace.generation.citations = ["chunk_001"]

    results = orchestrator.evaluate(trace)

    assert len(results) == 2

    grounding_result = results[0]
    citation_result = results[1]

    assert grounding_result.score == 1.0
    assert citation_result.score == 1.0


def test_orchestrator_preserves_evaluation_order():
    class FirstEvaluator(Evaluator[str]):

        @property
        def name(self) -> str:
            return "first"

        def evaluate(self, trace: Trace) -> str:
            return "first"

    class SecondEvaluator(Evaluator[str]):

        @property
        def name(self) -> str:
            return "second"

        def evaluate(self, trace: Trace) -> str:
            return "second"

    first = FirstEvaluator()
    second = SecondEvaluator()

    orchestrator = EvaluationOrchestrator(
        evaluators=[first, second]
    )

    trace = create_grounding_trace(
        answer="Test answer.",
        evidence="Test evidence.",
    )

    results = orchestrator.evaluate(trace)

    assert results == ["first", "second"]


def test_orchestrator_continues_when_evaluator_fails():
    class FailingEvaluator(Evaluator[str]):

        @property
        def name(self) -> str:
            return "failing"

        def evaluate(self, trace: Trace) -> str:
            raise RuntimeError("Evaluator failed")

    class SuccessfulEvaluator(Evaluator[str]):

        @property
        def name(self) -> str:
            return "successful"

        def evaluate(self, trace: Trace) -> str:
            return "success"

    failing = FailingEvaluator()
    successful = SuccessfulEvaluator()

    orchestrator = EvaluationOrchestrator(
        evaluators=[
            failing,
            successful,
        ]
    )

    trace = create_grounding_trace(
        answer="Test answer.",
        evidence="Test evidence.",
    )

    results = orchestrator.evaluate(trace)

    assert len(results) == 2

    failure = results[0]

    assert isinstance(failure, EvaluationFailure)
    assert failure.evaluator == "failing"
    assert failure.error == "Evaluator failed"

    assert results[1] == "success"


def test_orchestrator_returns_failure_and_success_results():
    class FailingEvaluator(Evaluator[str]):

        @property
        def name(self) -> str:
            return "failing"

        def evaluate(self, trace: Trace) -> str:
            raise RuntimeError("Something went wrong")

    grounding_evaluator = GroundingEvaluator(
        matcher=ExactEvidenceMatcher()
    )

    orchestrator = EvaluationOrchestrator(
        evaluators=[
            FailingEvaluator(),
            grounding_evaluator,
        ]
    )

    trace = create_grounding_trace(
        answer="Employees can carry forward up to 5 days of annual leave.",
        evidence="Employees can carry forward up to 5 days of annual leave.",
    )

    results = orchestrator.evaluate(trace)

    assert len(results) == 2

    assert isinstance(results[0], EvaluationFailure)
    assert results[0].evaluator == "failing"
    assert results[0].error == "Something went wrong"

    assert results[1].score == 1.0