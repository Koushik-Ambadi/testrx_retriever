"""Controlled chunk-size and hashing-dimension retrieval experiments."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import platform
import random
from statistics import mean, median
from typing import Any, Iterable

import numpy as np

from .baseline import read_jsonl, sha256, write_json, write_jsonl
from .baseline_config import ChunkingConfig, EmbeddingConfig
from .chunking import Chunk, TokenChunker
from .embedding import StableHashingEmbedder
from .evaluation import evaluate_retrieval
from .tokenization import RegexTokenizer
from .vector_index import ExactVectorIndex


@dataclass(frozen=True)
class SweepConfig:
    schema_version: str
    document_path: Path
    golden_dataset_path: Path
    output_directory: Path
    chunk_sizes: tuple[int, ...]
    overlap_ratio: float
    embedding_dimensions: tuple[int, ...]
    control_chunk_size: int
    control_chunk_overlap: int
    control_embedding_dimension: int
    random_seed: int
    random_trials: int
    retrieval_top_k: tuple[int, ...]

    @classmethod
    def load(cls, path: Path) -> "SweepConfig":
        value = json.loads(path.read_text(encoding="utf-8"))
        root = path.resolve().parent.parent
        control = value["control"]
        random_baseline = value["random_baseline"]
        config = cls(
            schema_version=str(value["schema_version"]),
            document_path=(root / value["document_path"]).resolve(),
            golden_dataset_path=(root / value["golden_dataset_path"]).resolve(),
            output_directory=(root / value["output_directory"]).resolve(),
            chunk_sizes=tuple(int(size) for size in value["chunk_sizes"]),
            overlap_ratio=float(value["overlap_ratio"]),
            embedding_dimensions=tuple(int(size) for size in value["embedding_dimensions"]),
            control_chunk_size=int(control["chunk_size"]),
            control_chunk_overlap=int(control["chunk_overlap"]),
            control_embedding_dimension=int(control["embedding_dimension"]),
            random_seed=int(random_baseline["seed"]),
            random_trials=int(random_baseline["trials"]),
            retrieval_top_k=tuple(int(k) for k in value["retrieval_top_k"]),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if not self.chunk_sizes or any(size <= 0 for size in self.chunk_sizes):
            raise ValueError("chunk_sizes must contain positive integers")
        if tuple(sorted(set(self.chunk_sizes))) != self.chunk_sizes:
            raise ValueError("chunk_sizes must be unique and sorted")
        if not 0 <= self.overlap_ratio < 1:
            raise ValueError("overlap_ratio must be in [0, 1)")
        if not self.embedding_dimensions or any(size <= 0 for size in self.embedding_dimensions):
            raise ValueError("embedding_dimensions must contain positive integers")
        if tuple(sorted(set(self.embedding_dimensions))) != self.embedding_dimensions:
            raise ValueError("embedding_dimensions must be unique and sorted")
        if self.random_trials <= 0:
            raise ValueError("random_trials must be positive")
        if not self.retrieval_top_k or tuple(sorted(set(self.retrieval_top_k))) != self.retrieval_top_k:
            raise ValueError("retrieval_top_k must be unique and sorted")
        ChunkingConfig(chunk_size=self.control_chunk_size, chunk_overlap=self.control_chunk_overlap).validate()
        EmbeddingConfig(dimension=self.control_embedding_dimension).validate()

    def overlap_for(self, chunk_size: int) -> int:
        """Round half up so 10% of 125 becomes the documented 13 tokens."""
        return int(math.floor(chunk_size * self.overlap_ratio + 0.5))

    def to_dict(self, root: Path) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "document_path": self.document_path.relative_to(root).as_posix(),
            "golden_dataset_path": self.golden_dataset_path.relative_to(root).as_posix(),
            "output_directory": self.output_directory.relative_to(root).as_posix(),
            "chunk_sizes": list(self.chunk_sizes),
            "overlap_ratio": self.overlap_ratio,
            "embedding_dimensions": list(self.embedding_dimensions),
            "control": {
                "chunk_size": self.control_chunk_size,
                "chunk_overlap": self.control_chunk_overlap,
                "embedding_dimension": self.control_embedding_dimension,
            },
            "random_baseline": {"seed": self.random_seed, "trials": self.random_trials},
            "retrieval_top_k": list(self.retrieval_top_k),
        }


def _source_ids(chunk: Chunk) -> set[str]:
    return set(chunk.semantic_unit_ids) | set(chunk.source_element_ids)


def _words(text: str) -> set[str]:
    return set(StableHashingEmbedder._words(text))


def _feature_collision_stats(texts: Iterable[str], dimension: int) -> dict[str, Any]:
    features: set[str] = set()
    for text in texts:
        features.update(feature for feature, _ in StableHashingEmbedder._features(StableHashingEmbedder._words(text)))
    buckets = {
        int.from_bytes(hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()[:4], "little") % dimension
        for feature in features
    }
    collisions = len(features) - len(buckets)
    return {
        "distinct_features": len(features),
        "occupied_dimensions": len(buckets),
        "colliding_features": collisions,
        "collision_fraction": round(collisions / len(features), 6) if features else 0.0,
    }


def _random_lineage_recall(
    chunks: list[Chunk], questions: list[dict[str, Any]], top_k_values: tuple[int, ...], seed: int, trials: int
) -> dict[str, float]:
    rng = random.Random(seed)
    chunk_sources = [_source_ids(chunk) for chunk in chunks]
    required_sets = [set(item["retrieval_ground_truth"]["required_source_set"]) for item in questions]
    totals = {k: 0 for k in top_k_values}
    indices = list(range(len(chunks)))
    for _ in range(trials):
        rng.shuffle(indices)
        cumulative: dict[int, set[str]] = {}
        retrieved: set[str] = set()
        next_k = iter(top_k_values)
        target = next(next_k, None)
        for rank, index in enumerate(indices[: max(top_k_values)], start=1):
            retrieved.update(chunk_sources[index])
            if rank == target:
                cumulative[rank] = set(retrieved)
                target = next(next_k, None)
        for required in required_sets:
            for k in top_k_values:
                totals[k] += required <= cumulative.get(k, retrieved)
    denominator = trials * len(questions)
    return {str(k): round(totals[k] / denominator, 6) for k in top_k_values}


def _chunk_diagnostics(chunks: list[Chunk], questions: list[dict[str, Any]]) -> dict[str, Any]:
    source_sets = [_source_ids(chunk) for chunk in chunks]
    relevant_fractions = []
    lexical_coverages = []
    for question in questions:
        required = set(question["retrieval_ground_truth"]["required_source_set"])
        relevant = [chunk for chunk, sources in zip(chunks, source_sets) if required & sources]
        relevant_fractions.append(len(relevant) / len(chunks))
        query_words = _words(question["question"])
        best_coverage = max(
            (len(query_words & _words(chunk.text)) / len(query_words) for chunk in relevant),
            default=0.0,
        ) if query_words else 0.0
        lexical_coverages.append(best_coverage)
    return {
        "mean_tokens_per_chunk": round(mean(chunk.token_count for chunk in chunks), 3),
        "mean_source_elements_per_chunk": round(mean(len(chunk.source_element_ids) for chunk in chunks), 3),
        "mean_semantic_units_per_chunk": round(mean(len(chunk.semantic_unit_ids) for chunk in chunks), 3),
        "mean_relevant_chunk_fraction_per_question": round(mean(relevant_fractions), 6),
        "median_relevant_chunk_fraction_per_question": round(median(relevant_fractions), 6),
        "mean_best_query_word_coverage_in_relevant_chunk": round(mean(lexical_coverages), 6),
    }


def _retrieval_diagnostics(
    index: ExactVectorIndex, questions: list[dict[str, Any]], records: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    margins: list[float] = []
    details: list[dict[str, Any]] = []
    for question, record in zip(questions, records):
        required = set(question["retrieval_ground_truth"]["required_source_set"])
        scores = index.embeddings @ index.embedder.embed_one(question["question"])
        relevant_scores = [float(score) for score, chunk in zip(scores, index.chunks) if required & _source_ids(chunk)]
        irrelevant_scores = [float(score) for score, chunk in zip(scores, index.chunks) if not required & _source_ids(chunk)]
        best_relevant = max(relevant_scores, default=0.0)
        best_irrelevant = max(irrelevant_scores, default=0.0)
        margin = best_relevant - best_irrelevant
        margins.append(margin)
        details.append({
            "question_id": question["question_id"],
            "first_relevant_rank": record["evaluation"]["first_relevant_rank"],
            "reciprocal_rank": record["evaluation"]["reciprocal_rank"],
            "complete_at_k": record["evaluation"]["complete_at_k"],
            "best_relevant_score": round(best_relevant, 10),
            "best_irrelevant_score": round(best_irrelevant, 10),
            "relevant_score_margin": round(margin, 10),
        })
    return {
        "mean_relevant_score_margin": round(mean(margins), 6),
        "positive_relevant_margin_fraction": round(sum(value > 0 for value in margins) / len(margins), 6),
    }, details


def _slice_metrics(records: list[dict[str, Any]], max_k: int) -> dict[str, Any]:
    groups: dict[str, dict[str, list[dict[str, Any]]]] = {
        "difficulty": defaultdict(list),
        "question_type": defaultdict(list),
    }
    for record in records:
        groups["difficulty"][record["difficulty"]].append(record)
        groups["question_type"][record["question_type"]].append(record)
    output: dict[str, Any] = {}
    for group_name, values in groups.items():
        output[group_name] = {}
        for label, group_records in sorted(values.items()):
            output[group_name][label] = {
                "count": len(group_records),
                "recall_at_1": round(mean(item["evaluation"]["complete_at_k"]["1"] for item in group_records), 6),
                "recall_at_max_k": round(mean(item["evaluation"]["complete_at_k"][str(max_k)] for item in group_records), 6),
            }
    return output


def _run_one(
    chunks: list[Chunk], questions: list[dict[str, Any]], dimension: int, top_k: tuple[int, ...]
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    embedder = StableHashingEmbedder(EmbeddingConfig(dimension=dimension))
    index = ExactVectorIndex(embedder)
    index.build_index(chunks)
    records, metrics = evaluate_retrieval(index, questions, top_k)
    retrieval_diagnostics, question_details = _retrieval_diagnostics(index, questions, records)
    metrics["retrieval_diagnostics"] = retrieval_diagnostics
    metrics["slices"] = _slice_metrics(records, max(top_k))
    return metrics, question_details, [record["retrieved_chunk_ids"][0] for record in records]


def _render_report(result: dict[str, Any]) -> str:
    rows = result["runs"]
    ks = result["configuration"]["retrieval_top_k"]
    reference_dimension = result["reference_dimension"]
    lines = [
        "# TESTRX Chunk Size and Embedding Dimension Study", "",
        "## Scope", "",
        "The golden questions, parser output, tokenizer, hashing features, cosine index, and metric definitions are fixed. Only token-window size, approximately 10% overlap, and hashing dimension vary. The 500/50/4096 baseline is repeated as a control.", "",
        "## Results", "",
        f"| Role | Chunk / overlap | Dim | Chunks | " + " | ".join(f"R@{k}" for k in ks) + f" | MRR | Random R@{max(ks)} | Collision | Top-1 vs {reference_dimension} |", 
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        metrics = row["metrics"]
        lines.append(
            f"| {row['role']} | {row['chunk_size']} / {row['chunk_overlap']} | {row['embedding_dimension']} | {row['chunk_count']} | "
            + " | ".join(f"{metrics['recall_at_k'][str(k)]:.3f}" for k in ks)
            + f" | {metrics['mrr']:.3f} | {row['random_lineage_recall_at_k'][str(max(ks))]:.3f} | "
            + f"{row['feature_collisions']['collision_fraction']:.3f} | {row['top1_agreement_with_4096']:.3f} |"
        )
    matrix = [row for row in rows if row["role"] == "sweep"]
    reference_rows = [row for row in matrix if row["embedding_dimension"] == reference_dimension]
    best = max(reference_rows, key=lambda row: (row["metrics"]["mrr"], row["metrics"]["recall_at_k"]["1"]))
    dim_spreads = {}
    for size in sorted({row["chunk_size"] for row in matrix}):
        same_size = [row for row in matrix if row["chunk_size"] == size]
        values = [row["metrics"]["mrr"] for row in same_size]
        dim_spreads[size] = max(values) - min(values)
    control = next(row for row in rows if row["role"] == "control")
    lines.extend([
        "", "## Observations", "",
        f"- At 4,096 dimensions, the strongest MRR among tested smaller windows is {best['metrics']['mrr']:.3f} at {best['chunk_size']}/{best['chunk_overlap']}; its Recall@10 is {best['metrics']['recall_at_k'][str(max(ks))]:.3f}.",
        f"- The 500-token control contains only {control['chunk_count']} chunks, so K=10 searches {10 / control['chunk_count']:.1%} of the entire index. Its measured random-lineage Recall@10 is {control['random_lineage_recall_at_k'][str(max(ks))]:.3f}.",
        f"- Across dimensions, the MRR range by chunk size is " + ", ".join(f"{size}: {spread:.3f}" for size, spread in dim_spreads.items()) + ". Small ranges indicate that feature hashing dimension is not the main source of performance.",
        "- `Random R@10` is a fixed-seed random-ranking lineage baseline. It exposes score inflation caused by a small index and chunks that each own many source IDs.",
        f"- `Collision` is the fraction of distinct corpus-and-query unigram/bigram features sharing an occupied hashing bucket. `Top-1 vs {reference_dimension}` measures ranking stability against the {reference_dimension:,}-dimensional run at the same chunk size.",
        "- The query/evidence lexical and lineage-density diagnostics are recorded in `summary.json`; per-question rank and relevant-versus-irrelevant score margins are in `question_diagnostics.jsonl`.",
        "", "## Interpretation guardrails", "",
        "These results characterize this manual and this frozen seed benchmark. They do not demonstrate semantic generalization. The embedder is lexical, the questions were written from the same source, and source-lineage recall gives a whole chunk credit when any recorded required ID is present.",
        "", "## Reproduction", "", "```powershell", "python -m testrx_retriever.experiments --config configs/retrieval_sweep.json", "```", "",
    ])
    return "\n".join(lines)


def run_sweep(config: SweepConfig, project_root: Path) -> dict[str, Any]:
    document = json.loads(config.document_path.read_text(encoding="utf-8"))
    questions = read_jsonl(config.golden_dataset_path)
    tokenizer = RegexTokenizer()
    run_specs = [
        ("sweep", size, config.overlap_for(size), dimension)
        for size in config.chunk_sizes for dimension in config.embedding_dimensions
    ] + [("control", config.control_chunk_size, config.control_chunk_overlap, config.control_embedding_dimension)]
    chunks_by_window: dict[tuple[int, int], list[Chunk]] = {}
    window_diagnostics: dict[tuple[int, int], dict[str, Any]] = {}
    random_baselines: dict[tuple[int, int], dict[str, float]] = {}
    rows: list[dict[str, Any]] = []
    question_rows: list[dict[str, Any]] = []
    top1_by_spec: dict[tuple[int, int, int], list[str]] = {}

    for role, chunk_size, overlap, dimension in run_specs:
        window = (chunk_size, overlap)
        if window not in chunks_by_window:
            chunks = TokenChunker(ChunkingConfig(chunk_size=chunk_size, chunk_overlap=overlap), tokenizer).chunk_document(document)
            chunks_by_window[window] = chunks
            window_diagnostics[window] = _chunk_diagnostics(chunks, questions)
            random_baselines[window] = _random_lineage_recall(
                chunks, questions, config.retrieval_top_k, config.random_seed + chunk_size, config.random_trials
            )
        chunks = chunks_by_window[window]
        metrics, details, top1 = _run_one(chunks, questions, dimension, config.retrieval_top_k)
        features = _feature_collision_stats(
            [chunk.text for chunk in chunks] + [question["question"] for question in questions], dimension
        )
        spec = (chunk_size, overlap, dimension)
        top1_by_spec[spec] = top1
        row = {
            "role": role,
            "chunk_size": chunk_size,
            "chunk_overlap": overlap,
            "embedding_dimension": dimension,
            "chunk_count": len(chunks),
            "index_fraction_at_max_k": round(min(max(config.retrieval_top_k), len(chunks)) / len(chunks), 6),
            "chunk_diagnostics": window_diagnostics[window],
            "feature_collisions": features,
            "random_lineage_recall_at_k": random_baselines[window],
            "metrics": metrics,
        }
        rows.append(row)
        for detail in details:
            question_rows.append({
                "role": role,
                "chunk_size": chunk_size,
                "chunk_overlap": overlap,
                "embedding_dimension": dimension,
                **detail,
            })

    reference_dimension = max(config.embedding_dimensions)
    for row in rows:
        reference_key = (row["chunk_size"], row["chunk_overlap"], reference_dimension)
        reference = top1_by_spec.get(reference_key, top1_by_spec[(row["chunk_size"], row["chunk_overlap"], row["embedding_dimension"])])
        current = top1_by_spec[(row["chunk_size"], row["chunk_overlap"], row["embedding_dimension"])]
        row["top1_agreement_with_4096"] = round(sum(a == b for a, b in zip(current, reference)) / len(reference), 6)

    result = {
        "schema_version": "1.0",
        "configuration": config.to_dict(project_root),
        "source_identity": {
            "document_source_sha256": document["source_sha256"],
            "canonical_document_sha256": sha256(config.document_path),
            "golden_dataset_sha256": sha256(config.golden_dataset_path),
        },
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
        "reference_dimension": reference_dimension,
        "runs": rows,
    }
    output = config.output_directory
    write_json(output / "summary.json", result)
    write_jsonl(output / "question_diagnostics.jsonl", question_rows)
    (output / "report.md").parent.mkdir(parents=True, exist_ok=True)
    (output / "report.md").write_text(_render_report(result), encoding="utf-8", newline="\n")
    manifest_paths = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "manifest.json")
    write_json(output / "manifest.json", {
        "schema_version": "1.0",
        "files": {path.relative_to(output).as_posix(): sha256(path) for path in manifest_paths},
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the TESTRX chunk-size and embedding-dimension study.")
    parser.add_argument("--config", type=Path, default=Path("configs/retrieval_sweep.json"))
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = SweepConfig.load(config_path)
    result = run_sweep(config, config_path.parent.parent)
    print(f"Completed {len(result['runs'])} controlled retrieval runs")
    print(f"Output: {config.output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
