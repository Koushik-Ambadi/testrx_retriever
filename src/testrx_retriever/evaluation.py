"""Golden retrieval evaluation and baseline report rendering."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable, Protocol

from .vector_index import RetrievedChunk


class Retriever(Protocol):
    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]: ...


def result_source_ids(result: RetrievedChunk) -> set[str]:
    return set(result.chunk.semantic_unit_ids) | set(result.chunk.source_element_ids)


def score_ranked_results(
    required_source_ids: Iterable[str],
    results: list[RetrievedChunk],
    top_k_values: tuple[int, ...],
    acceptable_source_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    required = set(required_source_ids)
    acceptable = set(acceptable_source_ids) if acceptable_source_ids is not None else set(required)
    if not required:
        raise ValueError("required_source_ids cannot be empty")
    if not acceptable:
        raise ValueError("acceptable_source_ids cannot be empty")
    coverage_at_k: dict[str, float] = {}
    complete_at_k: dict[str, bool] = {}
    retrieved_required_at_k: dict[str, list[str]] = {}
    precision_at_k: dict[str, float] = {}
    for top_k in top_k_values:
        ranked = results[:top_k]
        retrieved = set().union(*(result_source_ids(result) for result in ranked)) if ranked else set()
        matched = sorted(required & retrieved)
        coverage_at_k[str(top_k)] = round(len(matched) / len(required), 6)
        complete_at_k[str(top_k)] = len(matched) == len(required)
        retrieved_required_at_k[str(top_k)] = matched
        precision_at_k[str(top_k)] = round(
            sum(bool(acceptable & result_source_ids(result)) for result in ranked) / len(ranked), 6
        ) if ranked else 0.0
    first_relevant_rank = next(
        (result.rank for result in results if required & result_source_ids(result)),
        None,
    )
    max_coverage = coverage_at_k[str(max(top_k_values))]
    if max_coverage == 0:
        failure_category = "required_evidence_not_retrieved"
    elif max_coverage < 1:
        failure_category = "multi_unit_evidence_incomplete"
    else:
        failure_category = None
    return {
        "required_source_ids": sorted(required),
        "retrieved_required_source_ids_at_k": retrieved_required_at_k,
        "coverage_at_k": coverage_at_k,
        "complete_at_k": complete_at_k,
        "precision_at_k": precision_at_k,
        "first_relevant_rank": first_relevant_rank,
        "reciprocal_rank": round(1 / first_relevant_rank, 10) if first_relevant_rank else 0.0,
        "pass": complete_at_k[str(max(top_k_values))],
        "failure_category": failure_category,
    }


def evaluate_retrieval(
    retriever: Retriever,
    questions: list[dict[str, Any]],
    top_k_values: tuple[int, ...],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not questions:
        raise ValueError("questions cannot be empty")
    max_k = max(top_k_values)
    records: list[dict[str, Any]] = []
    for question in questions:
        results = retriever.retrieve(question["question"], max_k)
        required = question["retrieval_ground_truth"]["required_source_set"]
        acceptable = question["retrieval_ground_truth"].get("acceptable_source_set", required)
        evaluation = score_ranked_results(required, results, top_k_values, acceptable)
        records.append(
            {
                "question_id": question["question_id"],
                "question": question["question"],
                "question_type": question["question_type"],
                "difficulty": question["difficulty"],
                "paraphrase_level": question.get("paraphrase_level", "original"),
                "source_question_id": question.get("source_question_id"),
                "lexical_diagnostics": question.get("lexical_diagnostics", {}),
                "evaluation_metadata": question.get("evaluation_metadata", {}),
                "source": question.get("source", {}),
                "required_semantic_units": required,
                "required_evidence": question.get("required_evidence", []),
                "retrieved_chunks": [result.to_dict() for result in results],
                "retrieved_chunk_ids": [result.chunk_id for result in results],
                "retrieved_semantic_units": [
                    list(result.chunk.semantic_unit_ids) for result in results
                ],
                "retrieval_scores": [result.score for result in results],
                "evaluation": evaluation,
            }
        )

    count = len(records)
    aggregate = {
        "dataset_size": count,
        "recall_at_k": {
            str(k): round(sum(record["evaluation"]["complete_at_k"][str(k)] for record in records) / count, 6)
            for k in top_k_values
        },
        "semantic_unit_recall_at_k": {
            str(k): round(sum(record["evaluation"]["coverage_at_k"][str(k)] for record in records) / count, 6)
            for k in top_k_values
        },
        "precision_at_k": {
            str(k): round(sum(record["evaluation"]["precision_at_k"][str(k)] for record in records) / count, 6)
            for k in top_k_values
        },
        "mrr": round(sum(record["evaluation"]["reciprocal_rank"] for record in records) / count, 6),
        "mean_evidence_coverage": round(
            sum(record["evaluation"]["coverage_at_k"][str(max_k)] for record in records) / count,
            6,
        ),
        "passed_at_max_k": sum(record["evaluation"]["pass"] for record in records),
        "failed_at_max_k": sum(not record["evaluation"]["pass"] for record in records),
        "evidence_coverage_distribution": {
            "zero": round(sum(record["evaluation"]["coverage_at_k"][str(max_k)] == 0 for record in records) / count, 6),
            "partial": round(sum(0 < record["evaluation"]["coverage_at_k"][str(max_k)] < 1 for record in records) / count, 6),
            "complete": round(sum(record["evaluation"]["coverage_at_k"][str(max_k)] == 1 for record in records) / count, 6),
        },
        "failure_categories": dict(
            sorted(
                Counter(
                    record["evaluation"]["failure_category"]
                    for record in records
                    if record["evaluation"]["failure_category"]
                ).items()
            )
        ),
    }
    return records, aggregate


def render_retrieval_report(run: dict[str, Any], records: list[dict[str, Any]]) -> str:
    metrics = run["metrics"]
    config = run["configuration"]
    top_k_values = config["retrieval"]["top_k"]
    lines = [
        "# TESTRX Baseline Retrieval Report",
        "",
        "## Overall",
        "",
        f"- Dataset size: {metrics['dataset_size']}",
        f"- Chunk count: {run['chunk_count']}",
        f"- Chunking: {config['chunking']['strategy']} ({config['chunking']['chunk_size']} tokens, {config['chunking']['chunk_overlap']} overlap)",
        f"- Tokenizer: {config['tokenizer']['name']} {config['tokenizer']['version']}",
        f"- Embedding model: {config['embedding']['model']} {config['embedding']['model_version']}",
        f"- Embedding dimension: {config['embedding']['dimension']}",
        f"- Retriever: {config['retrieval']['algorithm']}",
    ]
    lines.extend(f"- Recall@{k}: {metrics['recall_at_k'][str(k)]:.3f}" for k in top_k_values)
    lines.extend(f"- Precision@{k}: {metrics['precision_at_k'][str(k)]:.3f}" for k in top_k_values)
    lines.extend(
        [
            f"- MRR: {metrics['mrr']:.3f}",
            f"- Mean evidence coverage@{max(top_k_values)}: {metrics['mean_evidence_coverage']:.3f}",
            f"- Complete questions@{max(top_k_values)}: {metrics['passed_at_max_k']} of {metrics['dataset_size']}",
            "",
            "Recall@K is strict: a multi-unit question counts only when every required source unit appears by K. Semantic-unit recall reports mean required-unit coverage.",
            "",
            "## Failure analysis",
            "",
        ]
    )
    if metrics["failure_categories"]:
        lines.extend(f"- {name}: {value}" for name, value in metrics["failure_categories"].items())
    else:
        lines.append("- No failures at the maximum K.")
    lines.extend(["", "## Per-question results", ""])
    for record in records:
        evaluation = record["evaluation"]
        retrieved_units = list(
            dict.fromkeys(unit for group in record["retrieved_semantic_units"] for unit in group)
        )
        lines.extend(
            [
                f"### {record['question_id']} - {record['question']}",
                "",
                f"- Type / difficulty: {record['question_type']} / {record['difficulty']}",
                f"- Required units: {', '.join(record['required_semantic_units'])}",
                f"- Retrieved chunks: {', '.join(record['retrieved_chunk_ids'])}",
                f"- Retrieved semantic units: {', '.join(retrieved_units)}",
                f"- Scores: {', '.join(f'{score:.6f}' for score in record['retrieval_scores'])}",
                f"- First relevant rank: {evaluation['first_relevant_rank'] if evaluation['first_relevant_rank'] is not None else 'not retrieved'}",
                f"- Evidence coverage@{max(top_k_values)}: {evaluation['coverage_at_k'][str(max(top_k_values))]:.3f}",
                f"- Result: {'PASS' if evaluation['pass'] else 'FAIL'}",
            ]
        )
        if evaluation["failure_category"]:
            lines.append(f"- Failure category: {evaluation['failure_category']}")
        lines.append("")
    return "\n".join(lines)
