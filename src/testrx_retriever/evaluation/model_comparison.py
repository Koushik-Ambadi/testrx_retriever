"""Reusable model/category analysis over complete grounded result records."""

from __future__ import annotations

from collections import defaultdict
import itertools
from typing import Any, Callable

from .analysis import summarize_evaluations


Facet = Callable[[dict[str, Any]], Any]


def _bucket(value: int, bounds: tuple[int, ...]) -> str:
    for bound in bounds:
        if value <= bound:
            return f"<= {bound}"
    return f"> {bounds[-1]}"


def _categories(question: dict[str, Any]) -> list[str]:
    return [
        key.removeprefix("requires_")
        for key, enabled in question.get("evaluation_metadata", {}).items()
        if key.startswith("requires_") and enabled
    ] or ["none"]


QUESTION_FACETS: dict[str, Facet] = {
    "question_id": lambda q: q["question_id"],
    "question_type": lambda q: q["question_type"],
    "difficulty": lambda q: q["difficulty"],
    "answerability": lambda q: q.get("answerability", "unspecified"),
    "paraphrase_level": lambda q: q.get("paraphrase_level", "original"),
    "question_family": lambda q: q.get("source_question_id") or q["question_id"],
    "source_document": lambda q: q.get("source", {}).get("document", "none"),
    "source_page": lambda q: q.get("source", {}).get("pages", []) or ["none"],
    "source_section_path": lambda q: [" > ".join(path) for path in q.get("source", {}).get("section_paths", [])] or ["none"],
    "source_semantic_id": lambda q: q.get("source", {}).get("semantic_unit_ids", []) or ["none"],
    "source_element_id": lambda q: q.get("source", {}).get("element_ids", []) or ["none"],
    "primary_source": lambda q: q.get("retrieval_ground_truth", {}).get("primary_source", "none"),
    "required_source": lambda q: q.get("retrieval_ground_truth", {}).get("required_source_set", []) or ["none"],
    "acceptable_source": lambda q: q.get("retrieval_ground_truth", {}).get("acceptable_source_set", []) or ["none"],
    "hard_negative_source": lambda q: q.get("hard_negative_sources", []) or ["none"],
    "category": _categories,
    "evaluation_flag": lambda q: [key for key, enabled in q.get("evaluation_metadata", {}).items() if enabled] or ["none"],
    "notes_present": lambda q: bool(q.get("notes")),
    "question_length": lambda q: _bucket(len(q.get("question", "").split()), (8, 16, 32)),
    "answer_length": lambda q: _bucket(len(q.get("expected_answer", "").split()), (16, 32, 64)),
    "required_source_count": lambda q: len(q.get("retrieval_ground_truth", {}).get("required_source_set", [])),
    "acceptable_source_count": lambda q: len(q.get("retrieval_ground_truth", {}).get("acceptable_source_set", [])),
    "required_evidence_count": lambda q: len(q.get("required_evidence", [])),
    "supporting_evidence_count": lambda q: len(q.get("supporting_evidence", [])),
    "hard_negative_count": lambda q: len(q.get("hard_negative_sources", [])),
    "lexical_overlap_decile": lambda q: int(10 * float(q.get("lexical_diagnostics", {}).get("query_source_lexical_overlap", 0))),
    "overlap_review_flag": lambda q: bool(q.get("lexical_diagnostics", {}).get("overlap_review_flag", False)),
    "query_token_count": lambda q: _bucket(int(q.get("lexical_diagnostics", {}).get("query_token_count", 0)), (8, 16, 32)),
    "unique_query_token_count": lambda q: _bucket(int(q.get("lexical_diagnostics", {}).get("unique_query_token_count", 0)), (8, 16, 32)),
    "relevant_source_token_count": lambda q: _bucket(int(q.get("lexical_diagnostics", {}).get("relevant_source_token_count", 0)), (32, 128, 512)),
    "diagnostic_tokenizer": lambda q: "@".join(str(q.get("lexical_diagnostics", {}).get("tokenizer", {}).get(key, "none")) for key in ("name", "version")),
}


