# importing the packages and libraries
from datetime import datetime, timezone

from app.ingestion.schemas import TraceInput
from app.models.trace import (
    GenerationTrace,
    PerformanceTrace,
    RetrievedChunk,
    RetrievalTrace,
    Trace,
)


def trace_input_to_domain(trace_input: TraceInput) -> Trace:
    retrieval_chunks = [
        RetrievedChunk(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            text = chunk.text,
            score= chunk.score,
            metadata= chunk.metadata
        )
        for chunk in trace_input.retrieval.chunks
    ]

    retrieval = RetrievalTrace(
        query = trace_input.retrieval.query,
        chunks = retrieval_chunks,
        retriever = trace_input.retrieval.retriever,
    )

    generation = GenerationTrace(
        model = trace_input.generation.model,
        answer = trace_input.generation.answer,
        citations = trace_input.generation.citations,
        prompt_version = trace_input.generation.prompt_version,
    )

    performance = PerformanceTrace(
        latency_ms = trace_input.performance.latency_ms,
        input_tokens = trace_input.performance.input_tokens,
        output_tokens = trace_input.performance.output_tokens,
        estimated_cost = trace_input.performance.estimated_cost,
    )

    return Trace(
        trace_id = trace_input.trace_id,
        timestamp = datetime.now(timezone.utc),
        application_id = trace_input.application_id,
        user_query = trace_input.user_query,
        retrieval = retrieval,
        generation = generation,
        performance = performance,
        metadata = trace_input.metadata,
    )

    
