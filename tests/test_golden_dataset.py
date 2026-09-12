import csv
import json
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.golden_paraphrases import (
    DERIVED_LEVELS, PARAPHRASE_LEVELS, canonical_legacy_hash, lexical_diagnostics,
)
from testrx_retriever.tokenization import RegexTokenizer
DATASET_DIR = ROOT / "output" / "datasets" / "golden"


class GoldenDatasetContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [
            json.loads(line)
            for line in (DATASET_DIR / "golden_dataset.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        cls.document = json.loads(
            (ROOT / "output" / "parsing" / "document.json").read_text(encoding="utf-8")
        )
        cls.element_ids = set()

        def walk(element):
            cls.element_ids.add(element["id"])
            for child in element.get("children", []):
                walk(child)

        for section in cls.document["sections"]:
            for element in section["elements"]:
                walk(element)

    def test_extension_size_ids_and_order(self):
        self.assertEqual(len(self.rows), 196)
        originals = [row for row in self.rows if row["paraphrase_level"] == "original"]
        derived = [row for row in self.rows if row["paraphrase_level"] != "original"]
        self.assertEqual([row["question_id"] for row in originals], [f"Q{i:03d}" for i in range(1, 133)])
        self.assertTrue(all(row["source_question_id"] is None for row in originals))
        self.assertEqual(len(derived), 64)
        self.assertEqual({row["paraphrase_level"] for row in self.rows}, set(PARAPHRASE_LEVELS))
        for offset in range(0, len(derived), 4):
            family = derived[offset:offset + 4]
            source_id = family[0]["source_question_id"]
            self.assertEqual([row["question_id"] for row in family], [f"{source_id}-P{i}" for i in range(1, 5)])
            self.assertEqual([row["paraphrase_level"] for row in family], list(DERIVED_LEVELS))

    def test_legacy_records_have_stable_hash(self):
        originals = [row for row in self.rows if row["paraphrase_level"] == "original"]
        self.assertEqual(
            canonical_legacy_hash(originals),
            "055FD96DCE85DDD2483024F809E33AA8FBFA1F527D78B9F8984B41110E9D8E1A",
        )

    def test_derived_families_preserve_all_grounded_fields(self):
        originals = {row["question_id"]: row for row in self.rows if row["paraphrase_level"] == "original"}
        mutable = {"question_id", "question", "source_question_id", "paraphrase_level", "lexical_diagnostics"}
        for row in self.rows:
            if not row["source_question_id"]:
                continue
            source = originals[row["source_question_id"]]
            self.assertEqual(
                {key: value for key, value in row.items() if key not in mutable},
                {key: value for key, value in source.items() if key not in mutable},
            )

    def test_lexical_diagnostics_are_reproducible(self):
        elements = {}
        def collect(element):
            elements[element["id"]] = element
            for child in element.get("children", []):
                collect(child)
        for section in self.document["sections"]:
            for element in section["elements"]:
                collect(element)
        tokenizer = RegexTokenizer()
        for row in self.rows:
            self.assertEqual(row["lexical_diagnostics"], lexical_diagnostics(row, elements, tokenizer))

    def test_required_categories_and_difficulties(self):
        types = {row["question_type"] for row in self.rows}
        self.assertTrue({"definition", "factual", "procedure", "configuration", "comparison", "troubleshooting", "table", "figure", "multi-section", "cross-reference"}.issubset(types))
        self.assertEqual({row["difficulty"] for row in self.rows}, {"easy", "medium", "hard"})

    def test_source_ids_resolve(self):
        for row in self.rows:
            for element_id in row["source"]["element_ids"] + row["hard_negative_sources"]:
                self.assertIn(element_id, self.element_ids, f"{row['question_id']}: {element_id}")

    def test_retrieval_ground_truth_is_consistent(self):
        for row in self.rows:
            gt = row["retrieval_ground_truth"]
            self.assertIn(gt["primary_source"], gt["required_source_set"])
            self.assertTrue(set(gt["required_source_set"]).issubset(gt["acceptable_source_set"]))
            self.assertEqual(row["evaluation_metadata"]["requires_single_unit"], len(gt["required_source_set"]) == 1)
            self.assertEqual(row["evaluation_metadata"]["requires_multiple_units"], len(gt["required_source_set"]) > 1)

    def test_csv_matches_jsonl(self):
        with (DATASET_DIR / "golden_dataset.csv").open(encoding="utf-8-sig", newline="") as handle:
            csv_rows = list(csv.DictReader(handle))
        self.assertEqual(len(csv_rows), len(self.rows))
        self.assertEqual([r["question_id"] for r in csv_rows], [r["question_id"] for r in self.rows])


if __name__ == "__main__":
    unittest.main()
