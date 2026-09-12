"""Reusable retrieval analytics for full results and compact shared stores."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import itertools
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


RUN_DIMENSIONS = {
    "experiment_id": lambda run, _: run["experiment_id"],
    "run_id": lambda run, _: run["run_id"],
    "run_role": lambda run, _: run["role"],
    "chunking_strategy": lambda run, _: run["components"]["chunking"]["strategy"],
    "token_size": lambda run, _: run["components"]["chunking"]["chunk_size"],
    "token_overlap": lambda run, _: run["components"]["chunking"]["chunk_overlap"],
    "embedding_family": lambda run, _: run["components"]["embedding"].get("family", "unspecified"),
    "embedding_model": lambda run, _: run["components"]["embedding"]["model"],
    "embedding_dimension": lambda run, _: run["components"]["embedding"]["dimension"],
    "retrieval_algorithm": lambda run, _: run["components"]["retrieval"]["algorithm"],
    "reranking_algorithm": lambda run, _: run["components"]["reranking"]["algorithm"],
}
QUESTION_DIMENSIONS = {
    "difficulty": lambda _, question: question["difficulty"],
    "question_type": lambda _, question: question["question_type"],
    "paraphrase_level": lambda _, question: question.get("paraphrase_level", "original"),
    "category": lambda _, question: question.get("categories", []),
    "source_semantic_id": lambda _, question: question.get("source_semantic_unit_ids", []),
    "source_question_id": lambda _, question: question.get("source_question_id") or question["question_id"],
}
AVAILABLE_DIMENSIONS = {**RUN_DIMENSIONS, **QUESTION_DIMENSIONS}


def summarize_evaluations(records: list[dict[str, Any]], top_k_values: tuple[int, ...]) -> dict[str, Any]:
    if not records:
        raise ValueError("Cannot summarize an empty record group")
    max_k = max(top_k_values)
    coverage = [record["evaluation"]["coverage_at_k"][str(max_k)] for record in records]
    failed = [not record["evaluation"]["complete_at_k"][str(max_k)] for record in records]
    failure_categories = Counter(
        record["evaluation"].get("failure_category") or record.get("failure_category")
        for record, is_failed in zip(records, failed) if is_failed
    )
    overlaps = [
        record.get("lexical_diagnostics", {}).get("query_source_lexical_overlap")
        for record in records
    ]
    overlaps = [value for value in overlaps if value is not None]
    return {
        "question_count": len(records),
        "maximum_k": max_k,
        "failed_at_max_k": sum(failed),
        "failure_rate_at_max_k": round(sum(failed) / len(records), 6),
        "failure_categories": dict(sorted((key or "unspecified", value) for key, value in failure_categories.items())),
        "mean_lexical_overlap": round(mean(overlaps), 6) if overlaps else None,
        "recall_at_k": {
            str(k): round(mean(record["evaluation"]["complete_at_k"][str(k)] for record in records), 6)
            for k in top_k_values
        },
        "precision_at_k": {
            str(k): round(mean(record["evaluation"]["precision_at_k"][str(k)] for record in records), 6)
            for k in top_k_values
        },
        "mrr": round(mean(record["evaluation"]["reciprocal_rank"] for record in records), 6),
        "mean_evidence_coverage": round(mean(coverage), 6),
        "evidence_coverage_distribution": {
            "zero": round(sum(value == 0 for value in coverage) / len(coverage), 6),
            "partial": round(sum(0 < value < 1 for value in coverage) / len(coverage), 6),
            "complete": round(sum(value == 1 for value in coverage) / len(coverage), 6),
        },
    }


def _group_full_records(
    records: list[dict[str, Any]], dimensions: tuple[str, ...]
) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        values: list[list[Any]] = []
        for dimension in dimensions:
            if dimension == "category":
                categories = [
                    key.removeprefix("requires_")
                    for key, enabled in record.get("evaluation_metadata", {}).items()
                    if key.startswith("requires_") and enabled
                ]
                values.append(categories or ["none"])
            elif dimension == "source_semantic_id":
                values.append(record.get("source", {}).get("semantic_unit_ids", []) or ["none"])
            elif dimension == "source_question_id":
                values.append([record.get("source_question_id") or record["question_id"]])
            else:
                values.append([record.get(dimension, "unspecified")])
        for key in itertools.product(*values):
            grouped[key].append(record)
    return grouped


def _pearson(pairs: Iterable[tuple[float, float]]) -> float | None:
    values = list(pairs)
    if len(values) < 2:
        return None
    xs, ys = zip(*values)
    x_mean, y_mean = mean(xs), mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in values)
    denominator = math.sqrt(sum((x - x_mean) ** 2 for x in xs) * sum((y - y_mean) ** 2 for y in ys))
    return round(numerator / denominator, 6) if denominator else None


def build_retrieval_analysis(
    records: list[dict[str, Any]], top_k_values: tuple[int, ...]
) -> dict[str, Any]:
    selected_families = {
        record.get("source_question_id") or record["question_id"]
        for record in records if record.get("source_question_id")
    }
    paired = [
        record for record in records
        if (record.get("source_question_id") or record["question_id"]) in selected_families
    ]
    dimensions = {
        "by_paraphrase_level": ("paraphrase_level",),
        "by_difficulty_and_paraphrase_level": ("difficulty", "paraphrase_level"),
        "by_question_type_and_paraphrase_level": ("question_type", "paraphrase_level"),
        "by_category_and_paraphrase_level": ("category", "paraphrase_level"),
        "by_source_semantic_id": ("source_semantic_id",),
        "by_family_and_paraphrase_level": ("source_question_id", "paraphrase_level"),
    }
    output: dict[str, Any] = {"overall": summarize_evaluations(records, top_k_values)}
    for name, group_dimensions in dimensions.items():
        source = paired if name == "by_family_and_paraphrase_level" else records
        grouped = _group_full_records(source, group_dimensions)
        output[name] = [
            {
                "group": dict(zip(group_dimensions, key)),
                **summarize_evaluations(items, top_k_values),
            }
            for key, items in sorted(grouped.items(), key=lambda item: tuple(str(value) for value in item[0]))
        ]
    output["paired_family_question_count"] = len(paired)
    output["lexical_overlap_mrr_pearson"] = _pearson(
        (
            record["lexical_diagnostics"]["query_source_lexical_overlap"],
            record["evaluation"]["reciprocal_rank"],
        )
        for record in paired
    )
    return output


def render_analysis_report(analysis: dict[str, Any], top_k_values: tuple[int, ...]) -> str:
    lines = [
        "# Retrieval Analytics", "", "## Paraphrase-level summary", "",
        "| Level | N | Lexical overlap | R@1 | R@3 | R@5 | R@10 | MRR | Coverage | P@1 | P@3 | P@5 | P@10 | Zero | Partial | Complete |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in analysis["by_paraphrase_level"]:
        summary = row
        distribution = summary["evidence_coverage_distribution"]
        overlap = summary["mean_lexical_overlap"]
        overlap_text = "n/a" if overlap is None else f"{overlap:.3f}"
        lines.append(
            f"| {row['group']['paraphrase_level']} | {summary['question_count']} | {overlap_text} | "
            + " | ".join(f"{summary['recall_at_k'][str(k)]:.3f}" for k in top_k_values)
            + f" | {summary['mrr']:.3f} | {summary['mean_evidence_coverage']:.3f} | "
            + " | ".join(f"{summary['precision_at_k'][str(k)]:.3f}" for k in top_k_values)
            + f" | {distribution['zero']:.3f} | {distribution['partial']:.3f} | {distribution['complete']:.3f} |"
        )
    lines.extend([
        "", "## Primary diagnostic", "",
        f"- Paired family questions: {analysis['paired_family_question_count']}",
        f"- Pearson correlation, lexical overlap versus reciprocal rank: {analysis['lexical_overlap_mrr_pearson']}",
        "", "## Additional slices", "",
        "Machine-readable analytics include difficulty × paraphrase level, question type × paraphrase level, category × paraphrase level, source semantic ID, and source-question family × paraphrase level.",
        "", "Precision treats a retrieved chunk as relevant when its semantic-unit or source-element lineage intersects the question's acceptable source set. Recall, evidence coverage, and MRR continue to use the required source set. Required-evidence text is retained for audit but is not used as a strategy-specific text-match shortcut.", "",
    ])
    return "\n".join(lines)


def _compact_as_full(question: dict[str, Any]) -> dict[str, Any]:
    return {
        **question,
        "lexical_diagnostics": question.get("lexical_diagnostics", {}),
        "evaluation": {
            "coverage_at_k": question["coverage_at_k"],
            "complete_at_k": question["complete_at_k"],
            "precision_at_k": question["precision_at_k"],
            "reciprocal_rank": question["reciprocal_rank"],
            "failure_category": question.get("failure_category"),
        },
    }


def analyze_shared_store(
    store: Path, dimensions: tuple[str, ...], filters: dict[str, str] | None = None
) -> list[dict[str, Any]]:
    invalid = [dimension for dimension in dimensions if dimension not in AVAILABLE_DIMENSIONS]
    if invalid:
        raise ValueError(f"Unknown dimensions {invalid}; choose from {sorted(AVAILABLE_DIMENSIONS)}")
    runs = {record["run_id"]: record for record in _read_jsonl(store / "runs.jsonl")}
    questions = _read_jsonl(store / "question_metrics.jsonl")
    filters = filters or {}
    invalid_filters = [dimension for dimension in filters if dimension not in AVAILABLE_DIMENSIONS]
    if invalid_filters:
        raise ValueError(f"Unknown filter dimensions {invalid_filters}; choose from {sorted(AVAILABLE_DIMENSIONS)}")
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for question in questions:
        run = runs[question["run_id"]]
        if any(
            str(expected) not in [str(item) for item in (value if isinstance(value, list) else [value])]
            for dimension, expected in filters.items()
            for value in [AVAILABLE_DIMENSIONS[dimension](run, question)]
        ):
            continue
        values: list[list[Any]] = []
        for dimension in dimensions:
            value = AVAILABLE_DIMENSIONS[dimension](run, question)
            values.append(value if isinstance(value, list) else [value])
        for key in itertools.product(*values):
            grouped[key].append(_compact_as_full(question))
    rows = []
    for key, items in sorted(grouped.items(), key=lambda item: tuple(str(value) for value in item[0])):
        top_k = tuple(sorted(int(k) for k in items[0]["evaluation"]["complete_at_k"]))
        rows.append({"group": dict(zip(dimensions, key)), **summarize_evaluations(items, top_k)})
    return rows


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze the shared retrieval experiment store.")
    parser.add_argument("--store", type=Path, default=Path("output/retrieval/experiments"))
    parser.add_argument(
        "--group-by", default="experiment_id,run_id",
        help=f"Comma-separated dimensions: {', '.join(sorted(AVAILABLE_DIMENSIONS))}",
    )
    parser.add_argument("--format", choices=("json", "table"), default="table")
    parser.add_argument(
        "--where", action="append", default=[], metavar="DIMENSION=VALUE",
        help="Filter records before grouping; repeat for multiple exact filters.",
    )
    args = parser.parse_args()
    dimensions = tuple(part.strip() for part in args.group_by.split(",") if part.strip())
    filters: dict[str, str] = {}
    for expression in args.where:
        if "=" not in expression:
            parser.error("--where must use DIMENSION=VALUE")
        dimension, value = expression.split("=", 1)
        filters[dimension.strip()] = value.strip()
    rows = analyze_shared_store(args.store, dimensions, filters)
    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        columns = [*dimensions, "N", "Overlap", "R@1", "MRR", "Coverage", "Failed@maxK"]
        print(" | ".join(columns))
        print(" | ".join("---" for _ in columns))
        for row in rows:
            overlap = row["mean_lexical_overlap"]
            print(" | ".join([
                *(str(row["group"][dimension]) for dimension in dimensions),
                str(row["question_count"]), "n/a" if overlap is None else f"{overlap:.3f}",
                f"{row['recall_at_k'].get('1', 0):.3f}", f"{row['mrr']:.3f}",
                f"{row['mean_evidence_coverage']:.3f}",
                f"{row['failed_at_max_k']} ({row['failure_rate_at_max_k']:.1%})",
            ]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
