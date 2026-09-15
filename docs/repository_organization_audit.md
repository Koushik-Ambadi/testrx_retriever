# Repository Organization Audit

Date: 2026-09-13

## Executive summary

The repository has a sound conceptual pipeline and good reproducibility habits,
but its physical organization has not kept pace with its growth from a PDF
parser into a parser, benchmark builder, retrieval laboratory, model comparison
pipeline, and analytics suite.

The most important problems are:

1. `src/testrx_retriever/` mixes parsing, dataset construction, retrieval,
   evaluation, experiment management, analytics, model adapters, CLI entry
   points, and artifact I/O in one mostly flat package.
2. `__init__.py` imports the PDF parser eagerly. Importing an unrelated module
   such as the tokenizer therefore requires `pdfplumber` and defeats subsystem
   isolation.
3. `baseline.py`, `pipeline.py`, and `experiments.py` are overlapping workflow
   orchestrators. Shared JSON/JSONL and hashing utilities live in
   `baseline.py`, causing other high-level workflows to depend on another
   workflow module.
4. `models.py`, `modeling/`, and the top-level `models/` directory use nearly
   identical names for three different concepts: document entities, executable
   model adapters, and local model artifacts.
5. Generated artifacts occupy about 51.4 MiB, including about 14.7 MiB of
   versioned retrieval evidence. The policy is deliberate but the directory
   name `output/` does not distinguish durable benchmark fixtures from disposable
   run artifacts.
6. Documentation is extensive but increasingly historical: `decisions.md`,
   `review.md`, `progress.md`, and `plan.md` total more than 2,200 lines, while
   the current architecture inventory omits newer pipeline/modeling components.
7. Configuration contracts are split across three modules and three related but
   inconsistent JSON shapes.
8. Two production modules exceed 500 lines, and the 539-line golden-dataset
   script combines curated data, validation, serialization, report generation,
   and command execution.

The recommended response is an incremental package reorganization, not a
rewrite. Preserve algorithms and artifact contracts, first add characterization
tests, then move code behind compatibility imports and small CLI wrappers.

## Scope and evidence

The audit covered:

- all tracked and visible repository files outside `.git`;
- top-level purpose and naming;
- Python module sizes, definitions, and internal imports;
- CLI and configuration boundaries;
- generated/tracked artifact policy;
- documentation roles and overlap;
- test organization and one test-discovery run.

Observed inventory:

| Area | Visible files | Approximate size | Assessment |
|---|---:|---:|---|
| `src/` | 67 including bytecode caches | 0.41 MiB | Core, but package boundaries need work |
| `tests/` | 27 including bytecode caches | 0.18 MiB | Core; mirrors features only partially |
| `docs/` | 16 | 0.13 MiB | Valuable, but historical/current concerns overlap |
| `configs/` | 5 | 0.01 MiB | Core, sensible top-level category |
| `source/` | 2 | 3.45 MiB | Core input, but name is easily confused with `src/` |
| `models/` | 10 | negligible without weights | Conditional runtime store; name conflicts with code concepts |
| `output/` | 40 | 51.43 MiB | Mixed durable evidence and disposable generated data |
| `scripts/` | 3 including bytecode | 0.10 MiB | Necessary jobs, but one is too monolithic |

The working tree already contains unrelated user changes and new pipeline work.
This report does not modify, move, or remove those files.

## What is relevant

### Product source and contracts

- `src/testrx_retriever/`: all current parser and retrieval implementation.
- `pyproject.toml`: packaging, runtime dependencies, optional transformer
  dependency, and five console entry points.
- `configs/`: declarative dataset, reference-run, experiment, and pipeline
  configurations.
- `tests/`: behavioral and regression coverage for parsing, dataset generation,
  retrieval, experiments, analytics, and the newer pipeline.

### Authoritative input and benchmark material

- `source/TESTRX_User_Manual.pdf`: authoritative domain input.
- `source/README.md`: source identity and checksum record.
- `output/datasets/golden/`: derived but durable benchmark contract and review
  evidence.

### Reproducibility and decision evidence

- `docs/architecture.md`, `docs/schema.md`, `docs/runbook.md`, and
  `docs/decisions.md` contain important operating and design contracts.
- `docs/experiments/` contains study-specific interpretation that should remain
  separate from runtime code.
- `output/retrieval/reference/` is relevant if the project intentionally keeps
  one frozen, auditable reference result in Git.
- `output/retrieval/experiments/` is relevant if normalized historical metrics
  are treated as versioned research evidence.

### Conditional model assets

- The registries and READMEs under `models/` are relevant as declarations of
  model roles and installation state.
- `models/*/artifacts/` is correctly ignored and should remain local-only.

## What is generated, redundant, stale, or misplaced

