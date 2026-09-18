from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.application import RetrievalApplication, RetrievalApplicationConfig


class RetrievalApplicationTests(unittest.TestCase):
    def make_project(self, root: Path, *, candidate_k: int = 3, top_k: int = 2) -> Path:
        (root / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
        (root / "document.json").write_text(json.dumps({
            "document_id": "doc", "title": "Test", "source_file": "test.pdf",
            "source_sha256": "ABC", "sections": [{
                "section_id": "1", "title": "Test", "level": 1,
                "parent_section_id": None, "ancestor_path": ["1 Test"],
                "sequence": 1, "page_start": 1, "page_end": 1,
                "elements": [
                    {"id": "unit-1", "type": "paragraph", "sequence": 1,
                     "text": "configure controller area network signal logging",
                     "page_start": 1, "page_end": 1, "children": []},
                    {"id": "unit-2", "type": "paragraph", "sequence": 2,
                     "text": "inspect execution reports", "page_start": 1,
                     "page_end": 1, "children": []},
                    {"id": "unit-3", "type": "paragraph", "sequence": 3,
                     "text": "remove database dependency", "page_start": 1,
                     "page_end": 1, "children": []},
                ],
            }],
        }), encoding="utf-8")
        config_path = root / "retrieval.json"
        config_path.write_text(json.dumps({
            "schema_version": "1.0",
            "inputs": {"document_path": "document.json"},
            "chunking": {"strategy": "hierarchical_max_tokens", "max_tokens": 12},
            "encoder": {
                "id": "lexical", "algorithm": "stable_hashing_word_bigram", "dimension": 256,
            },
            "reranker": {"id": "pairwise", "algorithm": "lexical_pairwise_baseline"},
            "retrieval": {"candidate_k": candidate_k, "top_k": top_k},
        }), encoding="utf-8")
        return config_path

    def test_query_returns_ranked_chunks_provenance_tokens_and_timing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = self.make_project(Path(directory))
            application = RetrievalApplication.from_config(config_path)
            response = application.retrieve("How do I configure network logging?")
            self.assertEqual(response["configuration"]["candidate_k"], 3)
            self.assertEqual(response["configuration"]["top_k"], 2)
            self.assertEqual(response["result_count"], 2)
            self.assertEqual(response["chunks"][0]["metadata"]["source_element_ids"], ("unit-1",))
            self.assertGreater(response["total_chunk_tokens"], 0)
            self.assertGreater(response["timing"]["total_retrieval_cycle_ns"], 0)

    def test_call_time_k_overrides_are_applied_and_validated(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            application = RetrievalApplication.from_config(self.make_project(Path(directory)))
            response = application.retrieve("reports", candidate_k=2, top_k=1)
            self.assertEqual(response["configuration"]["candidate_k"], 2)
            self.assertEqual(response["result_count"], 1)
            with self.assertRaisesRegex(ValueError, "candidate_k"):
                application.retrieve("reports", candidate_k=1, top_k=2)
            with self.assertRaisesRegex(ValueError, "empty"):
                application.retrieve("  ")

    def test_config_rejects_top_k_above_candidate_k(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            config_path = self.make_project(Path(directory), candidate_k=1, top_k=2)
            with self.assertRaisesRegex(ValueError, "candidate_k"):
                RetrievalApplicationConfig.load(config_path)


if __name__ == "__main__":
    unittest.main()
