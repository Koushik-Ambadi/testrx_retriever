# Experiment Documentation

This directory holds experiment-specific rationale and findings. Project-wide
architecture, decisions, progress, operations, schemas, limitations, and review
status remain in the top-level `docs/` files.

## Convention

- Use one stable `experiment_id` in each configuration.
- Add configurations under `configs/retrieval/experiments/`; do not create an
  output directory per experiment or per run.
- Write compact results to the shared `output/retrieval/experiments/` store.
- Keep full chunks, embeddings, and ranked payloads only for an explicitly
  designated reference run under `output/retrieval/reference/`.
- Record material interpretation and follow-up decisions in both the relevant
  experiment document and the project-level decision/progress files.

## Current studies

- `chunk_dimension_study.md`: token-window size, hashing dimension, index-size
  effects, lexical overlap, lineage density, and collision analysis.
