from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.evaluation.analysis import analyze_shared_store, summarize_evaluations


def evaluation(overlap: float, complete: bool, precision: float, reciprocal_rank: float) -> dict:
    return {
        "lexical_diagnostics": {"query_source_lexical_overlap": overlap},
        "evaluation": {
            "coverage_at_k": {"1": float(complete)},
            "complete_at_k": {"1": complete},
            "precision_at_k": {"1": precision},
            "reciprocal_rank": reciprocal_rank,
        },
    }


class AnalyticsTests(unittest.TestCase):
    def test_summary_metrics(self) -> None:
        summary = summarize_evaluations(
            [evaluation(0.8, True, 1.0, 1.0), evaluation(0.2, False, 0.0, 0.0)], (1,)
        )
        self.assertEqual(summary["question_count"], 2)
        self.assertEqual(summary["mean_lexical_overlap"], 0.5)
        self.assertEqual(summary["recall_at_k"]["1"], 0.5)
        self.assertEqual(summary["precision_at_k"]["1"], 0.5)
        self.assertEqual(summary["failed_at_max_k"], 1)
        self.assertEqual(summary["failure_rate_at_max_k"], 0.5)

    def test_shared_store_groups_run_and_question_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            store = Path(directory)
            run = {
                "experiment_id": "exp", "run_id": "run", "role": "sweep",
                "components": {
                    "chunking": {"strategy": "token_window", "chunk_size": 500, "chunk_overlap": 50},
                    "embedding": {"family": "lexical", "model": "hash", "dimension": 4096},
                    "retrieval": {"algorithm": "cosine"}, "reranking": {"algorithm": "none"},
                },
            }
            question = {
                "experiment_id": "exp", "run_id": "run", "question_id": "Q001",
                "source_question_id": None, "difficulty": "easy", "question_type": "factual",
                "paraphrase_level": "original", "categories": ["single_unit"],
                "source_semantic_unit_ids": ["unit-1"], "lexical_diagnostics": {"query_source_lexical_overlap": 0.5},
                "coverage_at_k": {"1": 1.0}, "complete_at_k": {"1": True},
                "precision_at_k": {"1": 1.0}, "reciprocal_rank": 1.0,
            }
            (store / "runs.jsonl").write_text(json.dumps(run) + "\n", encoding="utf-8")
            (store / "question_metrics.jsonl").write_text(json.dumps(question) + "\n", encoding="utf-8")
            rows = analyze_shared_store(store, ("token_size", "embedding_family", "paraphrase_level"))
            self.assertEqual(rows[0]["group"], {
                "token_size": 500, "embedding_family": "lexical", "paraphrase_level": "original",
            })
            self.assertEqual(rows[0]["mrr"], 1.0)
            filtered = analyze_shared_store(
                store, ("question_type",), {"embedding_family": "lexical"}
            )
            self.assertEqual(filtered[0]["group"], {"question_type": "factual"})
            self.assertEqual(
                analyze_shared_store(store, ("question_type",), {"embedding_family": "transformer"}), []
            )


if __name__ == "__main__":
    unittest.main()
