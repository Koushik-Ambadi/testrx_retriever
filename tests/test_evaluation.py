from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.chunking import Chunk
from testrx_retriever.evaluation import evaluate_retrieval, score_ranked_results
from testrx_retriever.vector_index import RetrievedChunk


def result(rank: int, units: tuple[str, ...]) -> RetrievedChunk:
    chunk = Chunk(
        chunk_id=f"CH-{rank}", document_id="doc", chunk_index=rank, text="text",
        token_count=1, token_start=rank, token_end=rank + 1, page_start=1, page_end=1,
        section_path=("1",), section_paths=(("1",),), semantic_unit_ids=units,
        source_element_ids=units, content_types=("paragraph",),
    )
    return RetrievedChunk(rank=rank, chunk_id=chunk.chunk_id, score=1 / rank, chunk=chunk)


class FakeRetriever:
    def __init__(self, results):
        self.results = results

    def retrieve(self, query: str, top_k: int):
        return self.results[:top_k]


class EvaluationTests(unittest.TestCase):
    def test_single_unit_complete_and_mrr(self) -> None:
        scored = score_ranked_results(["a"], [result(1, ("x",)), result(2, ("a",))], (1, 3), ["a", "alias"])
        self.assertFalse(scored["complete_at_k"]["1"])
        self.assertTrue(scored["complete_at_k"]["3"])
        self.assertEqual(scored["first_relevant_rank"], 2)
        self.assertEqual(scored["reciprocal_rank"], 0.5)
        self.assertEqual(scored["precision_at_k"], {"1": 0.0, "3": 0.5})

    def test_precision_uses_acceptable_lineage(self) -> None:
        scored = score_ranked_results(
            ["required"], [result(1, ("acceptable",)), result(2, ("noise",))], (1, 2),
            ["required", "acceptable"],
        )
        self.assertEqual(scored["precision_at_k"], {"1": 1.0, "2": 0.5})
        self.assertFalse(scored["complete_at_k"]["2"])

    def test_multi_unit_partial_and_complete_coverage(self) -> None:
        partial = score_ranked_results(["a", "b"], [result(1, ("a",))], (1,))
        self.assertEqual(partial["coverage_at_k"]["1"], 0.5)
        self.assertEqual(partial["failure_category"], "multi_unit_evidence_incomplete")
        complete = score_ranked_results(["a", "b"], [result(1, ("a",)), result(2, ("b",))], (1, 2))
        self.assertEqual(complete["coverage_at_k"]["2"], 1.0)
        self.assertTrue(complete["pass"])

    def test_no_hit_case(self) -> None:
        scored = score_ranked_results(["a"], [result(1, ("x",))], (1,))
        self.assertEqual(scored["reciprocal_rank"], 0.0)
        self.assertEqual(scored["failure_category"], "required_evidence_not_retrieved")

    def test_aggregate_recall_coverage_and_mrr(self) -> None:
        questions = [
            {"question_id": "Q1", "question": "q", "question_type": "factual", "difficulty": "easy", "retrieval_ground_truth": {"required_source_set": ["a"]}},
            {"question_id": "Q2", "question": "q", "question_type": "comparison", "difficulty": "hard", "retrieval_ground_truth": {"required_source_set": ["a", "b"]}},
        ]
        records, metrics = evaluate_retrieval(FakeRetriever([result(1, ("a",))]), questions, (1,))
        self.assertEqual(len(records), 2)
        self.assertEqual(metrics["recall_at_k"]["1"], 0.5)
        self.assertEqual(metrics["semantic_unit_recall_at_k"]["1"], 0.75)
        self.assertEqual(metrics["mrr"], 1.0)


if __name__ == "__main__":
    unittest.main()
