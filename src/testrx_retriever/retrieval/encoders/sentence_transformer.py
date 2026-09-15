"""Lazy adapter for a local or pinned Sentence Transformers bi-encoder."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import numpy as np


class SentenceTransformerBiEncoder:
    family = "contextual_attention"

    def __init__(self, spec: dict[str, Any]):
        self.model_id = str(spec["id"])
        self.model_path = str(spec["model_path"])
        self.revision = spec.get("revision")
        self.batch_size = int(spec.get("batch_size", 32))
        self.device = spec.get("device")
        self.query_prefix = str(spec.get("query_prefix", ""))
        self.document_prefix = str(spec.get("document_prefix", ""))
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "sentence-transformers is required for algorithm=sentence_transformer; "
                "install the project 'transformers' optional dependencies"
            ) from error
        load_options: dict[str, Any] = {"device": self.device}
        if self.revision and not Path(self.model_path).exists():
            load_options["revision"] = self.revision
        self.model = SentenceTransformer(self.model_path, **load_options)
        dimension_getter = getattr(self.model, "get_embedding_dimension", None)
        self.dimension = int(
            dimension_getter() if dimension_getter else self.model.get_sentence_embedding_dimension()
        )

    def _encode(self, texts: Sequence[str], prefix: str) -> np.ndarray:
        return np.asarray(self.model.encode(
            [prefix + text for text in texts], batch_size=self.batch_size, normalize_embeddings=True,
            convert_to_numpy=True, show_progress_bar=False,
        ), dtype=np.float32)

    def encode_documents(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts, self.document_prefix)

    def encode_queries(self, texts: Sequence[str]) -> np.ndarray:
        return self._encode(texts, self.query_prefix)

    def metadata(self) -> dict[str, Any]:
        return {
            "id": self.model_id,
            "family": self.family,
            "algorithm": "sentence_transformer",
            "model_path": self.model_path,
            "revision": self.revision,
            "dimension": self.dimension,
            "batch_size": self.batch_size,
            "device": self.device,
            "query_prefix": self.query_prefix,
            "document_prefix": self.document_prefix,
        }
