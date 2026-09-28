"""Run a reusable hierarchy-chunking matrix through the existing retrieval pipeline."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
from typing import Any

from ..configuration import ChunkingConfig, find_project_root
from ..common.files import sha256, write_json
from .model_comparison import PipelineConfig, run_pipeline


def run_hierarchy_experiment(config_path: Path) -> dict[str, Any]:
    value = json.loads(config_path.read_text(encoding="utf-8"))
    if str(value["schema_version"]) != "1.0":
        raise ValueError(f"Unsupported hierarchy experiment schema: {value['schema_version']}")
    project_root = find_project_root(config_path)
    base_path = (project_root / value["base_pipeline_config"]).resolve()
    base = PipelineConfig.load(base_path)
    output = (project_root / value["output_directory"]).resolve()
    variants = value["chunking_variants"]
    ids = [str(item["id"]) for item in variants]
    if not variants or len(ids) != len(set(ids)):
        raise ValueError("chunking_variants must have unique IDs")

    completed: list[dict[str, Any]] = []
    for variant in variants:
        variant_id = str(variant["id"])
        chunking = ChunkingConfig(**variant["chunking"])
        chunking.validate()
        run_config = replace(
            base, output_directory=output / variant_id, chunking=chunking,
            latency=dict(value.get("latency", {"enabled": False})),
        )
        run = run_pipeline(run_config, project_root)
        completed.append({
            "id": variant_id,
            "chunking": variant["chunking"],
            "output_directory": (output / variant_id).relative_to(project_root).as_posix(),
            "chunk_count": run["chunk_count"],
            "question_count": run["question_count"],
        })

    manifest = {
        "schema_version": "1.0",
        "experiment_id": value["experiment_id"],
        "base_pipeline_config": base_path.relative_to(project_root).as_posix(),
        "base_pipeline_config_sha256": sha256(base_path),
        "source_document_sha256": sha256(base.document_path),
        "golden_dataset_sha256": sha256(base.golden_dataset_path),
        "timing_contract": {
            "clock": "time.perf_counter_ns",
            "excludes": ["chunking", "index_build", "model_load"],
            "includes": ["query_encoding", "candidate_ranking", "top_k_selection", "reranking_when_enabled"],
            "cache_policy": "model_loaded; cross-encoder query/chunk score cache cleared per system",
            "sampling": value.get("latency", {"enabled": False}),
        },
        "variants": completed,
    }
    write_json(output / "experiment_manifest.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run TESTRX hierarchy chunking experiments")
    parser.add_argument(
        "--config", type=Path,
        default=Path("configs/pipelines/hierarchical_chunking_experiment.json"),
    )
    args = parser.parse_args()
    manifest = run_hierarchy_experiment(args.config.resolve())
    print(f"Completed {len(manifest['variants'])} hierarchy chunking variants")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
