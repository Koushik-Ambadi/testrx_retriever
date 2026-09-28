"""Corpus-fitted latent semantic bi-encoder baseline."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from ...configuration import EmbeddingConfig
from .lexical_hashing import StableHashingEmbedder


def _normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return np.divide(matrix, norms, out=np.zeros_like(matrix), where=norms != 0)


class LatentSemanticBiEncoder:
    """Projects hashed lexical vectors into a corpus-derived latent space.

    This is a real two-tower semantic baseline, but it is not an attention model.
    The document corpus is fitted once; queries are projected independently.
    """

    family = "static_semantic"

    def __init__(self, spec: dict[str, Any]):
        self.model_id = str(spec["id"])
        self.hash_dimension = int(spec.get("hash_dimension", 4096))
        self.requested_dimension = int(spec.get("latent_dimension", 128))
        if self.hash_dimension <= 0 or self.requested_dimension <= 0:
            raise ValueError("LSA dimensions must be positive")
        self.lexical = StableHashingEmbedder(EmbeddingConfig(
            model="stable_hashing_word_bigram",
            model_version="1.0",
            dimension=self.hash_dimension,
        ))
        self.components: np.ndarray | None = None
        self.dimension = 0

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        lexical = self.lexical.embed(texts)
        if not len(lexical):
            raise ValueError("Cannot fit LSA without documents")
        _, _, right = np.linalg.svd(lexical, full_matrices=False)
        self.dimension = min(self.requested_dimension, right.shape[0])
        self.components = right[: self.dimension].astype(np.float32, copy=False)
        return _normalize(lexical @ self.components.T)

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray:
        if self.components is None:
            raise RuntimeError("encode_documents must be called before encode_queries")
        return _normalize(self.lexical.embed(texts) @ self.components.T)

    def metadata(self) -> dict[str, Any]:
        return {
            "id": self.model_id,
            "family": self.family,
            "algorithm": "latent_semantic_lsa",
            "hash_dimension": self.hash_dimension,
            "requested_dimension": self.requested_dimension,
            "fitted_dimension": self.dimension,
        }
