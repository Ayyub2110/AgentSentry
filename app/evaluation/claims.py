import re

from app.evaluation.models import Claim


def extract_claims(answer: str) -> list[Claim]:
    sentences = re.split(r"(?<=[.!?])\s+", answer.strip())

    claims = []

    for sentence in sentences:
        sentence = sentence.strip()

        if sentence:
            claims.append(Claim(text=sentence))

    return claims