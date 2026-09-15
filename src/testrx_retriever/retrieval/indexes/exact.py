"""Exact cosine vector index for the first retrieval baseline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, Sequence

import numpy as np

from ..chunking import Chunk


class Encoder(Protocol):
    def encode_documents(self, texts: Sequence[str]) -> np.ndarray: ...
    def encode_queries(self, texts: Sequence[str]) -> np.ndarray: ...


@dataclass(frozen=True)
class RetrievedChunk:
    rank: int
    chunk_id: str
    score: float
    chunk: Chunk

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "chunk_id": self.chunk_id,
            "score": self.score,
            "text": self.chunk.text,
            "metadata": {
                key: value
                for key, value in self.chunk.to_dict().items()
                if key not in {"chunk_id", "text"}
            },
        }


class ExactVectorIndex:
    """In-memory normalized-vector index with deterministic tie breaking."""

    algorithm = "cosine_similarity_exact"

    def __init__(self, embedder: Any):
        self.embedder = embedder
        self.chunks: tuple[Chunk, ...] = ()
        self.embeddings = np.empty((0, int(getattr(embedder, "dimension", 0))), dtype=np.float32)

    def build_index(self, chunks: Sequence[Chunk]) -> None:
        if not chunks:
            raise ValueError("Cannot build an index without chunks")
        self.chunks = tuple(chunks)
        texts = [chunk.text for chunk in chunks]
        if hasattr(self.embedder, "encode_documents"):
            self.embeddings = self.embedder.encode_documents(texts)
        else:
            self.embeddings = self.embedder.embed(texts)

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if not self.chunks:
            raise RuntimeError("Index has not been built")
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if hasattr(self.embedder, "encode_queries"):
            query_vector = self.embedder.encode_queries([query])[0]
        else:
            query_vector = self.embedder.embed_one(query)
        raw_scores = self.embeddings @ query_vector
        ranked_indices = sorted(
            range(len(self.chunks)),
            key=lambda index: (
                -round(float(raw_scores[index]), 12),
                self.chunks[index].chunk_index,
                self.chunks[index].chunk_id,
            ),
        )[: min(top_k, len(self.chunks))]
        return [
            RetrievedChunk(
                rank=rank,
                chunk_id=self.chunks[index].chunk_id,
                score=round(float(raw_scores[index]), 10),
                chunk=self.chunks[index],
            )
            for rank, index in enumerate(ranked_indices, start=1)
        ]

    def save_embeddings(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            np.save(handle, self.embeddings, allow_pickle=False)
