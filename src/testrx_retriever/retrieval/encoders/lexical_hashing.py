"""Small deterministic local embedding interface for the baseline."""

from __future__ import annotations

import hashlib
import math
import re
from typing import Iterable

import numpy as np

from ...baseline_config import EmbeddingConfig


EMBEDDING_MODEL = "stable_hashing_word_bigram"
EMBEDDING_MODEL_VERSION = "1.0"
WORD_PATTERN = re.compile(r"\w+(?:[._/-]\w+)*", re.UNICODE)


class StableHashingEmbedder:
    """Stateless signed feature hashing over normalized words and bigrams.

    This is deliberately a reproducible lexical baseline, not a learned semantic
    model. It never downloads weights and has no fit-time corpus state.
    """

    def __init__(self, config: EmbeddingConfig):
        config.validate()
        if config.model != EMBEDDING_MODEL or config.model_version != EMBEDDING_MODEL_VERSION:
            raise ValueError(
                f"Unsupported embedding model/version: {config.model} {config.model_version}"
            )
        self.config = config
        self.model = config.model
        self.model_version = config.model_version
        self.dimension = config.dimension

    @staticmethod
    def _words(text: str) -> list[str]:
        return [match.group(0).casefold() for match in WORD_PATTERN.finditer(text)]

    @staticmethod
    def _features(words: list[str]) -> Iterable[tuple[str, float]]:
        for word in words:
            yield f"u:{word}", 1.0
        for left, right in zip(words, words[1:]):
            yield f"b:{left}\x1f{right}", 1.5

    def embed_one(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimension, dtype=np.float32)
        for feature, weight in self._features(self._words(text)):
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "little") % self.dimension
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += np.float32(sign * weight)
        norm = math.sqrt(float(np.dot(vector, vector)))
        if norm:
            vector /= np.float32(norm)
        return vector

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        rows = [self.embed_one(text) for text in texts]
        if not rows:
            return np.empty((0, self.dimension), dtype=np.float32)
        return np.stack(rows).astype(np.float32, copy=False)
