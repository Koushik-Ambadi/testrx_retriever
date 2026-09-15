"""Runnable chunk -> retrieve -> fuse -> rerank -> evaluate flow."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import platform
import time
from typing import Any

import numpy as np

from ..common.files import read_jsonl, sha256, write_json, write_jsonl
from ..baseline_config import ChunkingConfig, find_project_root
from ..retrieval.chunking import Chunk, TokenChunker
from ..evaluation import evaluate_retrieval
from ..evaluation.model_comparison import analyze_model_comparison, render_model_comparison_report
from ..retrieval import build_bi_encoder, build_reranker
from ..retrieval.tokenization import RegexTokenizer
from ..retrieval.indexes import ExactVectorIndex, RetrievedChunk


class RerankedRetriever:
    def __init__(self, base: Any, reranker: Any, candidate_k: int):
        self.base = base
        self.reranker = reranker
        self.candidate_k = candidate_k
        self.prepared: dict[str, list[RetrievedChunk]] = {}

    def prepare(self, queries: list[str], top_k: int) -> None:
        candidate_groups = [self.base.retrieve(query, max(top_k, self.candidate_k)) for query in queries]
        if hasattr(self.reranker, "rerank_many"):
            groups = self.reranker.rerank_many(queries, candidate_groups, top_k)
        else:
            groups = [
                self.reranker.rerank(query, candidates, top_k)
                for query, candidates in zip(queries, candidate_groups)
            ]
        self.prepared = dict(zip(queries, groups))

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        if query in self.prepared:
            return self.prepared[query][:top_k]
        candidates = self.base.retrieve(query, max(top_k, self.candidate_k))
        return self.reranker.rerank(query, candidates, top_k)


class ReciprocalRankFusionRetriever:
    def __init__(self, retrievers: Sequence[Any], candidate_k: int, rank_constant: int = 60):
        if len(retrievers) < 2:
            raise ValueError("Fusion requires at least two retrievers")
        self.retrievers = tuple(retrievers)
        self.candidate_k = candidate_k
        self.rank_constant = rank_constant

    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]:
        by_id: dict[str, Chunk] = {}
        scores: dict[str, float] = {}
        first_seen: dict[str, int] = {}
        for retriever_index, retriever in enumerate(self.retrievers):
            for item in retriever.retrieve(query, self.candidate_k):
                by_id[item.chunk_id] = item.chunk
                scores[item.chunk_id] = scores.get(item.chunk_id, 0.0) + 1 / (self.rank_constant + item.rank)
                first_seen.setdefault(item.chunk_id, retriever_index * self.candidate_k + item.rank)
        ids = sorted(scores, key=lambda item: (-round(scores[item], 12), first_seen[item], by_id[item].chunk_index))
        return [
            RetrievedChunk(rank=rank, chunk_id=chunk_id, score=round(scores[chunk_id], 10), chunk=by_id[chunk_id])
            for rank, chunk_id in enumerate(ids[:top_k], start=1)
        ]


@dataclass(frozen=True)
class PipelineConfig:
    schema_version: str
    document_path: Path
    golden_dataset_path: Path
    output_directory: Path
    chunking: ChunkingConfig
    top_k: tuple[int, ...]
    candidate_k: int
    bi_encoders: tuple[dict[str, Any], ...]
    fusions: tuple[dict[str, Any], ...]
    rerankers: tuple[dict[str, Any], ...]

    @classmethod
    def load(cls, path: Path) -> "PipelineConfig":
        value = json.loads(path.read_text(encoding="utf-8"))
        root = find_project_root(path)
        def resolve_model_path(spec: dict[str, Any]) -> dict[str, Any]:
            resolved = dict(spec)
            if "model_path" in resolved:
                candidate = Path(resolved["model_path"])
                if not candidate.is_absolute():
                    resolved["model_path"] = str((root / candidate).resolve())
            return resolved
        config = cls(
            schema_version=str(value["schema_version"]),
            document_path=(root / value["inputs"]["document_path"]).resolve(),
            golden_dataset_path=(root / value["inputs"]["golden_dataset_path"]).resolve(),
            output_directory=(root / value["output_directory"]).resolve(),
            chunking=ChunkingConfig(**value["chunking"]),
            top_k=tuple(int(k) for k in value["evaluation"]["top_k"]),
            candidate_k=int(value["retrieval"]["candidate_k"]),
            bi_encoders=tuple(resolve_model_path(spec) for spec in value["bi_encoders"]),
            fusions=tuple(value.get("fusions", [value["fusion"]] if "fusion" in value else [])),
            rerankers=tuple(resolve_model_path(spec) for spec in value.get("rerankers", [value["reranker"]] if "reranker" in value else [])),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.schema_version != "1.0":
            raise ValueError(f"Unsupported pipeline schema_version: {self.schema_version}")
        self.chunking.validate()
        if not self.bi_encoders:
            raise ValueError("At least one bi-encoder is required")
        ids = [item["id"] for item in self.bi_encoders]
        if len(ids) != len(set(ids)):
            raise ValueError("Bi-encoder IDs must be unique")
        component_ids = ids + [item["id"] for item in self.fusions] + [item["id"] for item in self.rerankers]
        if len(component_ids) != len(set(component_ids)):
            raise ValueError("Encoder, fusion, and reranker IDs must be globally unique")
        if not self.top_k or tuple(sorted(set(self.top_k))) != self.top_k:
            raise ValueError("top_k must be unique and sorted")
        if self.candidate_k < max(self.top_k):
            raise ValueError("candidate_k must be at least max(top_k)")


def run_pipeline(config: PipelineConfig, project_root: Path) -> dict[str, Any]:
    document = json.loads(config.document_path.read_text(encoding="utf-8"))
    questions = read_jsonl(config.golden_dataset_path)
    chunks = TokenChunker(config.chunking, RegexTokenizer()).chunk_document(document)
    retrievers: dict[str, Any] = {}
    encoder_metadata: list[dict[str, Any]] = []
    build_metrics: dict[str, float] = {}
    for spec in config.bi_encoders:
        encoder = build_bi_encoder(spec)
        started = time.perf_counter()
        retriever = ExactVectorIndex(encoder)
        retriever.build_index(chunks)
        build_seconds = time.perf_counter() - started
        retrievers[spec["id"]] = retriever
        encoder_metadata.append(encoder.metadata())
        build_metrics[spec["id"]] = round(build_seconds, 6)

    for fusion in config.fusions:
        if not fusion.get("enabled", True):
            continue
        requested = fusion.get("encoder_ids", list(retrievers))
        retrievers[fusion["id"]] = ReciprocalRankFusionRetriever(
            [retrievers[item] for item in requested], config.candidate_k,
            int(fusion.get("rank_constant", 60)),
        )

    systems: dict[str, Any] = dict(retrievers)
    reranker_metadata: list[dict[str, Any]] = []
    for reranker_spec in config.rerankers:
        reranker = build_reranker(reranker_spec)
        reranker_metadata.append(reranker.metadata())
        for name, retriever in retrievers.items():
            systems[f"{name}+{reranker.model_id}"] = RerankedRetriever(retriever, reranker, config.candidate_k)

    output = config.output_directory
    evaluations: dict[str, Any] = {}
    system_records: dict[str, list[dict[str, Any]]] = {}
    candidate_metrics: dict[str, Any] = {}
    for name, retriever in retrievers.items():
        _, metrics = evaluate_retrieval(retriever, questions, (config.candidate_k,))
        candidate_metrics[name] = {
            "candidate_k": config.candidate_k,
            "recall": metrics["recall_at_k"][str(config.candidate_k)],
            "mean_evidence_coverage": metrics["mean_evidence_coverage"],
            "complete_questions": metrics["passed_at_max_k"],
        }
    for name, retriever in systems.items():
        if isinstance(retriever, RerankedRetriever):
            retriever.prepare([question["question"] for question in questions], max(config.top_k))
        started = time.perf_counter()
        records, metrics = evaluate_retrieval(retriever, questions, config.top_k)
        elapsed = time.perf_counter() - started
        source_system = name.split("+", 1)[0]
        metrics["candidate_generation"] = {
            "source_system": source_system,
            **candidate_metrics[source_system],
        }
        metrics["evaluation_seconds"] = round(elapsed, 6)
        metrics["mean_query_seconds"] = round(elapsed / len(questions), 8)
        evaluations[name] = metrics
        system_records[name] = records
        write_jsonl(output / "systems" / name / "results.jsonl", records)
        write_json(output / "systems" / name / "metrics.json", metrics)

    resolved = {
        "schema_version": "1.0",
        "inputs": {
            "document_path": config.document_path.relative_to(project_root).as_posix(),
            "document_sha256": sha256(config.document_path),
            "golden_dataset_path": config.golden_dataset_path.relative_to(project_root).as_posix(),
            "golden_dataset_sha256": sha256(config.golden_dataset_path),
        },
        "chunking": {
            "strategy": config.chunking.strategy,
            "chunk_size": config.chunking.chunk_size,
            "chunk_overlap": config.chunking.chunk_overlap,
        },
        "retrieval": {"candidate_k": config.candidate_k, "algorithm": "cosine_similarity_exact"},
        "bi_encoders": encoder_metadata,
        "fusions": list(config.fusions),
        "rerankers": reranker_metadata,
        "evaluation": {"top_k": list(config.top_k)},
    }
    run = {
        "schema_version": "1.0",
        "chunk_count": len(chunks),
        "question_count": len(questions),
        "configuration": resolved,
        "build_seconds": build_metrics,
        "candidate_generation": candidate_metrics,
        "systems": evaluations,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
    }
    write_json(output / "run_config.json", resolved)
    write_jsonl(output / "chunks" / "chunks.jsonl", [chunk.to_dict() for chunk in chunks])
    comparison = analyze_model_comparison(system_records, questions, config.top_k)
    write_json(output / "analysis" / "model_category_analysis.json", comparison)
    (output / "analysis" / "model_category_report.md").write_text(
        render_model_comparison_report(comparison), encoding="utf-8", newline="\n"
    )
    write_json(output / "summary.json", run)
    return run


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the complete TESTRX retrieval flow")
    parser.add_argument("--config", type=Path, default=Path("configs/pipelines/baseline.json"))
    args = parser.parse_args()
    config_path = args.config.resolve()
    root = find_project_root(config_path)
    run = run_pipeline(PipelineConfig.load(config_path), root)
    print(f"Completed {len(run['systems'])} retrieval systems over {run['question_count']} questions")
    print(f"Output: {PipelineConfig.load(config_path).output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
