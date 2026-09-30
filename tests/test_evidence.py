import pytest

from app.evaluation.evidence import (
    EvidenceMatcher,
    ExactEvidenceMatcher,
)
from app.evaluation.models import Claim
from app.models.trace import RetrievedChunk


def create_chunk(
    chunk_id: str,
    text: str,
) -> RetrievedChunk:
    return RetrievedChunk(
        chunk_id=chunk_id,
        document_id="doc_001",
        text=text,
        score=0.95,
    )


def test_evidence_matcher_is_abstract():
    with pytest.raises(TypeError):
        EvidenceMatcher()


def test_evidence_matcher_requires_find_matches():
    assert hasattr(EvidenceMatcher, "find_matches")


def test_exact_match_returns_evidence():
    claim = Claim(
        text="Employees can carry forward up to 5 days of annual leave."
    )

    chunk = create_chunk(
        "chunk_001",
        "Employees can carry forward up to 5 days of annual leave.",
    )

    matcher = ExactEvidenceMatcher()

    matches = matcher.find_matches(claim, [chunk])

    assert len(matches) == 1
    assert matches[0].chunk_id == "chunk_001"
    assert matches[0].evidence_text == chunk.text
    assert matches[0].similarity_score == 1.0


def test_exact_match_is_case_insensitive():
    claim = Claim(
        text="employees can carry forward up to 5 days of annual leave."
    )

    chunk = create_chunk(
        "chunk_001",
        "Employees Can Carry Forward Up To 5 Days Of Annual Leave.",
    )

    matcher = ExactEvidenceMatcher()

    matches = matcher.find_matches(claim, [chunk])

    assert len(matches) == 1


def test_exact_match_normalizes_whitespace():
    claim = Claim(
        text="Employees can carry forward up to 5 days of annual leave."
    )

    chunk = create_chunk(
        "chunk_001",
        "Employees   can   carry forward   up to 5 days of annual leave.",
    )

    matcher = ExactEvidenceMatcher()

    matches = matcher.find_matches(claim, [chunk])

    assert len(matches) == 1


def test_exact_match_returns_empty_for_no_match():
    claim = Claim(
        text="Employees receive 30 days of annual leave."
    )

    chunk = create_chunk(
        "chunk_001",
        "Employees can carry forward up to 5 days of annual leave.",
    )

    matcher = ExactEvidenceMatcher()

    matches = matcher.find_matches(claim, [chunk])

    assert matches == []


def test_exact_match_returns_all_matching_chunks():
    claim = Claim(
        text="Employees can carry forward up to 5 days of annual leave."
    )

    chunks = [
        create_chunk(
            "chunk_001",
            "Employees can carry forward up to 5 days of annual leave.",
        ),
        create_chunk(
            "chunk_002",
            "Employees can carry forward up to 5 days of annual leave.",
        ),
        create_chunk(
            "chunk_003",
            "Employees receive 20 days of annual leave.",
        ),
    ]

    matcher = ExactEvidenceMatcher()

    matches = matcher.find_matches(claim, chunks)

    assert len(matches) == 2
    assert {match.chunk_id for match in matches} == {
        "chunk_001",
        "chunk_002",
    }