# Retrieval model-comparison pipeline

Status: subsystem reference  
Owner: retrieval workflows  
Last reviewed: 2026-09-17

## Purpose

The pipeline makes the complete retrieval path runnable before component-level
optimization:

```text
canonical document
  -> fixed token chunks
  -> lexical and semantic bi-encoder retrieval
  -> optional reciprocal-rank fusion
  -> candidate reranking
  -> the same grounded evaluator for every system
```

The pipeline's `baseline.json` remains an engineering control. The selected
application path is separately frozen in `configs/retrieval/production.json`:
hierarchy max 384, BGE small English v1.5, MiniLM-L6 reranking, candidate K=10,
and final K=5. The decision evidence is in
`configs/retrieval/production.md`.

## Model separation

- `model_store/encoders/` stores first-stage query/document encoder manifests and
  local artifacts.
- `model_store/rerankers/` stores pairwise reranker manifests and local artifacts.
- `model_store/generators/` is reserved for the later generator stage.
- `src/testrx_retriever/retrieval/` contains runtime adapters, separated by the
  same roles.

Large weights live under each role's ignored `artifacts/` directory. Versioned
registries describe what is available. A run must explicitly select a local
artifact or pinned model; the baseline never downloads a model implicitly.

## Run

Install the project dependencies and execute:

```powershell
python -m pip install -e .
python -m testrx_retriever.workflows.model_comparison --config configs/pipelines/baseline.json
```

The command evaluates six systems: each of the two bi-encoders, their fused
ranking, and a reranked variant of all three. Outputs are written beneath
`output/retrieval/pipeline_baseline/` with shared chunks, a resolved run
configuration, summary metrics, and per-system metrics/results. Every system's
metrics also record pre-rerank Recall and evidence coverage at the configured
candidate depth, so reranking cannot hide inadequate candidate generation.

To use attention-based candidates, install the optional runtime and point the
appropriate config entry at a local model artifact:

```powershell
python -m pip install -e ".[transformers]"
```

Use `algorithm: sentence_transformer` for a bi-encoder and
`algorithm: sentence_transformer_cross_encoder` for a reranker. Both require a
`model_path`; model choice and acquisition are separate, explicit steps.

Install the pinned candidates into `model_store/` and run the production
candidate comparison with:

```powershell
python scripts/install_model_candidates.py
python -m testrx_retriever.workflows.model_comparison --config configs/pipelines/candidates.json
```

Run the hierarchy-aware chunking matrix through the same models, retrieval,
reranking, and evaluator with:

```powershell
python -m testrx_retriever.workflows.hierarchy_experiment --config configs/pipelines/hierarchical_chunking_experiment.json
```

The matrix runner only replaces the configured chunker. Hierarchy runs add raw
canonical-node measurements and emitted-chunk statistics. Optional latency
capture writes per-query nanosecond observations and explicitly records its
question-selection and cache policy; chunking, index build, and model loading
are outside that timing boundary.

The long-lived application boundary is `testrx_retriever.application` and its
CLI is `testrx-retrieve`. It returns ranked chunk text, complete source metadata,
total chunk tokens, and candidate/reranking timing. Candidate and final K may be
overridden per call without changing the frozen defaults.

## Experiment boundary

The baseline proves component wiring and remains a control; it is not the
selected application configuration. Future retriever changes must preserve the
evaluator and ground truth, establish candidate coverage before judging
reranking, report original and paraphrased results separately, and update the
binding production decision rather than silently changing defaults.
