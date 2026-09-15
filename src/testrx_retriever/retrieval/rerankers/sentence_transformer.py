"""Lazy adapter for a local or pinned Sentence Transformers cross-encoder."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..indexes import RetrievedChunk


class SentenceTransformerCrossEncoder:
    def __init__(self, spec: dict[str, Any]):
        self.model_id = str(spec["id"])
        self.model_path = str(spec["model_path"])
        self.revision = spec.get("revision")
        self.batch_size = int(spec.get("batch_size", 32))
        self.device = spec.get("device")
        try:
            from sentence_transformers import CrossEncoder
        except ImportError as error:
            raise RuntimeError(
                "sentence-transformers is required for the transformer cross-encoder; "
                "install the project 'transformers' optional dependencies"
            ) from error
        load_options: dict[str, Any] = {"device": self.device}
        if self.revision and not Path(self.model_path).exists():
            load_options["revision"] = self.revision
        self.model = CrossEncoder(self.model_path, **load_options)
        self._score_cache: dict[tuple[str, str], float] = {}

    def rerank(self, query: str, candidates: list[RetrievedChunk], top_k: int) -> list[RetrievedChunk]:
        scores = self.model.predict(
            [(query, item.chunk.text) for item in candidates],
            batch_size=self.batch_size, show_progress_bar=False,
        )
        scored = [(float(score), item) for score, item in zip(scores, candidates)]
        scored.sort(key=lambda pair: (-round(pair[0], 12), pair[1].rank, pair[1].chunk.chunk_index))
        return [
            RetrievedChunk(rank=rank, chunk_id=item.chunk_id, score=round(score, 10), chunk=item.chunk)
            for rank, (score, item) in enumerate(scored[:top_k], start=1)
        ]

    def rerank_many(
        self, queries: list[str], candidate_groups: list[list[RetrievedChunk]], top_k: int
    ) -> list[list[RetrievedChunk]]:
        keyed_pairs = [
            ((query, candidate.chunk_id), (query, candidate.chunk.text))
            for query, candidates in zip(queries, candidate_groups)
            for candidate in candidates
        ]
        missing: dict[tuple[str, str], tuple[str, str]] = {}
        for key, pair in keyed_pairs:
            if key not in self._score_cache:
                missing.setdefault(key, pair)
        if missing:
            keys = list(missing)
            scores = self.model.predict(
                [missing[key] for key in keys], batch_size=self.batch_size,
                show_progress_bar=False,
            )
            self._score_cache.update((key, float(score)) for key, score in zip(keys, scores))
        all_scores = [self._score_cache[key] for key, _ in keyed_pairs]
        output: list[list[RetrievedChunk]] = []
        offset = 0
        for candidates in candidate_groups:
            scores = all_scores[offset: offset + len(candidates)]
            offset += len(candidates)
            scored = [(float(score), item) for score, item in zip(scores, candidates)]
            scored.sort(key=lambda pair: (-round(pair[0], 12), pair[1].rank, pair[1].chunk.chunk_index))
            output.append([
                RetrievedChunk(rank=rank, chunk_id=item.chunk_id, score=round(score, 10), chunk=item.chunk)
                for rank, (score, item) in enumerate(scored[:top_k], start=1)
            ])
        return output

    def metadata(self) -> dict[str, Any]:
        return {
            "id": self.model_id,
            "family": "contextual_attention_cross_encoder",
            "algorithm": "sentence_transformer_cross_encoder",
            "model_path": self.model_path,
            "revision": self.revision,
            "batch_size": self.batch_size,
            "device": self.device,
        }