These items are not necessarily useless; they need clearer ownership.

### Disposable generated content

- `output/parsing/` is reproducible and ignored. That is appropriate.
- `output/retrieval/pipeline_baseline/` is reproducible and ignored. That is
  appropriate, but its six near-identical per-system result bundles account for
  roughly 35 MiB and should not be treated as repository content.
- `__pycache__/`, `*.pyc`, test caches, virtual environments, and temporary
  render data are disposable and already covered by ignore rules.

### Durable generated evidence in an ambiguous location

- `output/retrieval/reference/evaluation/retrieval_results.jsonl` is about
  8.64 MiB.
- `output/retrieval/experiments/question_metrics.jsonl` is about 4.29 MiB.
- Other tracked reference artifacts include embeddings, chunks, reports, and
  analytics.

If these files are release evidence, move them conceptually under a name such as
`artifacts/reference/` or `benchmarks/results/` and document the retention rule.
If they are only reproducible outputs, remove them from Git and publish checksums
or attach compressed bundles to releases. Keeping both policies under `output/`
makes relevance unclear.

### Overlapping or misplaced code

- `baseline.py` contains generic `sha256`, `read_jsonl`, `write_json`, and
  `write_jsonl` functions. Both `pipeline.py` and `experiments.py` import these
  helpers from the baseline workflow. They belong in a low-level artifact or I/O
  module.
- `DenseBiEncoderRetriever` in `pipeline.py` repeats the core matrix scoring and
  deterministic ranking responsibility already present in `ExactVectorIndex`.
  The index should accept a general encoder protocol, or both should delegate to
  one ranking implementation.
- `inspection.py` imports `IMPERATIVE_VERBS` from `structure.py`. Shared parsing
  rules should live in a small rules module instead of coupling inspection to
  reconstruction internals.
- `HashingBiEncoder` wraps `StableHashingEmbedder`. An adapter can be valid, but
  the naming and interfaces should make the legacy compatibility role explicit
  and avoid two apparent implementations of the same model.
- `scripts/build_golden_dataset.py` is a 539-line executable data declaration and
  processing pipeline. It should be split into curated question data, builder,
  validators, serializers/reporters, and a thin command.

### Documentation that needs role clarification

- `docs/architecture.md` documents the original flat parser/retrieval modules but
  does not inventory `pipeline.py`, `modeling/`, LSA, fusion, reranking, or the
  current model-store boundary.
- `docs/plan.md` is titled “Phase 1 Plan” while it also contains Phase 2A-2F.
  Rename it to a roadmap or split completed phase plans into an archive.
- `docs/review.md` is 850 lines and mixes current audit findings with historical
  evidence. Freeze dated reviews under `docs/reviews/` and maintain a short
  current status page.
- `docs/decisions.md` is 775 lines. Retain the decisions, but prefer one ADR file
  per decision under `docs/adr/` plus an index. This reduces merge conflicts and
  makes supersession explicit.
- `docs/progress.md` is a 334-line chronological log. Treat it as a changelog or
  archive rather than part of the current operating specification.
- `docs/runbook.md` is named as a project-wide runbook but remains parser-focused.
  Split it into parser, benchmark, retrieval, and experiment runbooks or expand
  the title to state its scope.

## Priority findings

### P0: remove package import side effects

`src/testrx_retriever/__init__.py` imports `parse_manual`, which imports
`pdfplumber`. As a result, importing `testrx_retriever.tokenization` or
`testrx_retriever.baseline_config` also imports the PDF stack.

The audit test run produced nine import errors before executing tests. Some were
caused by this environment not having declared dependencies installed, but the
cross-subsystem coupling is real: non-parser imports should not require the
parser dependency.

Recommended change:

- keep `__init__.py` limited to metadata such as `__version__`;
- import `parse_manual` from `testrx_retriever.parsing` explicitly; or
- expose it through a lazy wrapper only if backward compatibility requires the
  top-level symbol.

### P0: establish subsystem packages

The flat package makes ownership and dependency direction unclear. Parsing,
retrieval, evaluation, and workflow orchestration should not be peers in one
directory after the project has reached this size.

Recommended dependency direction:

```text
common/domain
    <- parsing
    <- datasets
    <- retrieval core
         <- evaluation
              <- experiments/workflows/CLI
```

Lower layers must not import workflow modules. CLI modules should be leaves.

### P1: unify artifact I/O and configuration contracts

Three config classes parse different path shapes and validate overlapping
fields independently. `PipelineConfig` does not retain its input
`schema_version`, while the baseline and sweep configs do. The workflow configs
also use different field layouts for the same document/dataset/output concepts.

Recommended change:

- define shared `InputPaths`, `ChunkingConfig`, `EvaluationConfig`, and artifact
  path resolution helpers;
