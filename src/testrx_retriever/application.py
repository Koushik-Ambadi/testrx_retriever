"""Configurable query-to-chunks application boundary."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import time
from typing import Any

from .baseline_config import ChunkingConfig, find_project_root
from .retrieval import build_bi_encoder, build_reranker
from .retrieval.hierarchical_chunking import build_chunker
from .retrieval.indexes import ExactVectorIndex, RetrievedChunk
from .retrieval.tokenization import RegexTokenizer


@dataclass(frozen=True)
class RetrievalApplicationConfig:
    """Resolved configuration for the reusable retrieval application."""

    schema_version: str
    document_path: Path
    chunking: ChunkingConfig
    encoder: dict[str, Any]
    reranker: dict[str, Any] | None
    candidate_k: int
    top_k: int

    @classmethod
    def load(cls, path: Path) -> "RetrievalApplicationConfig":
        value = json.loads(path.read_text(encoding="utf-8"))
        root = find_project_root(path)

        def resolve_model_path(spec: dict[str, Any] | None) -> dict[str, Any] | None:
            if spec is None:
                return None
            resolved = dict(spec)
            if "model_path" in resolved:
                model_path = Path(resolved["model_path"])
                if not model_path.is_absolute():
                    resolved["model_path"] = str((root / model_path).resolve())
            return resolved

        config = cls(
            schema_version=str(value["schema_version"]),
            document_path=(root / value["inputs"]["document_path"]).resolve(),
            chunking=ChunkingConfig(**value["chunking"]),
            encoder=resolve_model_path(value["encoder"]) or {},
            reranker=resolve_model_path(value.get("reranker")),
            candidate_k=int(value["retrieval"]["candidate_k"]),
            top_k=int(value["retrieval"]["top_k"]),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError(f"Unsupported application schema_version: {self.schema_version}")
        self.chunking.validate()
        if not self.document_path.is_file():
            raise ValueError(f"Document does not exist: {self.document_path}")
        if not self.encoder.get("id") or not self.encoder.get("algorithm"):
            raise ValueError("encoder requires id and algorithm")
        if self.reranker is not None and (
            not self.reranker.get("id") or not self.reranker.get("algorithm")
        ):
            raise ValueError("reranker requires id and algorithm")
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.candidate_k < self.top_k:
            raise ValueError("candidate_k must be at least top_k")


class RetrievalApplication:
    """Load the fixed corpus once and serve repeated query-to-chunk calls."""

    def __init__(self, config: RetrievalApplicationConfig):
        config.validate()
        self.config = config
        document = json.loads(config.document_path.read_text(encoding="utf-8"))
        self.chunks = tuple(
            build_chunker(config.chunking, RegexTokenizer()).chunk_document(document)
        )
        self.encoder = build_bi_encoder(config.encoder)
        self.index = ExactVectorIndex(self.encoder)
        self.index.build_index(self.chunks)
        self.reranker = build_reranker(config.reranker) if config.reranker else None

    @classmethod
    def from_config(cls, path: Path | str) -> "RetrievalApplication":
        return cls(RetrievalApplicationConfig.load(Path(path).resolve()))

    def retrieve(
        self, query: str, *, candidate_k: int | None = None, top_k: int | None = None,
    ) -> dict[str, Any]:
        """Return ranked chunks with provenance and measured retrieval-stage latency."""
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query cannot be empty")
        resolved_candidate_k = self.config.candidate_k if candidate_k is None else int(candidate_k)
        resolved_top_k = self.config.top_k if top_k is None else int(top_k)
        if resolved_top_k <= 0:
            raise ValueError("top_k must be positive")
        if resolved_candidate_k < resolved_top_k:
            raise ValueError("candidate_k must be at least top_k")

        if self.reranker is not None:
            cycle_started = time.perf_counter_ns()
            candidate_started = time.perf_counter_ns()
            candidates = self.index.retrieve(normalized_query, resolved_candidate_k)
            candidate_finished = time.perf_counter_ns()
            rerank_started = time.perf_counter_ns()
            results = self.reranker.rerank(normalized_query, candidates, resolved_top_k)
            finished = time.perf_counter_ns()
            timing = {
                "candidate_retrieval_ns": candidate_finished - candidate_started,
                "reranking_ns": finished - rerank_started,
                "total_retrieval_cycle_ns": finished - cycle_started,
                "candidate_result_count": len(candidates),
            }
        else:
            started = time.perf_counter_ns()
            candidates = self.index.retrieve(normalized_query, resolved_candidate_k)
            finished = time.perf_counter_ns()
            results = [
                RetrievedChunk(rank=rank, chunk_id=item.chunk_id, score=item.score, chunk=item.chunk)
                for rank, item in enumerate(candidates[:resolved_top_k], start=1)
            ]
            timing = {
                "candidate_retrieval_ns": finished - started,
                "reranking_ns": 0,
                "total_retrieval_cycle_ns": finished - started,
                "candidate_result_count": len(candidates),
            }

        return {
            "schema_version": "1.0",
            "query": normalized_query,
            "configuration": {
                "chunking_strategy": self.config.chunking.strategy,
                "chunk_max_tokens": self.config.chunking.max_tokens,
                "encoder_id": self.config.encoder["id"],
                "reranker_id": self.config.reranker["id"] if self.config.reranker else None,
                "candidate_k": resolved_candidate_k,
                "top_k": resolved_top_k,
            },
            "result_count": len(results),
            "total_chunk_tokens": sum(item.chunk.token_count for item in results),
            "timing": timing,
            "chunks": [item.to_dict() for item in results],
        }
