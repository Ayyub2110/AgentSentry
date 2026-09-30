# importing the libraries
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RetrievedChunk:
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory = dict)

@dataclass
class RetrievalTrace:
    query: str
    chunks: list[RetrievedChunk]
    retriever: str

@dataclass
class GenerationTrace:
    model: str
    answer: str
    citations: list[str] = field(default_factory=list)
    prompt_version: str | None = None

@dataclass
class PerformanceTrace:
    latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost: float

@dataclass
class Trace:
    trace_id: str
    timestamp: datetime
    application_id: str

    user_query: str

    retrieval: RetrievalTrace
    generation: GenerationTrace
    performance: PerformanceTrace

    metadata: dict[str, Any] = field(default_factory = dict)