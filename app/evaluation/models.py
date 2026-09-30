# importing the libraries
from dataclasses import dataclass, field
from enum import Enum


class EvaluationResult:
    pass


@dataclass
class EvaluationFailure(EvaluationResult):
    evaluator: str
    error: str

class ClaimStatus(str, Enum):
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    NOT_SUPPORTED = "not_supported"


class GroundingLabel(str, Enum):
    GROUNDED = "grounded"
    PARTIALLY_GROUNDED = "partially_grounded"
    UNGROUNDED = "ungrounded"

@dataclass 
class EvidenceMatch:
    chunk_id: str
    evidence_text: str
    similarity_score: float

@dataclass
class Claim:
    text:str

@dataclass
class ClaimEvaluation:
    claim: Claim
    status: ClaimStatus
    evidence: list[EvidenceMatch] = field(default_factory=list)


@dataclass
class GroundingEvaluation(EvaluationResult):
    score: float
    label: GroundingLabel
    claims: list[ClaimEvaluation] = field(default_factory=list)


@dataclass
class CitationEvaluation:
    valid: bool
    citation: str
    reason: str


@dataclass
class CitationValidationResult(EvaluationResult):
    score: float
    citations: list[CitationEvaluation]


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Decision(str, Enum):
    PASS = "pass"
    WARN = "warn"
    HUMAN_REVIEW = "human_review"
    RETRY = "retry"
    BLOCK = "block"


@dataclass
class Assessment:
    risk: RiskLevel
    decision: Decision
    results: list[EvaluationResult] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)