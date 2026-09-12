"""Deterministic controlled-paraphrase extension for a grounded golden set."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from .tokenization import RegexTokenizer


PARAPHRASE_LEVELS = (
    "original",
    "level_1_light",
    "level_2_moderate",
    "level_3_strong",
    "level_4_conceptual",
)
DERIVED_LEVELS = PARAPHRASE_LEVELS[1:]
LEVEL_SUFFIX = {level: f"P{index}" for index, level in enumerate(DERIVED_LEVELS, start=1)}
ADDED_FIELDS = {"paraphrase_level", "source_question_id", "lexical_diagnostics"}
MUTABLE_FAMILY_FIELDS = {"question_id", "question", *ADDED_FIELDS}
OVERLAP_REVIEW_THRESHOLDS = {
    "level_1_light": 0.85,
    "level_2_moderate": 0.70,
    "level_3_strong": 0.60,
    "level_4_conceptual": 0.50,
}


def canonical_legacy_hash(questions: list[dict[str, Any]]) -> str:
    """Hash legacy fields so appended diagnostics cannot hide source edits."""
    lines = []
    for question in questions:
        legacy = {key: value for key, value in question.items() if key not in ADDED_FIELDS}
        lines.append(json.dumps(legacy, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    payload = ("\n".join(lines) + "\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def source_text(element: dict[str, Any]) -> str:
    parts = [element.get("text", "")]
    data = element.get("data") or {}
    for key in ("items", "rows", "resolved_rows"):
        value = data.get(key)
        if isinstance(value, list):
            parts.append(json.dumps(value, ensure_ascii=False))
    parts.extend(source_text(child) for child in element.get("children", []))
    return " ".join(part for part in parts if part)


def lexical_diagnostics(
    question: dict[str, Any], elements: dict[str, dict[str, Any]], tokenizer: RegexTokenizer
) -> dict[str, Any]:
    required_ids = question["retrieval_ground_truth"]["required_source_set"]
    relevant_text = "\n".join(source_text(elements[element_id]) for element_id in required_ids)
    query_tokens = [token.text.casefold() for token in tokenizer.tokenize(question["question"])]
    source_tokens = [token.text.casefold() for token in tokenizer.tokenize(relevant_text)]
    unique_query = set(query_tokens)
    unique_source = set(source_tokens)
    overlap = len(unique_query & unique_source) / len(unique_query) if unique_query else 0.0
    level = question.get("paraphrase_level", "original")
    threshold = OVERLAP_REVIEW_THRESHOLDS.get(level)
    return {
        "tokenizer": {"name": tokenizer.name, "version": tokenizer.version},
        "query_token_count": len(query_tokens),
        "unique_query_token_count": len(unique_query),
        "relevant_source_token_count": len(source_tokens),
        "query_source_lexical_overlap": round(overlap, 6),
        "overlap_review_threshold": threshold,
        "overlap_review_flag": threshold is not None and overlap > threshold,
    }


def _family_projection(question: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in question.items() if key not in MUTABLE_FAMILY_FIELDS}


def extend_with_paraphrases(
    questions: list[dict[str, Any]],
    specification: dict[str, Any],
    elements: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Append configured paraphrases while cloning every grounded field exactly."""
    if tuple(specification["levels"]) != DERIVED_LEVELS:
        raise ValueError(f"Paraphrase levels must be {DERIVED_LEVELS}")
    originals = deepcopy(questions)
    by_id = {question["question_id"]: question for question in originals}
    if len(by_id) != len(originals):
        raise ValueError("Original question IDs are not unique")
    for question in originals:
        question["paraphrase_level"] = "original"
        question["source_question_id"] = None

    derived: list[dict[str, Any]] = []
    seen_sources: set[str] = set()
    for family in specification["families"]:
        source_id = family["source_question_id"]
        if source_id in seen_sources:
            raise ValueError(f"Duplicate paraphrase family: {source_id}")
        seen_sources.add(source_id)
        if source_id not in by_id:
            raise ValueError(f"Unknown source question: {source_id}")
        if set(family["questions"]) != set(DERIVED_LEVELS):
            raise ValueError(f"Family {source_id} must define every paraphrase level")
        source = by_id[source_id]
        for level in DERIVED_LEVELS:
            text = str(family["questions"][level]).strip()
            if not text:
                raise ValueError(f"Empty paraphrase: {source_id} {level}")
            clone = deepcopy(source)
            clone["question_id"] = f"{source_id}-{LEVEL_SUFFIX[level]}"
            clone["question"] = text
            clone["paraphrase_level"] = level
            clone["source_question_id"] = source_id
            if _family_projection(clone) != _family_projection(source):
                raise AssertionError(f"Ground truth changed for {clone['question_id']}")
            derived.append(clone)

    extended = originals + derived
    identifiers = [question["question_id"] for question in extended]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Extended question IDs are not unique")
    tokenizer = RegexTokenizer()
    for question in extended:
        question["lexical_diagnostics"] = lexical_diagnostics(question, elements, tokenizer)
    return extended


def load_paraphrase_specification(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
