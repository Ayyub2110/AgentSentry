from app.evaluation.base import Evaluator
from app.evaluation.claims import extract_claims
from app.evaluation.evidence import EvidenceMatcher
from app.evaluation.models import (
    Claim,
    ClaimEvaluation,
    ClaimStatus,
    EvidenceMatch,
    GroundingEvaluation,
    GroundingLabel,
)
from app.models.trace import Trace


class GroundingEvaluator(Evaluator[GroundingEvaluation]):

    @property
    def name(self) -> str:
        return "grounding"

    def __init__(self, matcher: EvidenceMatcher):
        self.matcher = matcher

    def evaluate(self, trace: Trace) -> GroundingEvaluation:
        claims = extract_claims(trace.generation.answer)
        evidence_chunks = trace.retrieval.chunks

        claim_evaluations = []

        for claim in claims:
            claim_evaluation = self._evaluate_claim(
                claim,
                evidence_chunks,
            )

            claim_evaluations.append(claim_evaluation)

        score = self._calculate_score(claim_evaluations)
        label = self._calculate_label(score)

        return GroundingEvaluation(
            score=score,
            label=label,
            claims=claim_evaluations,
        )

    def _evaluate_claim(
        self,
        claim: Claim,
        evidence_chunks,
    ) -> ClaimEvaluation:
        matches = self.matcher.find_matches(
            claim,
            evidence_chunks,
        )

        if matches:
            return ClaimEvaluation(
                claim=claim,
                status=ClaimStatus.SUPPORTED,
                evidence=matches,
            )

        evidence = [
            EvidenceMatch(
                chunk_id=chunk.chunk_id,
                evidence_text=chunk.text,
                similarity_score=0.0,
            )
            for chunk in evidence_chunks
        ]

        return ClaimEvaluation(
            claim=claim,
            status=ClaimStatus.NOT_SUPPORTED,
            evidence=evidence,
        )

    def _calculate_score(
        self,
        claim_evaluations: list[ClaimEvaluation],
    ) -> float:
        if not claim_evaluations:
            return 0.0

        supported_claims = sum(
            evaluation.status == ClaimStatus.SUPPORTED
            for evaluation in claim_evaluations
        )

        return supported_claims / len(claim_evaluations)

    def _calculate_label(self, score: float) -> GroundingLabel:
        if score == 1.0:
            return GroundingLabel.GROUNDED

        if score == 0.0:
            return GroundingLabel.UNGROUNDED

        return GroundingLabel.PARTIALLY_GROUNDED