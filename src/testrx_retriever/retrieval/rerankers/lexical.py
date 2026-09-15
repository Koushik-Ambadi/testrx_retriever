"""Deterministic query-document pair scorer used to validate reranking flow."""

from __future__ import annotations

from typing import Any

from ..encoders.lexical_hashing import StableHashingEmbedder
from ..indexes import RetrievedChunk


class LexicalPairwiseReranker:
    def __init__(self, spec: dict[str, Any]):
        self.model_id = str(spec["id"])

    @staticmethod
    def _score(query: str, document: str) -> float:
        query_words = StableHashingEmbedder._words(query)
        document_words = StableHashingEmbedder._words(document)
        query_set, document_set = set(query_words), set(document_words)
        if not query_set or not document_set:
            return 0.0
        intersection = len(query_set & document_set)
        coverage = intersection / len(query_set)
        jaccard = intersection / len(query_set | document_set)
        query_bigrams = set(zip(query_words, query_words[1:]))
        document_bigrams = set(zip(document_words, document_words[1:]))
        bigram_coverage = (
            len(query_bigrams & document_bigrams) / len(query_bigrams)
            if query_bigrams else 0.0
        )
        return 0.60 * coverage + 0.25 * jaccard + 0.15 * bigram_coverage

    def rerank(self, query: str, candidates: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        scored = [(self._score(query, item.chunk.text), item) for item in candidates]
        scored.sort(key=lambda pair: (-round(pair[0], 12), pair[1].rank, pair[1].chunk.chunk_index))
        return [
            RetrievedChunk(rank=rank, chunk_id=item.chunk_id, score=round(score, 10), chunk=item.chunk)
            for rank, (score, item) in enumerate(scored[:top_k], start=1)
        ]

    def rerank_many(
        self, queries: list[str], candidate_groups: list[list[RetrievedChunk]], top_k: int
    ) -> list[list[RetrievedChunk]]:
        return [self.rerank(query, candidates, top_k) for query, candidates in zip(queries, candidate_groups)]

    def metadata(self) -> dict[str, Any]:
        return {"id": self.model_id, "family": "pairwise_lexical", "algorithm": "lexical_pairwise_baseline"}
