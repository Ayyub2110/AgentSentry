from app.evaluation.models import (
    Claim,
    ClaimEvaluation,
    ClaimStatus,
    EvidenceMatch,
    GroundingEvaluation,
    GroundingLabel,
)

from fastapi.testclient import TestClient
from app.main import app

import json
from datetime import datetime
import pytest
from app.ingestion.mapper import trace_input_to_domain
from app.ingestion.schemas import TraceInput
from app.storage.database import get_connection, initialize_database
from app.storage.trace_repository import TraceRepository



@pytest.fixture
def clean_database():
    initialize_database()

    connection = get_connection()

    connection.execute("DELETE FROM traces")
    connection.commit()
    connection.close()

    yield

def create_test_payload() -> dict:
    return {
        "trace_id": "trace_001",
        "application_id": "demo-hr-bot",
        "user_query": "How many days of annual leave can I carry forward?",
        "retrieval": {
            "query": "How many days of annual leave can I carry forward?",
            "retriever": "hybrid",
            "chunks": [
                {
                    "chunk_id": "chunk_001",
                    "document_id": "hr_policy_001",
                    "text": "Employees can carry forward up to 5 days of annual leave.",
                    "score": 0.91,
                    "metadata": {
                        "department": "HR",
                        "version": "2026.1",
                    },
                }
            ],
        },
        "generation": {
            "model": "test-model",
            "answer": "Employees can carry forward up to 5 days of annual leave.",
            "citations": ["chunk_001"],
            "prompt_version": "v1",
        },
        "performance": {
            "latency_ms": 842.5,
            "input_tokens": 1200,
            "output_tokens": 45,
            "estimated_cost": 0.0032,
        },
    }


def test_trace_input_validation():
    trace_input = TraceInput.model_validate(create_test_payload())

    assert trace_input.trace_id == "trace_001"
    assert trace_input.application_id == "demo-hr-bot"
    assert trace_input.retrieval.chunks[0].chunk_id == "chunk_001"
    assert trace_input.retrieval.chunks[0].score == 0.91
    assert trace_input.generation.model == "test-model"
    assert trace_input.generation.citations == ["chunk_001"]
    assert trace_input.performance.input_tokens == 1200


def test_trace_input_to_domain_model():
    trace_input = TraceInput.model_validate(create_test_payload())

    trace = trace_input_to_domain(trace_input)

    assert trace.trace_id == "trace_001"
    assert trace.application_id == "demo-hr-bot"
    assert trace.user_query == (
        "How many days of annual leave can I carry forward?"
    )

    assert trace.retrieval.retriever == "hybrid"
    assert len(trace.retrieval.chunks) == 1
    assert trace.retrieval.chunks[0].chunk_id == "chunk_001"

    assert trace.generation.model == "test-model"
    assert trace.generation.citations == ["chunk_001"]

    assert trace.performance.latency_ms == 842.5
    assert trace.performance.input_tokens == 1200

    assert isinstance(trace.timestamp, datetime)


def test_invalid_retrieval_score_is_rejected():
    payload = create_test_payload()

    payload["retrieval"]["chunks"][0]["score"] = 1.5

    try:
        TraceInput.model_validate(payload)
        assert False, "Expected validation to fail"
    except ValueError:
        pass

def test_trace_can_be_saved(clean_database):
    

    trace_input = TraceInput.model_validate(create_test_payload())
    trace = trace_input_to_domain(trace_input)

    repository = TraceRepository()
    repository.save(trace)

    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM traces WHERE trace_id = ?",
        ("trace_001",),
    ).fetchone()

    connection.close()

    assert row is not None
    assert row["trace_id"] == "trace_001"
    assert row["application_id"] == "demo-hr-bot"

    stored_trace = json.loads(row["trace_data"])

    assert stored_trace["trace_id"] == "trace_001"
    assert stored_trace["user_query"] == (
        "How many days of annual leave can I carry forward?"
    )
    assert stored_trace["retrieval"]["retriever"] == "hybrid"
    assert stored_trace["retrieval"]["chunks"][0]["document_id"] == "hr_policy_001"

    assert stored_trace["retrieval"]["chunks"][0]["score"] == 0.91

    assert stored_trace["generation"]["model"] == "test-model"
    assert stored_trace["generation"]["citations"] == ["chunk_001"]

    assert stored_trace["performance"]["input_tokens"] == 1200
    assert stored_trace["performance"]["output_tokens"] == 45


