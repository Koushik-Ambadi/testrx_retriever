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
from testrx_retriever.retrieval.hierarchical_chunking import (
    HierarchicalChunker,
    build_hierarchy,
    hierarchy_node_records,
    token_statistics,
)


def synthetic_document() -> dict:
    return {
        "document_id": "doc-test",
        "source_sha256": "abc123",
        "sections": [
            {
                "section_id": "1",
                "title": "Example",
                "level": 1,
                "parent_section_id": None,
                "ancestor_path": ["1 Example"],
                "sequence": 1,
                "page_start": 1,
                "page_end": 3,
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


class HierarchicalChunkerTests(unittest.TestCase):
    def test_hierarchy_traversal_uses_canonical_node_types(self) -> None:
        root = build_hierarchy(synthetic_document())
        self.assertEqual(root.children[0].hierarchy_level, "section_level_1")
        self.assertEqual(root.children[0].children[1].hierarchy_level, "element:local_group")
        self.assertEqual(root.children[0].children[1].children[0].node_id, "element-2")

    def test_parent_too_large_descends_and_child_under_limit_is_emitted(self) -> None:
        chunks = HierarchicalChunker(ChunkingConfig(
            strategy="hierarchical_max_tokens", max_tokens=20,
        )).chunk_document(synthetic_document())
        self.assertGreater(len(chunks), 1)
        self.assertNotIn("1", {chunk.source_element_ids for chunk in chunks})
        self.assertTrue(any("element-1" in chunk.source_element_ids for chunk in chunks))
        self.assertTrue(any(chunk.split_reason == "parent_exceeded_max" for chunk in chunks))

    def test_top_level_node_that_fits_has_no_false_split_reason(self) -> None:
        chunks = HierarchicalChunker(ChunkingConfig(
            strategy="hierarchical_max_tokens", max_tokens=100,
        )).chunk_document(synthetic_document())
        self.assertEqual(len(chunks), 1)
        self.assertIsNone(chunks[0].split_reason)

    def test_nested_descent_preserves_parent_context_and_lineage(self) -> None:
        chunks = HierarchicalChunker(ChunkingConfig(
            strategy="hierarchical_max_tokens", max_tokens=14,
        )).chunk_document(synthetic_document())
        child = next(chunk for chunk in chunks if "element-2" in chunk.source_element_ids)
        self.assertIn("Hierarchy:", child.text)
        self.assertIn("Interface", child.text)
        self.assertIn("group-1", child.semantic_unit_ids)
        self.assertEqual(child.parent_node_id, "group-1")

    def test_oversized_leaf_uses_deterministic_bounded_fallback(self) -> None:
        config = ChunkingConfig(strategy="hierarchical_max_tokens", max_tokens=8)
        first = HierarchicalChunker(config).chunk_document(synthetic_document())
        second = HierarchicalChunker(config).chunk_document(copy.deepcopy(synthetic_document()))
        self.assertEqual([chunk.to_dict() for chunk in first], [chunk.to_dict() for chunk in second])
        self.assertTrue(any(chunk.fallback_split for chunk in first))
        self.assertTrue(all(chunk.token_count <= 8 for chunk in first))
        self.assertTrue(all(chunk.split_reason for chunk in first))

    def test_pure_hierarchy_emits_each_non_document_node(self) -> None:
        chunks = HierarchicalChunker(ChunkingConfig(
            strategy="hierarchical_pure",
        )).chunk_document(synthetic_document())
        self.assertEqual(len(chunks), 4)
        self.assertEqual(
            [chunk.hierarchy_level for chunk in chunks],
            ["section_level_1", "element:paragraph", "element:local_group", "element:list"],
        )

    def test_raw_node_records_and_statistics_are_reproducible(self) -> None:
        first = hierarchy_node_records(synthetic_document())
        second = hierarchy_node_records(copy.deepcopy(synthetic_document()))
        self.assertEqual(first, second)
        summary = token_statistics(first)
        document_stats = next(item for item in summary["levels"] if item["level"] == "document")
        self.assertEqual(document_stats["node_count"], 1)
        self.assertGreater(document_stats["max_tokens"], 0)
        self.assertIn("256", document_stats["nodes_over_limit"])

    def test_token_window_output_remains_unchanged_by_new_config_fields(self) -> None:
        legacy = TokenChunker(ChunkingConfig(chunk_size=8, chunk_overlap=2))
        explicit = TokenChunker(ChunkingConfig(
            strategy="token_window", chunk_size=8, chunk_overlap=2, max_tokens=None,
        ))
        self.assertEqual(
            [chunk.to_dict() for chunk in legacy.chunk_document(synthetic_document())],
            [chunk.to_dict() for chunk in explicit.chunk_document(synthetic_document())],
        )


if __name__ == "__main__":
    unittest.main()
