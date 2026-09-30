# importing the necessary libraries
from fastapi import APIRouter, status, HTTPException

from app.ingestion.mapper import trace_input_to_domain
from app.ingestion.schemas import TraceInput
from app.storage.trace_repository import TraceRepository

router = APIRouter()

@router.post("/traces", status_code=status.HTTP_201_CREATED)
def ingest_trace(trace_input: TraceInput):
    trace = trace_input_to_domain(trace_input)

    repository = TraceRepository()
    repository.save(trace)

    return {
        "trace_id": trace.trace_id,
        "status": "accepted",
    }


@router.get("/traces/{trace_id}")
def get_trace(trace_id: str):
    repository = TraceRepository()

    trace = repository.get_by_id(trace_id)

    if trace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trace '{trace_id}' not found",
        )

    return {
        "trace_id": trace.trace_id,
        "timestamp": trace.timestamp.isoformat(),
        "application_id": trace.application_id,
        "user_query": trace.user_query,
        "retrieval": {
            "query": trace.retrieval.query,
            "retriever": trace.retrieval.retriever,
            "chunks": [
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "text": chunk.text,
                    "score": chunk.score,
                    "metadata": chunk.metadata,
                }
                for chunk in trace.retrieval.chunks
            ],
        },

        "generation": {
            "model": trace.generation.model,
            "answer": trace.generation.answer,
            "citations": trace.generation.citations,
            "prompt_version": trace.generation.prompt_version,
        },

        "performance": {
            "latency_ms": trace.performance.latency_ms,
            "input_tokens": trace.performance.input_tokens,
            "output_tokens": trace.performance.output_tokens,
            "estimated_cost": trace.performance.estimated_cost
        },

        "metadata": trace.metadata,
    }