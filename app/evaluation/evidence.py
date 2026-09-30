import re
from abc import ABC, abstractmethod

from app.evaluation.models import Claim, EvidenceMatch
from app.models.trace import RetrievedChunk


class EvidenceMatcher(ABC):

    @abstractmethod
    def find_matches(
        self,
        claim: Claim,
        chunks: list[RetrievedChunk],
    ) -> list[EvidenceMatch]:
        pass


class ExactEvidenceMatcher(EvidenceMatcher):

    def find_matches(
        self,
        claim: Claim,
        chunks: list[RetrievedChunk],
    ) -> list[EvidenceMatch]:
        normalized_claim = self._normalize(claim.text)

        matches = []

        for chunk in chunks:
            normalized_chunk = self._normalize(chunk.text)

            if normalized_claim == normalized_chunk:
                matches.append(
                    EvidenceMatch(
                        chunk_id=chunk.chunk_id,
                        evidence_text=chunk.text,
                        similarity_score=1.0,
                    )
                )

        return matches

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip()).lower()