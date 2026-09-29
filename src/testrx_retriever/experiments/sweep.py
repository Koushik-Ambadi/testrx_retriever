"""Controlled chunk-size and hashing-dimension retrieval experiments."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import random
import subprocess
from statistics import mean, median
from typing import Any, Iterable

import numpy as np

from ..common.files import read_jsonl, sha256, write_json, write_jsonl
from ..configuration import ChunkingConfig, EmbeddingConfig, find_project_root
from ..retrieval.chunking import Chunk, TokenChunker
from ..retrieval.encoders.lexical_hashing import StableHashingEmbedder
from ..evaluation import evaluate_retrieval
from ..retrieval.tokenization import RegexTokenizer
from ..retrieval.indexes import ExactVectorIndex


@dataclass(frozen=True)
class SweepConfig:
    schema_version: str
    experiment_id: str
    title: str
    hypothesis: str
    document_path: Path
    golden_dataset_path: Path
    output_directory: Path
    retention: dict[str, bool]
    chunkers: tuple[dict[str, Any], ...]
    embedders: tuple[dict[str, Any], ...]
    retrievers: tuple[dict[str, Any], ...]
    rerankers: tuple[dict[str, Any], ...]
    controls: tuple[dict[str, Any], ...]
    random_seed: int
    random_trials: int
    retrieval_top_k: tuple[int, ...]
    question_filter: dict[str, Any]

    @classmethod
    def load(cls, path: Path) -> "SweepConfig":
        value = json.loads(path.read_text(encoding="utf-8"))
        root = find_project_root(path)
        inputs = value["inputs"]
        components = value["components"]
        evaluation = value["evaluation"]
        random_baseline = evaluation["random_baseline"]
        config = cls(
            schema_version=str(value["schema_version"]),
            experiment_id=str(value["experiment_id"]),
            title=str(value["title"]),
            hypothesis=str(value["hypothesis"]),
            document_path=(root / inputs["document_path"]).resolve(),
            golden_dataset_path=(root / inputs["golden_dataset_path"]).resolve(),
            output_directory=(root / value["output_store"]).resolve(),
            retention={key: bool(item) for key, item in value["retention"].items()},
            chunkers=tuple(components["chunkers"]),
            embedders=tuple(components["embedders"]),
            retrievers=tuple(components["retrievers"]),
            rerankers=tuple(components["rerankers"]),
            controls=tuple(value.get("controls", [])),
            random_seed=int(random_baseline["seed"]),
            random_trials=int(random_baseline["trials"]),
            retrieval_top_k=tuple(int(k) for k in evaluation["top_k"]),
            question_filter=dict(evaluation.get("question_filter", {})),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if not self.experiment_id or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in self.experiment_id):
            raise ValueError("experiment_id must use lowercase letters, digits, hyphens, or underscores")
        required_retention = {"run_metrics", "question_metrics", "chunks", "embeddings", "ranked_results"}
        if set(self.retention) != required_retention:
            raise ValueError(f"retention must define exactly {sorted(required_retention)}")
        if not self.retention["run_metrics"]:
            raise ValueError("run_metrics retention is required")
        if self.retention["chunks"] or self.retention["embeddings"] or self.retention["ranked_results"]:
            raise ValueError("full artifacts belong in output/retrieval/reference, not the compact experiment store")
        if not self.chunkers or not self.embedders or not self.retrievers or not self.rerankers:
            raise ValueError("every component grid must contain at least one variant")
        for chunker in self.chunkers:
            if chunker["strategy"] != "token_window":
                raise ValueError(f"Unsupported chunker: {chunker['strategy']}")
            parameters = chunker["parameters"]
            sizes = tuple(int(size) for size in parameters["chunk_sizes"])
            if not sizes or any(size <= 0 for size in sizes) or tuple(sorted(set(sizes))) != sizes:
                raise ValueError("chunk_sizes must contain unique sorted positive integers")
            overlap = parameters["overlap"]
            if overlap != {"mode": "ratio", "value": overlap["value"], "rounding": "half_up"}:
                raise ValueError("only ratio overlap with half_up rounding is currently supported")
            if not 0 <= float(overlap["value"]) < 1:
                raise ValueError("overlap ratio must be in [0, 1)")
        for embedder in self.embedders:
            if (embedder["model"], embedder["model_version"]) != ("stable_hashing_word_bigram", "1.0"):
                raise ValueError(f"Unsupported embedder: {embedder['model']} {embedder['model_version']}")
            dimensions = tuple(int(size) for size in embedder["parameters"]["dimensions"])
            if not dimensions or any(size <= 0 for size in dimensions) or tuple(sorted(set(dimensions))) != dimensions:
                raise ValueError("dimensions must contain unique sorted positive integers")
        if any(item["algorithm"] != "cosine_similarity_exact" for item in self.retrievers):
            raise ValueError("only cosine_similarity_exact retrieval is currently implemented")
        if any(item["algorithm"] != "none" for item in self.rerankers):
            raise ValueError("configured reranker is not implemented")
        if self.random_trials <= 0:
            raise ValueError("random_trials must be positive")
        if not self.retrieval_top_k or tuple(sorted(set(self.retrieval_top_k))) != self.retrieval_top_k:
            raise ValueError("retrieval_top_k must be unique and sorted")
        unsupported_filters = set(self.question_filter) - {"paraphrase_levels"}
        if unsupported_filters:
            raise ValueError(f"unsupported question filters: {sorted(unsupported_filters)}")
        levels = self.question_filter.get("paraphrase_levels", [])
        if levels and (not isinstance(levels, list) or any(not isinstance(level, str) for level in levels)):
            raise ValueError("question_filter.paraphrase_levels must be a list of strings")
        for control in self.controls:
            ChunkingConfig(
                strategy=control["chunking"]["strategy"],
                chunk_size=int(control["chunking"]["chunk_size"]),
                chunk_overlap=int(control["chunking"]["chunk_overlap"]),
            ).validate()
            EmbeddingConfig(
                model=control["embedding"]["model"],
                model_version=control["embedding"]["model_version"],
                dimension=int(control["embedding"]["dimension"]),
            ).validate()
            if control["retrieval"]["algorithm"] != "cosine_similarity_exact" or control["reranking"]["algorithm"] != "none":
                raise ValueError("unsupported control retrieval or reranking component")

    @staticmethod
    def overlap_for(chunker: dict[str, Any], chunk_size: int) -> int:
        """Round half up so a 10% ratio at 125 becomes 13 tokens."""
        return int(math.floor(chunk_size * float(chunker["parameters"]["overlap"]["value"]) + 0.5))

    def run_specs(self) -> list[dict[str, Any]]:
        specs: list[dict[str, Any]] = []
        for chunker, embedder, retriever, reranker in itertools.product(
            self.chunkers, self.embedders, self.retrievers, self.rerankers
        ):
            for size, dimension in itertools.product(
                chunker["parameters"]["chunk_sizes"], embedder["parameters"]["dimensions"]
            ):
                specs.append({
                    "role": "sweep",
                    "label": None,
                    "chunking": {
                        "strategy": chunker["strategy"],
                        "chunk_size": int(size),
                        "chunk_overlap": self.overlap_for(chunker, int(size)),
                    },
                    "embedding": {
                        "family": embedder.get("family", "unspecified"),
                        "model": embedder["model"],
                        "model_version": embedder["model_version"],
                        "dimension": int(dimension),
                    },
                    "retrieval": retriever,
                    "reranking": reranker,
                })
        specs.extend({"role": "control", **control} for control in self.controls)
        return specs

    def to_dict(self, root: Path) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "experiment_id": self.experiment_id,
            "title": self.title,
            "hypothesis": self.hypothesis,
            "inputs": {
                "document_path": self.document_path.relative_to(root).as_posix(),
                "golden_dataset_path": self.golden_dataset_path.relative_to(root).as_posix(),
            },
            "output_store": self.output_directory.relative_to(root).as_posix(),
            "retention": self.retention,
            "evaluation": {
                "top_k": list(self.retrieval_top_k),
                "random_baseline": {"seed": self.random_seed, "trials": self.random_trials},
                "question_filter": self.question_filter,
            },
            "components": {
                "chunkers": list(self.chunkers),
                "embedders": list(self.embedders),
                "retrievers": list(self.retrievers),
                "rerankers": list(self.rerankers),
            },
            "controls": list(self.controls),
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
            "source_question_id": question.get("source_question_id"),
            "paraphrase_level": question.get("paraphrase_level", "original"),
            "question_type": question["question_type"],
            "difficulty": question["difficulty"],
            "required_source_ids": sorted(required),
            "source_pages": question.get("source", {}).get("pages", []),
            "source_section_paths": question.get("source", {}).get("section_paths", []),
            "source_semantic_unit_ids": question.get("source", {}).get("semantic_unit_ids", []),
            "categories": sorted(
                key.removeprefix("requires_")
                for key, enabled in question.get("evaluation_metadata", {}).items()
                if key.startswith("requires_") and enabled
            ),
            "lexical_diagnostics": question.get("lexical_diagnostics", {}),
            "first_relevant_rank": record["evaluation"]["first_relevant_rank"],
            "reciprocal_rank": record["evaluation"]["reciprocal_rank"],
            "precision_at_k": record["evaluation"]["precision_at_k"],
            "coverage_at_k": record["evaluation"]["coverage_at_k"],
            "complete_at_k": record["evaluation"]["complete_at_k"],
            "failure_category": record["evaluation"]["failure_category"],
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
    chunks: list[Chunk], questions: list[dict[str, Any]], embedding: dict[str, Any], top_k: tuple[int, ...]
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    embedder = StableHashingEmbedder(EmbeddingConfig(
        model=embedding["model"],
        model_version=embedding["model_version"],
        dimension=int(embedding["dimension"]),
    ))
    index = ExactVectorIndex(embedder)
    index.build_index(chunks)
    records, metrics = evaluate_retrieval(index, questions, top_k)
    retrieval_diagnostics, question_details = _retrieval_diagnostics(index, questions, records)
    metrics["retrieval_diagnostics"] = retrieval_diagnostics
    metrics["slices"] = _slice_metrics(records, max(top_k))
    return metrics, question_details, [record["retrieved_chunk_ids"][0] for record in records]


def _experiment_observations(rows: list[dict[str, Any]], top_k: tuple[int, ...]) -> list[dict[str, Any]]:
    sweep = [row for row in rows if row["role"] == "sweep"]
    controls = [row for row in rows if row["role"] == "control"]
    observations: list[dict[str, Any]] = []
    if sweep:
        best = max(sweep, key=lambda row: (row["metrics"]["mrr"], row["metrics"]["recall_at_k"]["1"]))
        observations.append({
            "finding": "best_measured_sweep_run",
            "run_id": best["run_id"],
            "mrr": best["metrics"]["mrr"],
            "recall_at_max_k": best["metrics"]["recall_at_k"][str(max(top_k))],
        })
    for control in controls:
        observations.append({
            "finding": "fixed_k_index_exposure",
            "run_id": control["run_id"],
            "index_fraction_at_max_k": control["index_fraction_at_max_k"],
            "random_lineage_recall_at_max_k": control["random_lineage_recall_at_k"][str(max(top_k))],
        })
    observations.append({
        "finding": "interpretation_boundary",
        "note": "Results measure same-document lexical retrieval with lineage relevance; they do not establish semantic generalization.",
    })
    return observations


def _upsert_records(path: Path, experiment_id: str, records: list[dict[str, Any]]) -> None:
    existing = read_jsonl(path) if path.exists() else []
    retained = [record for record in existing if record.get("experiment_id") != experiment_id]
    combined = retained + records
    combined.sort(key=lambda record: (record.get("experiment_id", ""), record.get("run_id", ""), record.get("question_id", "")))
    write_jsonl(path, combined)


def _code_revision(project_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=project_root, check=True,
            capture_output=True, text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def run_sweep(config: SweepConfig, project_root: Path) -> dict[str, Any]:
    code_revision = _code_revision(project_root)
    document = json.loads(config.document_path.read_text(encoding="utf-8"))
    questions = read_jsonl(config.golden_dataset_path)
    selected_levels = set(config.question_filter.get("paraphrase_levels", []))
    if selected_levels:
        questions = [question for question in questions if question.get("paraphrase_level", "original") in selected_levels]
    if not questions:
        raise ValueError("question filter selected no evaluation questions")
    tokenizer = RegexTokenizer()
    run_specs = config.run_specs()
    source_identity = {
        "document_source_sha256": document["source_sha256"],
        "canonical_document_sha256": sha256(config.document_path),
        "golden_dataset_sha256": sha256(config.golden_dataset_path),
    }
    chunks_by_window: dict[tuple[str, int, int], list[Chunk]] = {}
    window_diagnostics: dict[tuple[str, int, int], dict[str, Any]] = {}
    random_baselines: dict[tuple[str, int, int], dict[str, float]] = {}
    rows: list[dict[str, Any]] = []
    question_rows: list[dict[str, Any]] = []
    top1_by_spec: dict[tuple[str, int, int, str, str, str, str, int], list[str]] = {}

    for spec in run_specs:
        chunking = spec["chunking"]
        embedding = spec["embedding"]
        chunk_size = int(chunking["chunk_size"])
        overlap = int(chunking["chunk_overlap"])
        dimension = int(embedding["dimension"])
        window = (chunking["strategy"], chunk_size, overlap)
        if window not in chunks_by_window:
            chunks = TokenChunker(ChunkingConfig(**chunking), tokenizer).chunk_document(document)
            chunks_by_window[window] = chunks
            window_diagnostics[window] = _chunk_diagnostics(chunks, questions)
            random_baselines[window] = _random_lineage_recall(
                chunks, questions, config.retrieval_top_k, config.random_seed + chunk_size, config.random_trials
            )
        chunks = chunks_by_window[window]
        metrics, details, top1 = _run_one(chunks, questions, embedding, config.retrieval_top_k)
        features = _feature_collision_stats(
            [chunk.text for chunk in chunks] + [question["question"] for question in questions], dimension
        )
        components = {
            "chunking": chunking,
            "embedding": embedding,
            "retrieval": spec["retrieval"],
            "reranking": spec["reranking"],
        }
        run_identity = {
            "experiment_id": config.experiment_id,
            "source_identity": source_identity,
            "components": components,
            "evaluation": {
                "top_k": list(config.retrieval_top_k),
                "random_seed": config.random_seed,
                "random_trials": config.random_trials,
                "question_filter": config.question_filter,
            },
        }
        run_digest = hashlib.sha256(
            json.dumps(run_identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()[:16]
        run_id = f"RUN-{run_digest}"
        ranking_key = (
            chunking["strategy"], chunk_size, overlap,
            embedding["model"], embedding["model_version"],
            json.dumps(spec["retrieval"], sort_keys=True, separators=(",", ":")),
            json.dumps(spec["reranking"], sort_keys=True, separators=(",", ":")),
            dimension,
        )
        top1_by_spec[ranking_key] = top1
        row = {
            "schema_version": "1.1",
            "experiment_id": config.experiment_id,
            "run_id": run_id,
            "code_revision": code_revision,
            "role": spec["role"],
            "label": spec.get("label"),
            "components": components,
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
                "schema_version": "1.0",
                "experiment_id": config.experiment_id,
                "run_id": run_id,
                **detail,
            })

    ranking_families = {
        (
            spec["chunking"]["strategy"], int(spec["chunking"]["chunk_size"]), int(spec["chunking"]["chunk_overlap"]),
            spec["embedding"]["model"], spec["embedding"]["model_version"],
            json.dumps(spec["retrieval"], sort_keys=True, separators=(",", ":")),
            json.dumps(spec["reranking"], sort_keys=True, separators=(",", ":")),
        )
        for spec in run_specs if spec["role"] == "sweep"
    }
    reference_dimensions = {
        family: max(
            int(spec["embedding"]["dimension"])
            for spec in run_specs
            if spec["role"] == "sweep"
            and (
                spec["chunking"]["strategy"], int(spec["chunking"]["chunk_size"]), int(spec["chunking"]["chunk_overlap"]),
                spec["embedding"]["model"], spec["embedding"]["model_version"],
                json.dumps(spec["retrieval"], sort_keys=True, separators=(",", ":")),
                json.dumps(spec["reranking"], sort_keys=True, separators=(",", ":")),
            ) == family
        )
        for family in ranking_families
    }
    for row in rows:
        chunking = row["components"]["chunking"]
        embedding = row["components"]["embedding"]
        family = (
            chunking["strategy"], row["chunk_size"], row["chunk_overlap"],
            embedding["model"], embedding["model_version"],
            json.dumps(row["components"]["retrieval"], sort_keys=True, separators=(",", ":")),
            json.dumps(row["components"]["reranking"], sort_keys=True, separators=(",", ":")),
        )
        if family not in reference_dimensions:
            row["top1_agreement_with_reference"] = None
            continue
        reference_key = (
            *family, reference_dimensions[family],
        )
        if reference_key not in top1_by_spec:
            row["top1_agreement_with_reference"] = None
            continue
        reference = top1_by_spec[reference_key]
        current_key = (
            *family, row["embedding_dimension"],
        )
        current = top1_by_spec[current_key]
        row["top1_agreement_with_reference"] = round(sum(a == b for a, b in zip(current, reference)) / len(reference), 6)

    result = {
        "schema_version": "2.1",
        "experiment_id": config.experiment_id,
        "code_revision": code_revision,
        "title": config.title,
        "hypothesis": config.hypothesis,
        "configuration": config.to_dict(project_root),
        "source_identity": source_identity,
        "runtime": {"python": platform.python_version(), "numpy": np.__version__},
        "observations": _experiment_observations(rows, config.retrieval_top_k),
        "runs": rows,
    }
    output = config.output_directory
    experiment_record = {key: value for key, value in result.items() if key != "runs"}
    _upsert_records(output / "experiments.jsonl", config.experiment_id, [experiment_record])
    _upsert_records(output / "runs.jsonl", config.experiment_id, rows)
    if config.retention["question_metrics"]:
        _upsert_records(output / "question_metrics.jsonl", config.experiment_id, question_rows)
    else:
        _upsert_records(output / "question_metrics.jsonl", config.experiment_id, [])
    manifest_paths = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "manifest.json")
    write_json(output / "manifest.json", {
        "schema_version": "1.0",
        "files": {path.relative_to(output).as_posix(): sha256(path) for path in manifest_paths},
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the TESTRX chunk-size and embedding-dimension study.")
    parser.add_argument(
        "--config", type=Path,
        default=Path("studies/retrieval/chunk-dimension-sweep/experiment.json"),
    )
    args = parser.parse_args()
    config_path = args.config.resolve()
    config = SweepConfig.load(config_path)
    result = run_sweep(config, find_project_root(config_path))
    print(f"Completed {len(result['runs'])} controlled retrieval runs")
    print(f"Output: {config.output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
