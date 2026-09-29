# TESTRX Retriever architecture

Status: living  
Owner: project architecture  
Last reviewed: 2026-09-29
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
  -> configurable in-process query-to-ranked-chunks application boundary
```

The PDF and checksum are factual authority. Canonical structure, benchmark
lineage, chunks, rankings, metrics, and reports are derived layers with explicit
schemas and reproducibility rules.

## Subsystems

- `parsing/`: source extraction, domain entities, normalization, structure,
  tables, figures, inspection, and validation. Parser implementation and its
  domain types are colocated in this package.
- `retrieval/`: tokenization, token-window and hierarchy-aware chunking,
  encoders, exact indexes, fusion inputs, and rerankers.
- `evaluation/`: grounded metrics, cross-run analytics, and model/category
  comparison views.
- `workflows/`: reference build, model comparison, production query, and
  hierarchy experiment orchestration.
- `src/testrx_retriever/experiments/`: parameterized sweep implementation and
  CLI package, retaining the package-level `SweepConfig`, `run_sweep`, and
  `main` interface.
- root `experiments/`: retrieval experiment configurations, frozen protocols,
  results, and cross-study analysis; raw run artifacts remain under `output/`.
- `configs/pipelines/`: pipeline-specific experiment configurations and their
  reports, kept together; shared runtime and dataset configurations remain in
  `configs/`.
- `configuration.py`: shared typed configuration contracts used by baseline,
  retrieval, experiments, and the production application.
- `application.py`: long-lived production query wrapper; it loads the fixed
  corpus/index once and accepts per-call candidate and final K overrides.
- `common/`: deterministic file and hashing foundations.
- `configs/`: shared runtime, dataset, and pipeline configurations. Dedicated
  retrieval studies live under root `experiments/retrieval/`; pipeline-specific
  experiment configurations and reports stay together under `configs/pipelines/`.
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
parse arguments and delegate. Subsystems are imported from their owning
packages; retired flat aliases are not part of the supported internal interface.

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

Canonical parsing, the grounded benchmark, retrieval experiments, and the
hierarchy-384/BGE/MiniLM retrieval contract are complete. The application now
ends at ranked, provenance-rich chunks. Context assembly, answer generation,
network service concerns, and end-user evaluation remain outside the boundary.
