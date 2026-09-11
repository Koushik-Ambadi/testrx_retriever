import csv
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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

    def test_seed_size_and_ids(self):
        self.assertGreaterEqual(len(self.rows), 100)
        self.assertLessEqual(len(self.rows), 200)
        self.assertEqual([row["question_id"] for row in self.rows], [f"Q{i:03d}" for i in range(1, len(self.rows) + 1)])

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
