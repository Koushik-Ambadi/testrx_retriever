# TESTRX Retriever architecture

Status: living  
Owner: project architecture  
Last reviewed: 2026-09-17  
Source of truth for: current subsystem boundaries and dependency direction

## System boundary

The project converts one preserved TESTRX manual into a provenance-rich
canonical document, a grounded benchmark, and reproducible retrieval evidence.
It currently stops before context assembly, answer generation, UI, service/API,
and user-data collection.

## Data flow

```text
immutable PDF
  -> physical extraction and typed evidence
  -> conservative logical reconstruction
  -> canonical document and validation artifacts
  -> independently grounded golden benchmark
  -> configurable chunking
  -> encoder/index/candidate retrieval
  -> optional fusion and reranking
  -> grounded evaluation, analytics, and experiment evidence
```

The PDF and checksum are factual authority. Canonical structure, benchmark
lineage, chunks, rankings, metrics, and reports are derived layers with explicit
schemas and reproducibility rules.

## Subsystems

- `parsing/` plus temporary flat compatibility modules: source extraction,
  domain entities, normalization, structure, tables, figures, inspection, and
  validation.
- `retrieval/`: tokenization, token-window and hierarchy-aware chunking,
  encoders, exact indexes, fusion inputs, and rerankers.
- `evaluation/`: grounded metrics, cross-run analytics, and model/category
  comparison views.
- `workflows/`: reference build, model comparison, and hierarchy experiment
  orchestration.
- `common/`: deterministic file and hashing foundations.
- `configs/`: declarative reference, experiment, and pipeline definitions.
- `model_store/`: versioned registries and ignored local artifacts separated by
  encoder, reranker, and generator roles.
- `skills/`: reusable cross-project workflows. Skills contain general lifecycle
  practices only; TESTRX-specific technical knowledge remains with this project.
- `output/`: durable benchmark/reference evidence plus ignored ordinary runs,
  governed by `artifact-policy.md`.

Subsystem-specific behavior and operation are documented beside the owning code
or configuration and indexed from `docs/README.md`.

## Dependency direction

```text
common + parsing domain
        <- parsing
        <- retrieval core
             <- evaluation
                  <- experiments and workflows
                       <- CLI entry points
```

Lower layers do not import workflows. Evaluation depends on small retrieval
protocols and source lineage rather than concrete workflow classes. CLI modules
parse arguments and delegate. Legacy flat imports remain thin compatibility
shims during migration.

## Reproducibility principles

- No implicit network calls, model downloads, OCR, LLMs, timestamps, or random
  identities in deterministic artifact paths.
- Source traversal, tokenization, chunk IDs, ranking tie-breaks, JSON ordering,
  and manifests are stable.
- Uncertain parsing evidence is preserved and surfaced as warnings rather than
  silently invented.
- Full ranked payloads are retained only for designated references or ignored
  ordinary runs; normalized experiment stores avoid repeated chunks/vectors.
- Model artifacts are selected explicitly by registry/configuration identity.

## Current state

Canonical parsing, the grounded benchmark, lexical reference studies, production
candidate comparison, and raw hierarchy experiments are complete. Learned dense
retrieval and reranking are available but no production retriever or chunk policy
is frozen. The active gate is hierarchy comparison and held-out retrieval
selection before context assembly or generation.
