from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.baseline import run_baseline
from testrx_retriever.baseline_config import BaselineConfig


class BaselineIntegrationTests(unittest.TestCase):
    def test_complete_output_bundle_is_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document_path = root / "document.json"
            dataset_path = root / "golden.jsonl"
            output_path = root / "retrieval"
            document_path.write_text(
                json.dumps(
                    {
                        "document_id": "doc",
                        "source_sha256": "ABC123",
                        "sections": [
                            {
                                "section_id": "1",
                                "ancestor_path": ["1 Example"],
                                "sequence": 1,
                                "elements": [
                                    {
                                        "id": "unit-1", "type": "paragraph", "sequence": 1,
                                        "text": "alpha beta gamma delta epsilon", "page_start": 1,
                                        "page_end": 1, "children": [],
                                    }
                                ],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            dataset_path.write_text(
                json.dumps(
                    {
                        "question_id": "Q001", "question": "Where is alpha?",
                        "question_type": "factual", "difficulty": "easy",
                        "retrieval_ground_truth": {"required_source_set": ["unit-1"]},
                    }
                ) + "\n",
                encoding="utf-8",
            )
            config = BaselineConfig.from_dict(
                {
                    "schema_version": "1.0",
                    "document_path": "document.json",
                    "golden_dataset_path": "golden.jsonl",
                    "output_directory": "retrieval",
                    "chunking": {"strategy": "token_window", "chunk_size": 5, "chunk_overlap": 1},
                    "tokenizer": {"name": "testrx_regex_tokenizer", "version": "1.0"},
                    "embedding": {"model": "stable_hashing_word_bigram", "model_version": "1.0", "dimension": 64},
                    "retrieval": {"algorithm": "cosine_similarity_exact", "top_k": [1]},
                },
                root,
            )

            run_baseline(config, root)
            first = {
                path.relative_to(output_path).as_posix(): path.read_bytes()
                for path in output_path.rglob("*") if path.is_file()
            }
            run_baseline(config, root)
            second = {
                path.relative_to(output_path).as_posix(): path.read_bytes()
                for path in output_path.rglob("*") if path.is_file()
            }
            self.assertEqual(first, second)
            self.assertIn("index/embeddings.npy", first)
            self.assertIn("evaluation/retrieval_results.jsonl", first)
            self.assertIn("manifest.json", first)


if __name__ == "__main__":
    unittest.main()
