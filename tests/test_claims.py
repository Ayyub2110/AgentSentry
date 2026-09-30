# importing the packages and libraries
from app.evaluation.claims import extract_claims

def test_extract_single_claim():
    claims = extract_claims(
        "Employees can carry forward up to 5 days of annual leave."
    )

    assert len(claims) == 1
    assert claims[0].text == (
        "Employees can carry forward up to 5 days of annual leave."
    )

def test_extract_multiple_claims():
    claims = extract_claims(
        "Employees receive 20 days of annual leave. "
        "They can carry forward up to 5 days."
    )

    assert len(claims) == 2
    assert claims[0].text == "Employees receive 20 days of annual leave."
    assert claims[1].text == "They can carry forward up to 5 days."

def test_extract_claims_handles_multiple_punctuation_marks():
    claims = extract_claims(
        "Is annual leave transferable? Employees can carry forward 5 days."
    )

    assert len(claims) == 2

    assert claims[0].text == "Is annual leave transferable?"
    assert claims[1].text == "Employees can carry forward 5 days."


def test_extract_claims_handles_empty_answer():
    claims = extract_claims("")

    assert claims == []

