"""Pairwise reranker implementations and factory."""

from __future__ import annotations

from typing import Any, Protocol

from ..indexes import RetrievedChunk


class Reranker(Protocol):
    model_id: str

    def rerank(self, query: str, candidates: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]: ...

    def metadata(self) -> dict[str, Any]: ...


def build_reranker(spec: dict[str, Any]) -> Reranker:
    algorithm = spec["algorithm"]
    if algorithm == "lexical_pairwise_baseline":
        from .lexical import LexicalPairwiseReranker

        return LexicalPairwiseReranker(spec)
    if algorithm == "sentence_transformer_cross_encoder":
        from .sentence_transformer import SentenceTransformerCrossEncoder

        return SentenceTransformerCrossEncoder(spec)
    raise ValueError(f"Unsupported reranker algorithm: {algorithm}")


__all__ = ["Reranker", "build_reranker"]
