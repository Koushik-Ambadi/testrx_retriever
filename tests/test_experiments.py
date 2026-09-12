from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.experiments import SweepConfig, run_sweep


def write_config(root: Path, experiment_id: str) -> Path:
    config_path = root / "configs" / f"{experiment_id}.json"
    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text(json.dumps({
        "schema_version": "2.0",
        "experiment_id": experiment_id,
        "title": "Synthetic sweep",
        "hypothesis": "The compact store is reusable.",
        "inputs": {
            "document_path": "output/parsing/document.json",
            "golden_dataset_path": "output/datasets/golden.jsonl",
        },
        "output_store": "output/retrieval/experiments",
        "retention": {
            "run_metrics": True, "question_metrics": True, "chunks": False,
            "embeddings": False, "ranked_results": False,
        },
        "evaluation": {
            "top_k": [1], "random_baseline": {"seed": 7, "trials": 5},
            "question_filter": {"paraphrase_levels": ["original"]},
        },
        "components": {
            "chunkers": [{
                "strategy": "token_window",
                "parameters": {
                    "chunk_sizes": [5],
                    "overlap": {"mode": "ratio", "value": 0.2, "rounding": "half_up"},
                },
            }],
            "embedders": [{
                "family": "lexical",
                "model": "stable_hashing_word_bigram", "model_version": "1.0",
                "parameters": {"dimensions": [32, 64]},
            }],
            "retrievers": [{"algorithm": "cosine_similarity_exact", "parameters": {}}],
            "rerankers": [{"algorithm": "none", "parameters": {}}],
        },
        "controls": [{
            "label": "control",
            "chunking": {"strategy": "token_window", "chunk_size": 10, "chunk_overlap": 1},
            "embedding": {"family": "lexical", "model": "stable_hashing_word_bigram", "model_version": "1.0", "dimension": 64},
            "retrieval": {"algorithm": "cosine_similarity_exact", "parameters": {}},
            "reranking": {"algorithm": "none", "parameters": {}},
        }],
    }), encoding="utf-8")
    return config_path


class ExperimentStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "pyproject.toml").write_text(
            "[project]\nname='test'\nversion='0'\n", encoding="utf-8"
        )
        parsing = self.root / "output" / "parsing"
        datasets = self.root / "output" / "datasets"
        parsing.mkdir(parents=True)
        datasets.mkdir(parents=True)
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
        (parsing / "document.json").write_text(json.dumps(document), encoding="utf-8")
        question = {
            "question_id": "Q001", "question": "Where is alpha?", "question_type": "factual",
            "difficulty": "easy", "retrieval_ground_truth": {"required_source_set": ["unit-1"]},
            "paraphrase_level": "original", "source_question_id": None,
            "lexical_diagnostics": {"query_source_lexical_overlap": 0.5},
            "source": {"pages": [1], "section_paths": [["1 Example"]], "semantic_unit_ids": ["unit-1"]},
            "evaluation_metadata": {"requires_single_unit": True, "requires_table": False},
        }
        (datasets / "golden.jsonl").write_text(json.dumps(question) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_overlap_rounds_half_up(self) -> None:
        config = SweepConfig.load(write_config(self.root, "rounding-test"))
        chunker = config.chunkers[0]
        chunker["parameters"]["overlap"]["value"] = 0.1
        self.assertEqual(config.overlap_for(chunker, 125), 13)
        self.assertEqual(config.overlap_for(chunker, 200), 20)

    def test_shared_store_is_reproducible_and_upserts_experiments(self) -> None:
        first_config = SweepConfig.load(write_config(self.root, "experiment-one"))
        first = run_sweep(first_config, self.root)
        store = first_config.output_directory
        first_files = {path.name: path.read_bytes() for path in store.iterdir() if path.is_file()}
        second = run_sweep(first_config, self.root)
        second_files = {path.name: path.read_bytes() for path in store.iterdir() if path.is_file()}
        self.assertEqual(first, second)
        self.assertEqual(first_files, second_files)
        self.assertEqual(len(first["runs"]), 3)
        self.assertEqual(set(first_files), {"experiments.jsonl", "runs.jsonl", "question_metrics.jsonl", "manifest.json"})

        second_config = SweepConfig.load(write_config(self.root, "experiment-two"))
        run_sweep(second_config, self.root)
        experiments = [json.loads(line) for line in (store / "experiments.jsonl").read_text().splitlines()]
        runs = [json.loads(line) for line in (store / "runs.jsonl").read_text().splitlines()]
        questions = [json.loads(line) for line in (store / "question_metrics.jsonl").read_text().splitlines()]
        self.assertEqual(len(experiments), 2)
        self.assertEqual(len(runs), 6)
        self.assertEqual(len(questions), 6)
        self.assertEqual(questions[0]["source_semantic_unit_ids"], ["unit-1"])
        self.assertEqual(questions[0]["categories"], ["single_unit"])
        self.assertEqual(questions[0]["paraphrase_level"], "original")
        self.assertEqual(questions[0]["precision_at_k"], {"1": 1.0})
        self.assertEqual(runs[0]["components"]["embedding"]["family"], "lexical")


if __name__ == "__main__":
    unittest.main()
