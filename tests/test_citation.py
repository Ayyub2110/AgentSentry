from app.evaluation.citation import CitationEvaluator
from app.evaluation.models import CitationValidationResult
from app.models.trace import (
    GenerationTrace,
    PerformanceTrace,
    RetrievedChunk,
    RetrievalTrace,
    Trace,
)


def create_citation_trace(citations: list[str]) -> Trace:
    return Trace(
        trace_id="citation_test_001",
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
                    text="Employees can carry forward up to 5 days of annual leave.",
                    score=0.95,
                ),
                RetrievedChunk(
                    chunk_id="chunk_002",
                    document_id="doc_002",
                    text="Employees receive annual leave according to company policy.",
                    score=0.90,
                ),
            ],
        ),
        generation=GenerationTrace(
            model="test-model",
            answer="Employees can carry forward up to 5 days of annual leave.",
            citations=citations,
        ),
        performance=PerformanceTrace(
            latency_ms=100,
            input_tokens=100,
            output_tokens=20,
            estimated_cost=0.001,
        ),
    )


def test_valid_citation():
    trace = create_citation_trace(
        citations=["chunk_001"]
    )

    evaluator = CitationEvaluator()

    result = evaluator.evaluate(trace)

    assert isinstance(result, CitationValidationResult)
    assert result.score == 1.0
    assert len(result.citations) == 1

    citation = result.citations[0]

    assert citation.valid is True
    assert citation.citation == "chunk_001"


def test_invalid_citation():
    trace = create_citation_trace(
        citations=["chunk_999"]
    )

    evaluator = CitationEvaluator()

    result = evaluator.evaluate(trace)

    assert result.score == 0.0
    assert len(result.citations) == 1

    citation = result.citations[0]

    assert citation.valid is False
    assert citation.citation == "chunk_999"


def test_mixed_citations():
    trace = create_citation_trace(
        citations=["chunk_001", "chunk_999"]
    )

    evaluator = CitationEvaluator()

    result = evaluator.evaluate(trace)

    assert result.score == 0.5
    assert len(result.citations) == 2

    assert result.citations[0].valid is True
    assert result.citations[1].valid is False


def test_no_citations():
    trace = create_citation_trace(
        citations=[]
    )

    evaluator = CitationEvaluator()

    result = evaluator.evaluate(trace)

    assert result.score == 1.0
    assert result.citations == []