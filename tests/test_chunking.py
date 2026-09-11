from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.baseline_config import ChunkingConfig
from testrx_retriever.chunking import TokenChunker


def synthetic_document() -> dict:
    return {
        "document_id": "doc-test",
        "source_sha256": "abc123",
        "sections": [
            {
                "section_id": "1",
                "ancestor_path": ["1 Example"],
                "sequence": 1,
                "elements": [
                    {
                        "id": "element-1",
                        "type": "paragraph",
                        "sequence": 1,
                        "text": "alpha beta gamma delta epsilon zeta eta theta",
                        "page_start": 1,
                        "page_end": 1,
                        "children": [],
                    },
                    {
                        "id": "group-1",
                        "type": "local_group",
                        "sequence": 2,
                        "text": "Interface",
                        "page_start": 2,
                        "page_end": 2,
                        "children": [
                            {
                                "id": "element-2",
                                "type": "list",
                                "sequence": 3,
                                "text": "iota kappa lambda mu nu xi omicron pi rho sigma tau",
                                "page_start": 2,
                                "page_end": 3,
                                "children": [],
                            }
                        ],
                    },
                ],
            }
        ],
    }


class TokenChunkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ChunkingConfig(chunk_size=8, chunk_overlap=2)
        self.chunker = TokenChunker(self.config)

    def test_output_and_ids_are_deterministic(self) -> None:
        first = [chunk.to_dict() for chunk in self.chunker.chunk_document(synthetic_document())]
        second = [chunk.to_dict() for chunk in self.chunker.chunk_document(copy.deepcopy(synthetic_document()))]
        self.assertEqual(first, second)
        self.assertEqual(
            json.dumps(first, sort_keys=True, ensure_ascii=False),
            json.dumps(second, sort_keys=True, ensure_ascii=False),
        )

    def test_size_overlap_and_nonempty_chunks(self) -> None:
        chunks = self.chunker.chunk_document(synthetic_document())
        self.assertTrue(chunks)
        self.assertTrue(all(0 < chunk.token_count <= self.config.chunk_size for chunk in chunks))
        for previous, current in zip(chunks, chunks[1:]):
            self.assertEqual(current.token_start, previous.token_end - self.config.chunk_overlap)

    def test_source_lineage_and_recursive_semantic_ownership_survive(self) -> None:
        chunks = self.chunker.chunk_document(synthetic_document())
        self.assertIn("element-1", {eid for chunk in chunks for eid in chunk.source_element_ids})
        child_chunk = next(chunk for chunk in chunks if "element-2" in chunk.source_element_ids)
        self.assertIn("group-1", child_chunk.semantic_unit_ids)
        self.assertIn("element-2", child_chunk.semantic_unit_ids)
        self.assertEqual(child_chunk.document_id, "doc-test")
        self.assertLessEqual(child_chunk.page_start, child_chunk.page_end)
        self.assertTrue(child_chunk.section_path)

    def test_invalid_overlap_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TokenChunker(ChunkingConfig(chunk_size=10, chunk_overlap=10))


if __name__ == "__main__":
    unittest.main()
