from __future__ import annotations

from pathlib import Path
import sys
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.configuration import EmbeddingConfig
from testrx_retriever.retrieval.chunking import Chunk
from testrx_retriever.retrieval.encoders.lexical_hashing import StableHashingEmbedder
from testrx_retriever.retrieval.indexes import ExactVectorIndex


def chunk(index: int, text: str, element_id: str) -> Chunk:
    return Chunk(
        chunk_id=f"CH-{index:05d}-test",
        document_id="doc",
        chunk_index=index,
        text=text,
        token_count=len(text.split()),
        token_start=index * 5,
        token_end=index * 5 + len(text.split()),
        page_start=index + 1,
        page_end=index + 1,
        section_path=(f"{index + 1} Section",),
        section_paths=((f"{index + 1} Section",),),
        semantic_unit_ids=(element_id,),
        source_element_ids=(element_id,),
        content_types=("paragraph",),
    )


class EmbeddingAndRetrievalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.embedder = StableHashingEmbedder(
            EmbeddingConfig(model="stable_hashing_word_bigram", model_version="1.0", dimension=256)
        )
        self.chunks = [
            chunk(0, "configure CAN network signal logging", "can"),
            chunk(1, "remove a database dependency safely", "database"),
            chunk(2, "view the latest execution report", "report"),
        ]
        self.index = ExactVectorIndex(self.embedder)
        self.index.build_index(self.chunks)

    def test_embedding_is_deterministic_and_dimensioned(self) -> None:
        first = self.embedder.embed_one("CAN signal logging")
        second = self.embedder.embed_one("CAN signal logging")
        np.testing.assert_array_equal(first, second)
        self.assertEqual(first.shape, (256,))

    def test_retrieve_returns_requested_k_scores_and_metadata(self) -> None:
        results = self.index.retrieve("How do I configure CAN signal logging?", 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].chunk_id, self.chunks[0].chunk_id)
        self.assertIsInstance(results[0].score, float)
        self.assertEqual(results[0].chunk.source_element_ids, ("can",))

    def test_ranking_is_deterministic(self) -> None:
        first = [result.to_dict() for result in self.index.retrieve("execution report", 3)]
        second = [result.to_dict() for result in self.index.retrieve("execution report", 3)]
        self.assertEqual(first, second)

    def test_ties_use_chunk_order(self) -> None:
        tied = ExactVectorIndex(self.embedder)
        tied.build_index([chunk(4, "same words", "late"), chunk(2, "same words", "early")])
        results = tied.retrieve("same words", 2)
        self.assertEqual([result.chunk.chunk_index for result in results], [2, 4])


if __name__ == "__main__":
    unittest.main()
