import json
from datetime import datetime

from app.models.trace import (
    GenerationTrace,
    RetrievalTrace,
    PerformanceTrace,
    RetrievedChunk,
    Trace,
)
from app.models.trace import Trace
from app.storage.database import get_connection


class TraceRepository:

    def save(self, trace: Trace) -> None:
        connection = get_connection()

        trace_data = {
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
                "estimated_cost": trace.performance.estimated_cost,
            },
            "metadata": trace.metadata,
        }

        connection.execute(
            """
            INSERT INTO traces (
                trace_id,
                timestamp,
                application_id,
                user_query,
                trace_data
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                trace.trace_id,
                trace.timestamp.isoformat(),
                trace.application_id,
                trace.user_query,
                json.dumps(trace_data),
            ),
        )

        connection.commit()
        connection.close()

    def get_by_id(self, trace_id: str) -> Trace | None:
        connection = get_connection()


        row = connection.execute(
            """
            SELECT trace_data
            FROM traces
            WHERE trace_id = ?
            """,
            (trace_id,),
        ).fetchone()


        connection.close()

        if row is None:
            return None

        data = json.loads(row["trace_data"])

        chunks = [
            RetrievedChunk(
                chunk_id = chunk["chunk_id"],
                document_id = chunk["document_id"],
                text = chunk["text"],
                score = chunk["score"],
                metadata = chunk["metadata"],
            )
            for chunk in data["retrieval"]["chunks"]
        ]

        retrieval = RetrievalTrace(
            query= data["retrieval"]["query"],
            chunks=chunks,
            retriever = data["retrieval"]["retriever"],
        )

        generation = GenerationTrace(
            model = data["generation"]["model"],
            answer= data["generation"]["answer"],
            citations = data["generation"]["citations"],
            prompt_version = data["generation"]["prompt_version"],
        )

        performance = PerformanceTrace(
            latency_ms = data["performance"]["latency_ms"],
            input_tokens = data["performance"]["input_tokens"],
            output_tokens = data["performance"]["output_tokens"],
            estimated_cost = data["performance"]["estimated_cost"],
        )

        return Trace(
            trace_id = data["trace_id"],
            timestamp = datetime.fromisoformat(data["timestamp"]),
            application_id = data["application_id"],
            user_query = data["user_query"],
            retrieval = retrieval,
            generation = generation,
            performance = performance,
            metadata = data["metadata"],
        )