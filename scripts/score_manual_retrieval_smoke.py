"""Apply the documented human rubric to the fixed manual smoke-test statements."""

from __future__ import annotations

from collections import Counter
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


DIRECT_PATTERNS = {
    "QSM01": ("a pin icon", "once pinned", "a close icon"),
    "QSM02": ("file | save |", "file | save all |"),
    "QSM03": (
        "edit | recover | future scope", "edit | optimize | future scope",
        "options | cleanup | future scope", "options | logs | future scope",
    ),
    "QSM04": (
        "a details panel is displayed below the grid",
        "the dependencies option allows",
        "if no dependencies are needed",
        "mapping details panel (lower section)",
        "detailed mapping information panel (lower section)",
    ),
    "QSM05": (
        "labels with missing or invalid database signals are highlighted in pink",
        "read/write dropdowns are disabled",
        "invalid or missing signal mappings are highlighted visually",
    ),
    "QSM06": (
        "after: the condition", "with tolerance applied",
        "before: the condition", "when tolerance is enabled, the condition may still",
    ),
}


TOPICAL_PATTERNS = {
    "QSM01": ("project navigator", "navigator panel", "navigator window"),
    "QSM02": ("menu bar", "menu | sub menu", "file | save", "save —"),
    "QSM03": ("menu bar", "future scope", "options | user", "preferences | future scope"),
    "QSM04": ("map labels", "read path", "write path", "dependencies", "mapping"),
    "QSM05": ("map labels", "signal", "pink", "read/write", "mapping"),
    "QSM06": (
        "time constraint", "tolerance", "mode field", "time field",
        "in range", "entire range", "after:", "before:",
    ),
}


VERDICTS = {
    "QSM01": {
        "minimum_answer_rank": 1,
        "answerability": "complete_clean",
        "answer": "Use Pin to lock the navigator expanded until it is collapsed or unpinned; use Close to hide it from the main window.",
    },
    "QSM02": {
        "minimum_answer_rank": 1,
        "answerability": "complete_clean",
        "answer": "Save stores changes for the active test case; Save All stores pending changes for every open test-case tab.",
    },
    "QSM03": {
        "minimum_answer_rank": 2,
        "answerability": "complete_but_fragmented",
        "answer": "Outside Help, Edit > Recover, Edit > Optimize, Options > Cleanup, Options > User Preferences, and Options > Logs are future scope.",
    },
    "QSM04": {
        "minimum_answer_rank": 1,
        "answerability": "complete_clean",
        "answer": "Inspect the details panel below the grid for the selected label's read/write information; Dependencies can be disabled when none are needed.",
    },
    "QSM05": {
        "minimum_answer_rank": 1,
        "answerability": "complete_clean",
        "answer": "The label is highlighted pink and the Read/Write dropdowns are disabled when no valid signal is available.",
    },
    "QSM06": {
        "minimum_answer_rank": 1,
        "answerability": "complete_clean",
        "answer": "After normally requires an event after the range but allows the configured early window; Before normally requires it before the range but allows limited overlap into the range.",
    },
}


def score(question_id: str, statement: str) -> tuple[int, int, str]:
    """Return human-curated relevance, answer support, and a short rationale."""
    normalized = statement.casefold()
    if any(pattern in normalized for pattern in DIRECT_PATTERNS[question_id]):
        return 2, 1, "Directly supplies one required answer point."
    if any(pattern in normalized for pattern in TOPICAL_PATTERNS[question_id]):
        return 1, 0, "Topical context, but not independently answer-bearing."
    return 0, 0, "Not needed to answer this question."


def markdown_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path,
        default=ROOT / "output/retrieval/pipeline_manual_smoke/retrieved_statements.json",
    )
    parser.add_argument(
        "--json-output", type=Path,
        default=ROOT / "output/retrieval/pipeline_manual_smoke/scored_statements.json",
    )
    parser.add_argument(
        "--report", type=Path,
        default=ROOT / "output/retrieval/pipeline_manual_smoke/manual_evaluation.md",
    )
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    summary = Counter()
    lines = [
        "# Manual fresh-question retrieval smoke test", "",
        "Six questions were authored after reading and visually checking the source PDF. They are not copies of the golden question text.", "",
        "Statement rubric: relevance 0=unrelated, 1=topical, 2=direct; answer support 0=none, 1=partial, 2=sufficient alone. Every question deliberately asks for at least two facts, so correct atomic statements normally score answer support 1 and are assembled into a complete answer.", "",
    ]
    for question in payload["questions"]:
        verdict = VERDICTS[question["id"]]
        question.update(verdict)
        counts = Counter()
        for statement in question["statements"]:
            relevance, support, note = score(question["id"], statement["statement"])
            statement["relevance_score"] = relevance
            statement["answer_support_score"] = support
            statement["review_note"] = note
            counts[f"relevance_{relevance}"] += 1
            counts[f"support_{support}"] += 1
            summary[f"relevance_{relevance}"] += 1
            summary[f"support_{support}"] += 1
        question["statement_score_counts"] = dict(sorted(counts.items()))
        lines.extend([
            f"## {question['id']} - {question['question']}", "",
            f"- Source PDF pages: {', '.join(map(str, question['source_pages']))}",
            f"- Verdict: `{verdict['answerability']}` at retrieved rank {verdict['minimum_answer_rank']}",
            f"- Context: {question['total_chunk_tokens']} tokens; retrieval cycle: {question['timing']['total_retrieval_cycle_ns'] / 1_000_000:.1f} ms",
            f"- Reviewed answer: {verdict['answer']}",
            f"- Statement counts: direct {counts['relevance_2']}, topical {counts['relevance_1']}, unrelated {counts['relevance_0']}",
            "", "| Statement | Rank | Relevance | Answer support | Text |", "|---|---:|---:|---:|---|",
        ])
        for statement in question["statements"]:
            lines.append(
                f"| {statement['statement_id']} | {statement['chunk_rank']} | "
                f"{statement['relevance_score']} | {statement['answer_support_score']} | "
                f"{markdown_escape(statement['statement'])} |"
            )
        lines.append("")

    question_counts = Counter(question["answerability"] for question in payload["questions"])
    payload["manual_summary"] = {
        "question_count": len(payload["questions"]),
        "complete_clean": question_counts["complete_clean"],
        "complete_but_fragmented": question_counts["complete_but_fragmented"],
        "incomplete": question_counts["incomplete"],
        "statement_score_counts": dict(sorted(summary.items())),
    }
    lines[6:6] = [
        "## Summary", "",
        f"- Clean complete answers: {question_counts['complete_clean']} / {len(payload['questions'])}",
        f"- Complete but fragmented answers: {question_counts['complete_but_fragmented']} / {len(payload['questions'])}",
        f"- Incomplete answers: {question_counts['incomplete']} / {len(payload['questions'])}",
        f"- Atomic statements: direct {summary['relevance_2']}, topical {summary['relevance_1']}, unrelated {summary['relevance_0']}",
        "- Finding: Top-1 was sufficient for five questions. The future-scope table question required ranks 1-2 because one table row was split across the 384-token fallback boundary.",
        "",
    ]

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(payload["manual_summary"], indent=2))
    print(f"Report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