def test_trace_can_be_retrieved(clean_database):
    trace_input = TraceInput.model_validate(create_test_payload())
    original_trace = trace_input_to_domain(trace_input)

    repository = TraceRepository()
    repository.save(original_trace)

    retrieved_trace = repository.get_by_id("trace_001")

    assert retrieved_trace is not None

    assert retrieved_trace.trace_id == original_trace.trace_id
    assert retrieved_trace.application_id == original_trace.application_id
    assert retrieved_trace.user_query == original_trace.user_query


    assert (
        retrieved_trace.retrieval.query == original_trace.retrieval.query
    )

    assert len(retrieved_trace.retrieval.chunks)== 1

    assert (
        retrieved_trace.retrieval.chunks[0].chunk_id == original_trace.retrieval.chunks[0].chunk_id
    )

    assert (
        retrieved_trace.generation.answer == original_trace.generation.answer
    )

    assert(
        retrieved_trace.performance.input_tokens == original_trace.performance.input_tokens
    )


def test_missing_trace_returns_none(clean_database):
    repository = TraceRepository()

    result = repository.get_by_id("does_not_exist")

    assert result is None


def test_trace_api_end_to_end(clean_database):
    client = TestClient(app)

    payload = create_test_payload()

    # POST Trace
    post_response = client.post("/traces", json=payload)

    assert post_response.status_code == 201
    assert post_response.json() == {
        "trace_id": payload["trace_id"],
        "status": "accepted",
    }

    # GET Trace
    get_response = client.get(f"/traces/{payload['trace_id']}")

    assert get_response.status_code == 200

    data = get_response.json()

    assert data["trace_id"] == payload["trace_id"]
    assert data["application_id"] == payload["application_id"]
    assert data["user_query"] == payload["user_query"]

    assert data["retrieval"]["query"] == payload["retrieval"]["query"]
    assert data["retrieval"]["retriever"] == payload["retrieval"]["retriever"]

    assert data["generation"]["model"] == payload["generation"]["model"]
    assert data["generation"]["answer"] == payload["generation"]["answer"]

    assert data["performance"]["input_tokens"] == payload["performance"]["input_tokens"]
    assert data["performance"]["output_tokens"] == payload["performance"]["output_tokens"]


def test_get_missing_trace_returns_404(clean_database):
    client = TestClient(app)

    response = client.get("/traces/does_not_exist")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Trace 'does_not_exist' not found"
    }



def test_claim_evaluation_model():
    claim = Claim(
        text = "Employees can carry forward up to 5 days of annual leave."
    )

    evidence = EvidenceMatch(
        chunk_id = "chunk_001",
        evidence_text = "Employees can carry forward up to 5 days of annual leave.",
        similarity_score = 0.98,
    )

    evaluation = ClaimEvaluation(
        claim = claim,
        status = ClaimStatus.SUPPORTED,
        evidence = [evidence],
    )


    assert evaluation.claim.text == (
        "Employees can carry forward up to 5 days of annual leave."
    )
    assert evaluation.status == ClaimStatus.SUPPORTED
    assert len(evaluation.evidence) == 1
    assert evaluation.evidence[0].chunk_id == "chunk_001"

def test_grounding_evaluation_model():
    claim = Claim(
        text = "Employees can carry forward up to 5 days of annual leave."
    )

    evaluation = GroundingEvaluation(
        score = 1.0,
        label = GroundingLabel.GROUNDED,
        claims = [
            ClaimEvaluation(
                claim = claim,
                status = ClaimStatus.SUPPORTED,
            )
        ],
    )


    assert evaluation.score == 1.0
    assert evaluation.label == GroundingLabel.GROUNDED
    assert evaluation.claims[0].status == ClaimStatus.SUPPORTED


    