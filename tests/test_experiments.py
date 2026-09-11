from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.experiments import SweepConfig, run_sweep


class SweepConfigTests(unittest.TestCase):
    def test_overlap_rounds_half_up(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "configs" / "sweep.json"
            config_path.parent.mkdir()
            config_path.write_text(json.dumps({
                "schema_version": "1.0",
                "document_path": "document.json",
                "golden_dataset_path": "golden.jsonl",
                "output_directory": "output/sweep",
                "chunk_sizes": [125, 200],
                "overlap_ratio": 0.1,
                "embedding_dimensions": [64, 128],
                "control": {"chunk_size": 500, "chunk_overlap": 50, "embedding_dimension": 128},
                "random_baseline": {"seed": 7, "trials": 2},
                "retrieval_top_k": [1],
            }), encoding="utf-8")
            config = SweepConfig.load(config_path)
            self.assertEqual(config.overlap_for(125), 13)
            self.assertEqual(config.overlap_for(200), 20)

    def test_small_sweep_is_reproducible_and_keeps_control(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "configs").mkdir()
            (root / "output").mkdir()
            document = {
                "document_id": "doc", "source_sha256": "ABC123",
                "sections": [{
                    "section_id": "1", "ancestor_path": ["1 Example"], "sequence": 1,
                    "elements": [{
                        "id": "unit-1", "type": "paragraph", "sequence": 1,
                        "text": "alpha beta gamma delta epsilon zeta eta theta iota kappa",
                        "page_start": 1, "page_end": 1, "children": [],
                    }],
                }],
            }
            (root / "output" / "document.json").write_text(json.dumps(document), encoding="utf-8")
            question = {
                "question_id": "Q001", "question": "Where is alpha?", "question_type": "factual",
                "difficulty": "easy", "retrieval_ground_truth": {"required_source_set": ["unit-1"]},
            }
            (root / "output" / "golden.jsonl").write_text(json.dumps(question) + "\n", encoding="utf-8")
            config_path = root / "configs" / "sweep.json"
            config_path.write_text(json.dumps({
                "schema_version": "1.0", "document_path": "output/document.json",
                "golden_dataset_path": "output/golden.jsonl", "output_directory": "output/sweep",
                "chunk_sizes": [5], "overlap_ratio": 0.2, "embedding_dimensions": [32, 64],
                "control": {"chunk_size": 10, "chunk_overlap": 1, "embedding_dimension": 64},
                "random_baseline": {"seed": 7, "trials": 5}, "retrieval_top_k": [1],
            }), encoding="utf-8")
            config = SweepConfig.load(config_path)
            first = run_sweep(config, root)
            first_files = {p.relative_to(config.output_directory).as_posix(): p.read_bytes() for p in config.output_directory.rglob("*") if p.is_file()}
            second = run_sweep(config, root)
            second_files = {p.relative_to(config.output_directory).as_posix(): p.read_bytes() for p in config.output_directory.rglob("*") if p.is_file()}
            self.assertEqual(first, second)
            self.assertEqual(first_files, second_files)
            self.assertEqual(len(first["runs"]), 3)
            self.assertEqual(first["runs"][-1]["role"], "control")
            self.assertIn("question_diagnostics.jsonl", first_files)
            self.assertIn("manifest.json", first_files)


if __name__ == "__main__":
    unittest.main()
