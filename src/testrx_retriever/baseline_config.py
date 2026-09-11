"""Configuration contract for the reproducible retrieval baseline."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ChunkingConfig:
    strategy: str = "token_window"
    chunk_size: int = 500
    chunk_overlap: int = 50

    def validate(self) -> None:
        if self.strategy != "token_window":
            raise ValueError(f"Unsupported baseline chunking strategy: {self.strategy}")
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")


@dataclass(frozen=True)
class TokenizerConfig:
    name: str = "testrx_regex_tokenizer"
    version: str = "1.0"


@dataclass(frozen=True)
class EmbeddingConfig:
    model: str = "stable_hashing_word_bigram"
    model_version: str = "1.0"
    dimension: int = 4096

    def validate(self) -> None:
        if self.dimension <= 0:
            raise ValueError("embedding dimension must be positive")


@dataclass(frozen=True)
class RetrievalConfig:
    algorithm: str = "cosine_similarity_exact"
    top_k: tuple[int, ...] = (1, 3, 5, 10)

    def validate(self) -> None:
        if self.algorithm != "cosine_similarity_exact":
            raise ValueError(f"Unsupported baseline retrieval algorithm: {self.algorithm}")
        if not self.top_k or any(k <= 0 for k in self.top_k):
            raise ValueError("top_k must contain positive integers")
        if tuple(sorted(set(self.top_k))) != self.top_k:
            raise ValueError("top_k must be unique and sorted")


@dataclass(frozen=True)
class BaselineConfig:
    schema_version: str
    document_path: Path
    golden_dataset_path: Path
    output_directory: Path
    chunking: ChunkingConfig
    tokenizer: TokenizerConfig
    embedding: EmbeddingConfig
    retrieval: RetrievalConfig

    @classmethod
    def from_dict(cls, value: dict[str, Any], base_directory: Path = Path(".")) -> "BaselineConfig":
        config = cls(
            schema_version=str(value["schema_version"]),
            document_path=(base_directory / value["document_path"]).resolve(),
            golden_dataset_path=(base_directory / value["golden_dataset_path"]).resolve(),
            output_directory=(base_directory / value["output_directory"]).resolve(),
            chunking=ChunkingConfig(**value["chunking"]),
            tokenizer=TokenizerConfig(**value["tokenizer"]),
            embedding=EmbeddingConfig(**value["embedding"]),
            retrieval=RetrievalConfig(
                algorithm=value["retrieval"]["algorithm"],
                top_k=tuple(value["retrieval"]["top_k"]),
            ),
        )
        config.validate()
        return config

    @classmethod
    def load(cls, path: Path) -> "BaselineConfig":
        value = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(value, path.resolve().parent.parent)

    def validate(self) -> None:
        self.chunking.validate()
        self.embedding.validate()
        self.retrieval.validate()

    def to_dict(self, root: Path | None = None) -> dict[str, Any]:
        def display(path: Path) -> str:
            if root is None:
                return str(path)
            try:
                return path.relative_to(root.resolve()).as_posix()
            except ValueError:
                return str(path)

        return {
            "schema_version": self.schema_version,
            "document_path": display(self.document_path),
            "golden_dataset_path": display(self.golden_dataset_path),
            "output_directory": display(self.output_directory),
            "chunking": {
                "strategy": self.chunking.strategy,
                "chunk_size": self.chunking.chunk_size,
                "chunk_overlap": self.chunking.chunk_overlap,
            },
            "tokenizer": {"name": self.tokenizer.name, "version": self.tokenizer.version},
            "embedding": {
                "model": self.embedding.model,
                "model_version": self.embedding.model_version,
                "dimension": self.embedding.dimension,
            },
            "retrieval": {"algorithm": self.retrieval.algorithm, "top_k": list(self.retrieval.top_k)},
        }
