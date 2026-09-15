from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from testrx_retriever.baseline_config import ChunkingConfig
from testrx_retriever.chunking import Chunk
from testrx_retriever.retrieval.encoders import build_bi_encoder
from testrx_retriever.retrieval.rerankers import build_reranker
from testrx_retriever.pipeline import (
    PipelineConfig,
    ReciprocalRankFusionRetriever,
    RerankedRetriever,
    run_pipeline,
)
from testrx_retriever.vector_index import ExactVectorIndex


def chunk(index: int, text: str, element_id: str) -> Chunk:
    return Chunk(
        chunk_id=f"CH-{index:05d}-test", document_id="doc", chunk_index=index,
        text=text, token_count=len(text.split()), token_start=index * 5,
        token_end=index * 5 + len(text.split()), page_start=1, page_end=1,
        section_path=("1 Test",), section_paths=(("1 Test",),),
        semantic_unit_ids=(element_id,), source_element_ids=(element_id,),
        content_types=("paragraph",),
    )


class PipelineComponentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chunks = [
            chunk(0, "configure controller area network logging", "can"),
            chunk(1, "generate and inspect execution reports", "report"),
            chunk(2, "remove database dependency", "database"),
        ]

    def test_lsa_bi_encoder_produces_normalized_independent_query_vectors(self) -> None:
        encoder = build_bi_encoder({
            "id": "lsa", "algorithm": "latent_semantic_lsa",
            "hash_dimension": 128, "latent_dimension": 2,
        })
        documents = encoder.encode_documents([item.text for item in self.chunks])
        query = encoder.encode_queries(["network controller logging"])
        self.assertEqual(documents.shape, (3, 2))
        self.assertEqual(query.shape, (1, 2))
        self.assertAlmostEqual(float(np.linalg.norm(query[0])), 1.0, places=5)

    def test_retrieval_fusion_and_reranking_preserve_chunk_identity(self) -> None:
        lexical = ExactVectorIndex(build_bi_encoder({
            "id": "lexical", "algorithm": "stable_hashing_word_bigram", "dimension": 256,
        }))
        lexical.build_index(self.chunks)
        semantic = ExactVectorIndex(build_bi_encoder({
            "id": "lsa", "algorithm": "latent_semantic_lsa",
            "hash_dimension": 256, "latent_dimension": 2,
        }))
        semantic.build_index(self.chunks)
        fused = ReciprocalRankFusionRetriever([lexical, semantic], candidate_k=3)
        reranked = RerankedRetriever(
            fused,
            build_reranker({"id": "pair", "algorithm": "lexical_pairwise_baseline"}),
            candidate_k=3,
        )
        results = reranked.retrieve("How do I configure network logging?", 2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].chunk_id, self.chunks[0].chunk_id)
        self.assertEqual([item.rank for item in results], [1, 2])


class PipelineIntegrationTests(unittest.TestCase):
    def test_complete_flow_writes_each_system(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            document_path = root / "document.json"
            dataset_path = root / "golden.jsonl"
            output_path = root / "pipeline"
            document_path.write_text(json.dumps({
                "document_id": "doc", "source_sha256": "ABC",
                "sections": [{
                    "section_id": "1", "ancestor_path": ["1 Test"], "sequence": 1,
                    "elements": [{
                        "id": "unit-1", "type": "paragraph", "sequence": 1,
                        "text": "configure network signal logging", "page_start": 1,
                        "page_end": 1, "children": [],
                    }],
                }],
            }), encoding="utf-8")
            dataset_path.write_text(json.dumps({
                "question_id": "Q001", "question": "configure signal logging",
                "question_type": "procedure", "difficulty": "easy",
                "retrieval_ground_truth": {"required_source_set": ["unit-1"]},
            }) + "\n", encoding="utf-8")
            config = PipelineConfig(
                schema_version="1.0",
                document_path=document_path, golden_dataset_path=dataset_path,
                output_directory=output_path,
                chunking=ChunkingConfig(chunk_size=10, chunk_overlap=1),
                top_k=(1,), candidate_k=1,
                bi_encoders=(
                    {"id": "lexical", "algorithm": "stable_hashing_word_bigram", "dimension": 64},
                    {"id": "lsa", "algorithm": "latent_semantic_lsa", "hash_dimension": 64, "latent_dimension": 4},
                ),
                fusions=({"enabled": True, "id": "hybrid", "encoder_ids": ["lexical", "lsa"]},),
                rerankers=({"id": "pair", "algorithm": "lexical_pairwise_baseline"},),
            )
            run = run_pipeline(config, root)
            self.assertEqual(len(run["systems"]), 6)
            self.assertTrue((output_path / "summary.json").is_file())
            self.assertTrue((output_path / "analysis" / "model_category_report.md").is_file())
            for system in run["systems"]:
                self.assertTrue((output_path / "systems" / system / "metrics.json").is_file())


if __name__ == "__main__":
    unittest.main()
