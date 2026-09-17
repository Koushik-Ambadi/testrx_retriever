# Experiment Documentation

Status: configuration-area index  
Owner: retrieval experiments  
Last reviewed: 2026-09-17

This directory holds hashing/token-window experiment configurations and their
fixed rationale and findings. Pipeline model and hierarchy experiments live
beside their configurations under `configs/pipelines/`. Project-wide
architecture, decisions, progress, limitations, and reviews remain under
`docs/`.

## Convention

- Use one stable `experiment_id` in each configuration.
- Keep hashing/token-window sweep configurations here. Keep configurable model
  comparison and hierarchy matrix definitions under `configs/pipelines/`.
- Write compact results to the shared `output/retrieval/experiments/` store.
- Keep full chunks, embeddings, and ranked payloads only for an explicitly
  designated reference run under `output/retrieval/reference/`.
- Record material interpretation and follow-up decisions in both the relevant
  experiment document and the project-level decision/progress files.

## Current studies

- `chunk-dimension-sweep.md`: token-window size, hashing dimension, index-size
  effects, lexical overlap, lineage density, and collision analysis.
- `paraphrase-bias-baseline.md`: controlled paraphrase families, lexical-overlap
  diagnostics, paired retrieval degradation, and interpretation boundaries.
- `failure-analysis.md`: settings, types, categories, persistent failures,
  paraphrase failure modes, and the next-experiment decision.
- `../../pipelines/candidate-model-comparison.md`: BGE, E5, fusion, and reranker
  comparison.
- `../../pipelines/hierarchical-chunking-experiment.md`: natural hierarchy
  measurements, bounded hierarchy contract, latency boundary, and run record.
