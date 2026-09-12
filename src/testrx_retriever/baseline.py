"""Build and evaluate the deterministic TESTRX retrieval baseline."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform

import numpy as np

from .baseline_config import BaselineConfig, find_project_root
from .analytics import build_retrieval_analysis, render_analysis_report
from .chunking import TokenChunker
from .embedding import StableHashingEmbedder
from .evaluation import evaluate_retrieval, render_retrieval_report
from .tokenization import RegexTokenizer
from .vector_index import ExactVectorIndex


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def write_json(path: Path, value: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_jsonl(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")


def run_baseline(config: BaselineConfig, project_root: Path) -> dict:
    document = json.loads(config.document_path.read_text(encoding="utf-8"))
    questions = read_jsonl(config.golden_dataset_path)
    tokenizer = RegexTokenizer()
    if (tokenizer.name, tokenizer.version) != (config.tokenizer.name, config.tokenizer.version):
        raise ValueError("Configured tokenizer does not match the implemented pinned tokenizer")
    chunks = TokenChunker(config.chunking, tokenizer).chunk_document(document)
    embedder = StableHashingEmbedder(config.embedding)
    index = ExactVectorIndex(embedder)
    index.build_index(chunks)
    records, metrics = evaluate_retrieval(index, questions, config.retrieval.top_k)
    analytics = build_retrieval_analysis(records, config.retrieval.top_k)

    output = config.output_directory
    evaluation_dir = output / "evaluation"
    index_dir = output / "index"
    resolved_config = config.to_dict(project_root)
    run_metadata = {
        "schema_version": "1.0",
        "document_source_sha256": document["source_sha256"],
        "golden_dataset_sha256": sha256(config.golden_dataset_path),
        "chunk_count": len(chunks),
        "configuration": resolved_config,
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
    }
    run = {**run_metadata, "metrics": metrics}

    write_json(output / "run_config.json", run_metadata)
    write_jsonl(output / "chunks" / "chunks.jsonl", [chunk.to_dict() for chunk in chunks])
    index.save_embeddings(index_dir / "embeddings.npy")
    write_json(index_dir / "chunk_ids.json", [chunk.chunk_id for chunk in chunks])
    write_jsonl(evaluation_dir / "retrieval_results.jsonl", records)
    write_json(evaluation_dir / "retrieval_metrics.json", metrics)
    write_json(evaluation_dir / "retrieval_analytics.json", analytics)
    analytics_report = render_analysis_report(analytics, config.retrieval.top_k)
    (evaluation_dir / "retrieval_analytics.md").write_text(
        analytics_report, encoding="utf-8", newline="\n"
    )
    report_path = evaluation_dir / "retrieval_report.md"
    combined_report = render_retrieval_report(run, records) + "\n\n" + analytics_report
    report_path.write_text(combined_report, encoding="utf-8", newline="\n")

    artifact_paths = sorted(
        path for path in output.rglob("*") if path.is_file() and path.name != "manifest.json"
    )
    manifest = {
        "schema_version": "1.0",
        "files": {
            path.relative_to(output).as_posix(): sha256(path)
            for path in artifact_paths
        },
    }
    write_json(output / "manifest.json", manifest)
    return run


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and evaluate the TESTRX retrieval baseline.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/retrieval/reference.json"),
        help="Baseline configuration JSON",
    )
    arguments = parser.parse_args()
    config_path = arguments.config.resolve()
    project_root = find_project_root(config_path)
    run = run_baseline(BaselineConfig.load(config_path), project_root)
    metrics = run["metrics"]
    print("Baseline retrieval evaluation complete\n")
    print(f"Chunks: {run['chunk_count']}")
    print(f"Questions: {metrics['dataset_size']}")
    for k, value in metrics["recall_at_k"].items():
        print(f"Recall@{k}: {value:.3f}")
    print(f"MRR: {metrics['mrr']:.3f}")
    print(f"Mean evidence coverage: {metrics['mean_evidence_coverage']:.3f}")
    print(f"\nOutput: {BaselineConfig.load(config_path).output_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
