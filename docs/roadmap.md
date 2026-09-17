# TESTRX Retriever roadmap

Status: living  
Owner: project architecture  
Created: 2026-09-09  
Last reviewed: 2026-09-17  
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
- Project documentation ownership and testing strategy.

Completed dates and verification belong in `progress.md`. Rationale belongs in
`decisions.md`; measurements belong in generated artifacts and fixed experiment
records beside their configurations.

## Active gate: hierarchy comparison and validation design

Objective: determine whether one bounded hierarchy policy improves complete,
focused evidence retrieval enough to replace the 300/30 token-window diagnostic
anchor.

Required work:

1. Define family-grouped development and held-out partitions without splitting
   original/paraphrase families.
2. Add span-complete or evidence-completeness views that distinguish lineage
   presence from complete answer-bearing text.
3. Compare fixed K together with index exposure, chunks required for complete
   evidence, fallback behavior, and latency boundaries.
4. Inspect persistent multi-unit, table, figure, and cross-reference failures.
5. Shortlist at most one bounded hierarchy configuration and retain the
   token-window control.

Exit criteria:

- evaluation populations and selection rules are frozen before final comparison;
- no configuration is selected only from aggregate MRR;
- candidate retrieval coverage is reported before reranking;
- the selected policy has a documented quality, latency, and complexity case;
- failures and regressions are explicitly recorded.

## Next gate: retriever and context assembly

After chunk-policy selection:

1. Tune candidate depth on the fixed development population.
2. Compare dense, lexical, and justified hybrid candidate generation.
3. Add diversity/evidence assembly for multi-chunk questions.
4. Tune reranked context depth separately from candidate depth.
5. Select on held-out families and freeze the retriever contract.

The final contract must specify chunk policy, encoder revision and prefix policy,
index/retrieval algorithm, candidate depth, fusion, reranker, final context depth,
latency boundary, and fallback behavior.

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