def analyze_model_comparison(
    system_records: dict[str, list[dict[str, Any]]],
    questions: list[dict[str, Any]],
    top_k: tuple[int, ...],
) -> dict[str, Any]:
    questions_by_id = {question["question_id"]: question for question in questions}
    rows: list[dict[str, Any]] = []
    overall = [
        {"system": system, **summarize_evaluations(records, top_k)}
        for system, records in sorted(system_records.items())
    ]
    for system, records in sorted(system_records.items()):
        for facet_name, extractor in QUESTION_FACETS.items():
            grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
            for record in records:
                value = extractor(questions_by_id[record["question_id"]])
                values = value if isinstance(value, list) else [value]
                for item in values:
                    grouped[item].append(record)
            for value, items in sorted(grouped.items(), key=lambda pair: str(pair[0])):
                rows.append({
                    "system": system,
                    "dimension": facet_name,
                    "value": value,
                    **summarize_evaluations(items, top_k),
                })
    top_level_fields = sorted(set(itertools.chain.from_iterable(question.keys() for question in questions)))
    field_inventory = {
        field: {
            "populated": sum(question.get(field) not in (None, "", [], {}) for question in questions),
            "analytics_usage": "grouped" if field in QUESTION_FACETS else (
                "derived_features" if field in {"question", "expected_answer", "source", "retrieval_ground_truth", "required_evidence", "supporting_evidence", "hard_negative_sources", "evaluation_metadata", "lexical_diagnostics"}
                else "identity_or_audit"
            ),
        }
        for field in top_level_fields
    }
    return {"schema_version": "1.0", "field_inventory": field_inventory, "overall": overall, "rows": rows}


def render_model_comparison_report(analysis: dict[str, Any]) -> str:
    selected = [row for row in analysis["rows"] if row["dimension"] in {"category", "question_type"}]
    lines = [
        "# Model comparison by golden-set category and type", "",
        "This report uses identical chunks, questions, ground truth, and metric definitions for every system.", "",
        "## Overall", "",
        "| System | N | R@1 | R@10 | MRR | Coverage |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in analysis["overall"]:
        max_k = str(row["maximum_k"])
        lines.append(
            f"| {row['system']} | {row['question_count']} | {row['recall_at_k'].get('1', 0):.3f} | "
            f"{row['recall_at_k'][max_k]:.3f} | {row['mrr']:.3f} | {row['mean_evidence_coverage']:.3f} |"
        )
    lines.extend([
        "", "## Best system by category and question type", "",
        "| Dimension | Value | Best system | N | R@1 | R@10 | MRR | Coverage |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ])
    segments: dict[tuple[str, Any], list[dict[str, Any]]] = defaultdict(list)
    for row in selected:
        segments[(row["dimension"], row["value"])].append(row)
    for (dimension, value), candidates in sorted(segments.items(), key=lambda item: (item[0][0], str(item[0][1]))):
        row = max(candidates, key=lambda item: (item["mrr"], item["recall_at_k"].get("1", 0), item["mean_evidence_coverage"]))
        max_k = str(row["maximum_k"])
        lines.append(
            f"| {dimension} | {value} | {row['system']} | {row['question_count']} | "
            f"{row['recall_at_k'].get('1', 0):.3f} | {row['recall_at_k'][max_k]:.3f} | "
            f"{row['mrr']:.3f} | {row['mean_evidence_coverage']:.3f} |"
        )
    lines.extend([
        "", "## Complete category and type matrix", "",
        "| Dimension | Value | System | N | R@1 | R@10 | MRR | Coverage |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ])
    for row in selected:
        recall = row["recall_at_k"]
        max_k = str(row["maximum_k"])
        lines.append(
            f"| {row['dimension']} | {row['value']} | {row['system']} | {row['question_count']} | "
            f"{recall.get('1', 0):.3f} | {recall[max_k]:.3f} | {row['mrr']:.3f} | "
            f"{row['mean_evidence_coverage']:.3f} |"
        )
    lines.extend([
        "", "The machine-readable analysis also covers identity, source, evidence-set, answerability, difficulty, paraphrase, evaluation-flag, text-length, lexical-diagnostic, and hard-negative facets. Free-text columns contribute derived lengths/counts and remain available in per-question result records rather than becoming meaningless one-row groups.", "",
    ])
    return "\n".join(lines)
