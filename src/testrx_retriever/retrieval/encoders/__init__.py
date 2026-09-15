"""Bi-encoder implementations and factory."""

from __future__ import annotations

from typing import Any, Protocol, Sequence

import numpy as np

from .hashing import HashingBiEncoder
from .lsa import LatentSemanticBiEncoder


class BiEncoder(Protocol):
    model_id: str
    family: str

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray: ...

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray: ...

    def metadata(self) -> dict[str, Any]: ...


def build_bi_encoder(spec: dict[str, Any]) -> BiEncoder:
    algorithm = spec["algorithm"]
    if algorithm == "stable_hashing_word_bigram":
        return HashingBiEncoder(spec)
    if algorithm == "latent_semantic_lsa":
        return LatentSemanticBiEncoder(spec)
    if algorithm == "sentence_transformer":
        from .sentence_transformer import SentenceTransformerBiEncoder

        return SentenceTransformerBiEncoder(spec)
    raise ValueError(f"Unsupported bi-encoder algorithm: {algorithm}")


__all__ = ["BiEncoder", "build_bi_encoder"]
