"""Run a small, fresh-question retrieval smoke test and split chunks into statements."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.application import RetrievalApplication


QUESTIONS = (
    {
        "id": "QSM01",
        "question": "Which Project Navigator control keeps the panel permanently visible, and which control removes it from the main window?",
        "source_pages": [8],
        "expected_points": [
            "Pin locks the Project Navigator in an expanded state until it is collapsed or unpinned.",
            "Close hides the Project Navigator from the main window.",
        ],
    },
    {
        "id": "QSM02",
        "question": "What is the difference between Save and Save All in the File menu?",
        "source_pages": [9],
        "expected_points": [
            "Save stores changes for the currently active test case.",
            "Save All stores pending changes for all open test-case tabs.",
        ],
    },
    {
        "id": "QSM03",
        "question": "Outside the Help menu, which menu commands are marked as future scope?",
        "source_pages": [9, 10],
        "expected_points": [
            "Edit > Recover and Edit > Optimize are future scope.",
            "Options > Cleanup, Options > User Preferences, and Options > Logs are future scope.",
        ],
    },
    {
        "id": "QSM04",
        "question": "In Map Labels, where can I inspect extra read/write path information, and can dependency labels be disabled?",
        "source_pages": [48],
        "expected_points": [
            "The details panel below the grid shows additional read/write path information for the selected label.",
            "The Dependencies option can be disabled when dependency labels are not needed.",
        ],
    },
    {
        "id": "QSM05",
        "question": "How does Map Labels react when a database signal is missing or invalid?",
        "source_pages": [50],
        "expected_points": [
            "The affected label is highlighted in pink.",
            "Read/Write dropdowns are disabled when valid signals are unavailable.",
        ],
    },
    {
        "id": "QSM06",
        "question": "How do the After and Before time-constraint modes differ when tolerance is enabled?",
        "source_pages": [32],
        "expected_points": [
            "After normally requires the condition after the acceptable range but permits an early-tolerance window.",
            "Before normally requires the condition before the acceptable range but permits limited overlap into the range.",
        ],
    },
)


def split_statements(text: str) -> list[str]:
    """Create review-sized statements while retaining headings and table rows."""
    statements: list[str] = []
    for line in (part.strip(" -\t") for part in text.splitlines()):
        if not line:
            continue
        pieces = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", line)
        statements.extend(piece.strip() for piece in pieces if piece.strip())
    return statements


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", type=Path, default=ROOT / "configs/retrieval/production.json",
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "output/retrieval/pipeline_manual_smoke/retrieved_statements.json",
    )
    parser.add_argument("--candidate-k", type=int, default=None)
    parser.add_argument("--top-k", type=int, default=None)
    args = parser.parse_args()

    application = RetrievalApplication.from_config(args.config)
    records = []
    for question in QUESTIONS:
        response = application.retrieve(
            question["question"], candidate_k=args.candidate_k, top_k=args.top_k,
        )
        statements = []
        for chunk in response["chunks"]:
            for statement_index, statement in enumerate(split_statements(chunk["text"]), start=1):
                statements.append({
                    "statement_id": (
                        f"{question['id']}-C{chunk['rank']}-S{statement_index}"
                    ),
                    "chunk_rank": chunk["rank"],
                    "chunk_id": chunk["chunk_id"],
                    "statement": statement,
                    "relevance_score": None,
                    "answer_support_score": None,
                    "review_note": None,
                })
        records.append({
            **question,
            "retrieval_configuration": response["configuration"],
            "total_chunk_tokens": response["total_chunk_tokens"],
            "timing": response["timing"],
            "chunks": response["chunks"],
            "statements": statements,
        })

    payload = {
        "schema_version": "1.0",
        "score_contract": {
            "relevance_score": {"0": "unrelated", "1": "topically related", "2": "directly relevant"},
            "answer_support_score": {"0": "cannot support answer", "1": "supports part", "2": "sufficient alone"},
        },
        "questions": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8",
    )
    print(f"Wrote {len(records)} fresh questions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
