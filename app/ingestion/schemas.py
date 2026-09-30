from typing import Any

from pydantic import BaseModel, Field


class RetrievedChunkInput(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float = Field(..., ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalInput(BaseModel):
    query: str
    chunks: list[RetrievedChunkInput]
    retriever: str


class GenerationInput(BaseModel):
    model: str
    answer: str
    citations: list[str] = Field(default_factory=list)
    prompt_version: str | None = None


class PerformanceInput(BaseModel):
    latency_ms: float = Field(..., ge=0.0)
    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    estimated_cost: float = Field(..., ge=0.0)


class TraceInput(BaseModel):
    trace_id: str
    application_id: str
    user_query: str

    retrieval: RetrievalInput
    generation: GenerationInput
    performance: PerformanceInput

    metadata: dict[str, Any] = Field(default_factory=dict)