"""Adapter for the historical lexical hashing encoder."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from ...baseline_config import EmbeddingConfig
from .lexical_hashing import StableHashingEmbedder


class HashingBiEncoder:
    family = "lexical"

    def __init__(self, spec: dict[str, Any]):
        self.model_id = str(spec["id"])
        self.dimension = int(spec.get("dimension", 8192))
        self.encoder = StableHashingEmbedder(EmbeddingConfig(
            model="stable_hashing_word_bigram",
            model_version="1.0",
            dimension=self.dimension,
        ))

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        return self.encoder.embed(texts)

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self.encoder.embed(texts)

    def metadata(self) -> dict[str, Any]:
        return {
            "id": self.model_id,
            "family": self.family,
            "algorithm": "stable_hashing_word_bigram",
            "version": "1.0",
            "dimension": self.dimension,
        }
