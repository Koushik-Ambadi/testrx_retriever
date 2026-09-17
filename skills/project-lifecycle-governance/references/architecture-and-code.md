# Architecture, structure, and reusable code

## Boundary design

Separate concerns that change for different reasons:

- domain entities and invariants;
- adapters for external data/services/models;
- pure transformation/business logic;
- persistence and artifact I/O;
- configuration validation;
- orchestration/workflows;
- evaluation/observability;
- CLI/API/UI entry points.

Dependency direction should flow from stable domain/core layers toward
orchestration. Lower layers must not import workflows or CLIs. Entry points are
thin leaves.

## Replaceable components

When multiple models, datasets, strategies, or stages are expected:

- define a small protocol/typed contract;
- validate component configuration before expensive work;
- use stable component IDs separate from algorithm names and display labels;
- capture component version/revision, parameters, and preprocessing policy;
- keep evaluator and data contract independent of a concrete component;
- reuse one runner rather than copying one script per candidate.

Avoid premature abstraction for a single stable implementation. Extract a
boundary when two consumers need it, experiments require substitution, or the
responsibility already changes independently.

## Repository structure

Prefer role-revealing names and conventional locations. A typical shape may be:

```text
src/<package>/          production code
tests/                  verification
configs/                validated declarative run definitions
data/source/            immutable authoritative inputs
benchmarks/             reviewed durable evaluation contracts
model_store/            registries plus ignored local weights
artifacts/ or output/   generated evidence and ordinary runs
docs/                   project-wide governance only
skills/                 reusable workflow skills
scripts/                thin maintenance/build entry points
```

Adapt to language/ecosystem and do not create empty future directories.

## Naming

- Name modules for responsibility, not phase or status (`reference_run` instead
  of ambiguous `baseline` when the status may change).
- Avoid collisions such as `models.py`, `modeling/`, and `models/` for unrelated
  concepts.
- Use one term per concept across types, configs, metrics, and docs.
- Distinguish source data, benchmark data, generated runs, and durable evidence.
- Use standard ecosystem conventions for code and consistent kebab/snake case
  for documents/configs as appropriate.

## Reuse and rerun safety

- Extract common I/O, hashing, path resolution, scoring, and reporting instead
  of importing helpers from a high-level workflow.
- Make writes atomic when interruption would corrupt shared state.
- Define overwrite, append, and upsert semantics explicitly.
- Use deterministic ordering and stable IDs; do not use timestamps/random UUIDs
  for reproducible content identity.
- Preserve backward compatibility with explicit shims during migration, and set
  a removal condition/version rather than keeping duplicate APIs indefinitely.

## Refactoring

Before moving code:

1. characterize behavior and artifacts;
2. map imports and consumers;
3. move one responsibility at a time;
4. keep compatibility imports if callers cannot migrate atomically;
5. update tests/docs/config paths together;
6. prove outputs/metrics/hashes unchanged unless behavior change is intentional;
7. remove shims only after their consumers and deprecation window are clear.

Line count is a signal, not a rule. Split when a file owns multiple change
reasons: configuration, execution, diagnostics, persistence, and reporting are
common separable clusters.