- place workflow-specific config classes beside their workflows;
- validate schema versions explicitly;
- adopt one top-level JSON convention (`inputs`, `output`, `chunking`,
  `retrieval`, `evaluation`);
- add JSON Schema files only if external producers need to author configs.

### P1: resolve model naming collisions

Current meanings:

| Name | Actual meaning |
|---|---|
| `models.py` | Canonical parser/domain dataclasses |
| `modeling/` | Bi-encoder and reranker runtime implementations |
| `models/` | Local model registries and ignored weight stores |

Recommended names:

- `parsing/domain.py` or `parsing/entities.py` for current `models.py`;
- `retrieval/encoders/` and `retrieval/rerankers/` for current `modeling/`;
- `artifacts/models/` or `model_store/` for the top-level model store.

### P1: split oversized responsibility clusters

- `experiments.py` (576 lines): separate config expansion, diagnostics, runner,
  store persistence, and observation rendering.
- `structure.py` (507 lines): separate heading detection, element assembly,
  local grouping, and ownership/page-range resolution.
- `build_golden_dataset.py` (539 lines): move reusable logic into the package and
  curated records into a declarative data file or small domain-focused modules.

Line count alone is not the reason to split; each file contains multiple jobs
that change for different reasons.

### P1: define artifact retention classes

Use three explicit categories:

1. `data/source/`: immutable authoritative inputs.
2. `benchmarks/`: reviewed datasets and small fixtures that are versioned.
3. `artifacts/` or `runs/`: generated execution results, ignored by default,
   with a documented exception for frozen reference evidence.

Do not mix these under one generic `output/` name.

### P2: make tests mirror package boundaries

Current test names are understandable, but a flat test directory will become
harder to navigate as subsystem packages are introduced. Mirror the production
tree:

```text
tests/
  unit/parsing/
  unit/retrieval/
  unit/evaluation/
  integration/workflows/
  contract/artifacts/
```

Keep the PDF-based parser suite and full pipeline suite as integration tests.
Small config, tokenizer, scoring, and grouping tests should remain dependency-
light unit tests.

### P2: add standard engineering-tool configuration

`pyproject.toml` declares runtime and transformer dependencies but no development
extra and no lint, formatting, typing, coverage, or test-runner configuration.
For a Python 3.11+ project, add a documented development toolchain, for example:

- Ruff for formatting and linting;
- mypy or pyright for type checking;
- pytest plus coverage if richer fixtures/markers are needed, or retain
  `unittest` and configure coverage separately;
- pre-commit hooks and CI checks.

Choose tools intentionally; the organizational requirement is one canonical
local and CI quality command, not a specific brand.

## Recommended target structure

```text
testrx_retriever/
├── pyproject.toml
├── README.md
├── data/
│   └── source/
│       ├── TESTRX_User_Manual.pdf
│       └── manifest.md
├── benchmarks/
│   └── golden/
│       ├── questions.jsonl
│       ├── paraphrases.json
│       └── reports/
├── configs/
│   ├── reference/
│   ├── experiments/
│   └── pipelines/
├── model_store/
│   ├── encoders/
│   ├── rerankers/
│   └── generators/
├── artifacts/
│   ├── reference/          # version only by explicit policy
│   └── runs/               # ignored
├── docs/
│   ├── architecture/
│   ├── adr/
│   ├── runbooks/
│   ├── experiments/
│   ├── reviews/
│   └── archive/
├── scripts/
│   └── verify_golden_csv.mjs
├── src/testrx_retriever/
│   ├── __init__.py
│   ├── common/
│   │   ├── files.py
│   │   └── hashing.py
│   ├── parsing/
│   │   ├── domain.py
│   │   ├── parser.py
│   │   ├── normalization.py
│   │   ├── headings.py
│   │   ├── elements.py
│   │   ├── tables.py
│   │   ├── figures.py
│   │   ├── validation.py
│   │   ├── inspection.py
│   │   └── cli.py
│   ├── datasets/
│   │   ├── golden_builder.py
│   │   ├── paraphrases.py
│   │   ├── validation.py
│   │   └── reports.py
│   ├── retrieval/
│   │   ├── domain.py
│   │   ├── tokenization.py
│   │   ├── chunking.py
│   │   ├── encoders/
│   │   ├── indexes/
│   │   ├── fusion.py
│   │   └── rerankers/
│   ├── evaluation/
│   │   ├── metrics.py
│   │   ├── analysis.py
│   │   └── reports.py
│   ├── experiments/
│   │   ├── config.py
│   │   ├── diagnostics.py
│   │   ├── runner.py
│   │   └── store.py
│   └── workflows/
│       ├── reference_run.py
│       ├── model_comparison.py
│       └── cli.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/
```

