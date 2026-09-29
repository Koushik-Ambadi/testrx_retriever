# TESTRX Retriever roadmap

Status: living  
Owner: project architecture  
Created: 2026-09-09  
Last reviewed: 2026-09-29
Source of truth for: active gates, sequencing, and planned work  
Does not own: completed chronology, experiment measurements, or binding decisions

## Intent

Build a source-faithful, measurable retrieval system for the TESTRX manual, then
advance to grounded generation only after retrieval and context assembly have
explicit quality gates. Preserve provenance and reproducibility at every stage.

## Completed foundations

- Canonical PDF parsing, physical evidence, logical reconstruction, validation,
  warnings, and deterministic artifacts.
- Source-grounded golden dataset with 132 original questions and 64 controlled
  paraphrases.
- Deterministic lexical reference retrieval and normalized experiment storage.
- Token-window size and hashing-dimension investigation.
- Reusable analytics and failure categorization.
- Modular encoder, fusion, reranker, evaluation, and workflow boundaries.
- Pinned BGE/E5 encoder and MiniLM reranker candidate comparison.
- Deterministic hierarchy-aware chunkers and raw eight-variant matrix capture.
- Frozen hierarchy-384/BGE/MiniLM retrieval configuration, K tuning, and a
  configurable query-to-chunks wrapper.
- Project documentation ownership and testing strategy.

Completed dates and verification belong in `progress.md`. Binding rationale
belongs in `decisions.md`; measurements belong in generated artifacts and fixed
study records; cross-study conclusions and how they changed direction belong in
[`research-synthesis.md`](research-synthesis.md).

## Completed gate: hierarchy comparison and retriever freeze

Hierarchy-384 was selected over the 300/30 window on the quality/context/latency
frontier. BGE small English v1.5, MiniLM-L6 reranking, candidate K=10, and final
K=5 are frozen as configurable defaults. Measurements, regressions, and residual
risks are recorded in `configs/retrieval/production.md`.

## Active gate: context assembly

1. Add diversity-aware assembly for multi-unit, procedure, parent-context, and
   multi-section questions without changing the frozen first-stage defaults.
2. Add answer-span completeness and generator-facing context evaluation.
3. Define context deduplication, ordering, token-budget, citation, and abstention
   contracts.
4. Benchmark warm long-lived application latency on target deployment hardware.
5. Validate on a prospective or external query population before claiming
   cross-document generalization.

## Later gate: grounded generation

Generation begins only after the retrieval contract is frozen.

Required foundations:

- context assembly with stable source citations;
- answerability and abstention policy;
- grounded-answer evaluation and failure taxonomy;
- prompt/model revision and inference configuration;
- privacy, retention, and safety requirements.

A later retriever change is allowed only for a documented generator-facing
failure and must rerun the retrieval selection contract.

## Product gate

UI, sessions, telemetry, feedback capture, and service/API work remain deferred
until retrieval and generation behavior is measurable. Consent, privacy, schema,
and retention decisions must precede user-data collection.

## Global acceptance rules

- The PDF and checksum remain factual authority.
- Derived data and outputs retain source lineage and versioned schemas.
- Experiments change one controlled family of variables at a time.
- Generated artifacts are reproducible and follow `artifact-policy.md`.
- Commands, schemas, tests, and owning documentation change together.
- A phase is complete only after tests pass and the progress/decision records are
  updated.