This is a destination model, not a requirement to create every directory now.
Avoid empty future-facing packages. Introduce a directory only when it owns
working code or an active contract.

## Naming standard

Use names that state the business role rather than the implementation phase.

| Current name | Recommended direction | Reason |
|---|---|---|
| `source/` | `data/source/` | Avoid visual confusion with `src/` |
| `models.py` | `parsing/domain.py` | The file contains canonical entities, not ML models |
| `modeling/` | `retrieval/encoders/` and `retrieval/rerankers/` | State runtime roles directly |
| top-level `models/` | `model_store/` | State that it stores registries/artifacts |
| `baseline.py` | `workflows/reference_run.py` | “Baseline” is a status, not a responsibility |
| `pipeline.py` | `workflows/model_comparison.py` | It compares retrieval systems; it is not the entire product pipeline |
| `experiments.py` | `experiments/runner.py` | Distinguish orchestration from diagnostics and storage |
| `analytics.py` | `evaluation/analysis.py` | Name the analyzed domain |
| `inspection.py` | `parsing/inspection.py` | Make subsystem ownership explicit |
| `structure.py` | `headings.py` plus `elements.py` | Separate recognition from assembly/grouping |
| `output/` | `artifacts/` or `runs/` | Make generated status explicit |

Conventions:

- nouns for domain/value modules (`domain`, `metrics`, `config`);
- verb or job nouns for orchestration (`builder`, `runner`, `writer`);
- `cli.py` contains argument parsing only;
- avoid `utils.py`, `helpers.py`, `common.py`, and generic `models.py` unless the
  scope is made explicit by the containing package;
- one term per concept: choose `encoder` rather than alternating between
  `embedder`, `embedding model`, and `bi-encoder` when the interface is the same;
- distinguish configuration IDs, implementation algorithms, and user-facing
  system names in types and field names.

## Safe migration plan

### Stage 1: stabilize and measure

1. Install the declared development environment and get the existing suite
   green.
2. Add a test proving that importing tokenizer/config modules does not import
   `pdfplumber`.
3. Add characterization tests for artifact paths, hashes, config serialization,
   ranking tie-breaking, and CLI exit behavior.
4. Record the intended tracked-artifact policy in one short document.

### Stage 2: extract shared foundations

1. Move JSON/JSONL and checksum functions from `baseline.py` to
   `common/files.py`.
2. Move shared config records to narrowly scoped config modules.
3. Define common `Retriever`, `Encoder`, and `Reranker` protocols in the
   retrieval domain layer.
4. Make `ExactVectorIndex` encoder-agnostic and remove duplicate dense ranking
   logic from `pipeline.py`.

### Stage 3: form subsystem packages

1. Move parser modules under `parsing/` with compatibility re-exports.
2. Move retrieval primitives under `retrieval/`.
3. Move metrics/analytics/report rendering under `evaluation/`.
4. Split experiments and workflows last because they depend on all lower layers.
5. Update console entry points and imports, then remove compatibility shims in a
   later release.

### Stage 4: separate data and artifacts

1. Move authoritative source data and benchmark contracts first, updating paths
   in one compatibility-aware change.
2. Decide which generated evidence is versioned.
3. Move retained evidence to a clearly named durable location.
4. Keep ordinary run output ignored and add a cleanup command that targets only
   the explicit run directory.

### Stage 5: simplify documentation

1. Update the current architecture after code moves.
2. Convert decision entries to indexed ADRs without rewriting their history.
3. Archive completed plans/reviews/progress logs by date or phase.
4. Keep the README as a concise entry point and the runbooks as executable
   operational instructions.

## Acceptance criteria for the reorganization

The cleanup is complete when:

- importing a low-level subsystem does not load unrelated optional/runtime
  dependencies;
- every production module has one clear owning subsystem;
- workflow modules depend on core modules, never the reverse;
- exact ranking and artifact I/O each have one implementation;
- config files use one recognizable shape and validate schema versions;
- generated, benchmark, authoritative-source, and model-weight files have
  distinct locations and retention policies;
- test directories mirror the major production boundaries;
- the README and architecture map match the actual tree;
- one documented command runs formatting, linting, type checking, and tests;
- all existing artifact hashes and retrieval metrics remain unchanged unless a
  deliberate behavior change is separately approved.

## Overall assessment

The repository does not need broad deletion. Most content is relevant and the
domain intent is unusually well recorded. The required cleanup is primarily
about boundaries: turn the accumulated phase-oriented modules into stable
subsystems, separate durable evidence from disposable runs, remove naming
collisions, and compress historical documentation into indexed archives.

Recommended implementation order: package import isolation, shared I/O/config,
retrieval ranking deduplication, subsystem moves, artifact policy, then
documentation restructuring.
