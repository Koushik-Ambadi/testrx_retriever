# Testing and quality

## Test layers

- Unit: deterministic logic and boundary validation with small inputs.
- Integration: multiple real components, filesystem/database/service adapters,
  and workflow outputs.
- Contract: schemas, stable IDs, manifests, API/component protocols, import
  isolation, compatibility, and reproducibility.
- End-to-end: the supported user or batch path across deployed boundaries.
- Model/data evaluation: statistical quality, slices, robustness, and regression
  thresholds; do not confuse with unit correctness.

Use the smallest layer that proves the claim. Keep default tests fast/local;
mark or separate expensive, hardware, network, and model-backed suites.

## Before implementation

Define acceptance evidence before coding:

- representative happy paths;
- edge/failure cases;
- invariants and contracts;
- performance/latency boundaries if relevant;
- determinism and reproducibility expectations;
- compatibility behavior;
- manual review criteria for inherently subjective results.

For refactors, add characterization tests first. For bugs, reproduce the failure
before fixing it when practical.

## Data/model systems

Test separately:

- data identity, schema, ranges, missingness, leakage, and lineage;
- preprocessing equivalence between fit/index/query/inference stages;
- split/grouping invariants;
- model/component configuration and unavailable artifact behavior;
- candidate generation before reranking or downstream selection;
- metric correctness with hand-checkable examples;
- deterministic tie-breaking and seed handling;
- empty, partial, duplicate, and malformed inputs;
- saved artifact reload and environment compatibility.

## Quality gates

Before commit or merge, use the project-appropriate subset:

- formatter/linter;
- static/type checks;
- focused and full relevant tests;
- build/package/import smoke test;
- schema/config validation;
- artifact regeneration or manifest verification;
- documentation link/command checks;
- security/license/dependency checks where risk warrants;
- clean Git diff and status.

Never report a suite as passing if it did not execute because dependencies were
missing. Distinguish environment/setup failures from product failures.

## Test documentation

Maintain one project testing strategy covering levels, commands, dependencies,
fixtures, network/download policy, determinism, and extension rules. Do not add
one Markdown document per test/module unless unique setup makes it necessary.

## Failure handling

When verification fails:

1. preserve the exact command/environment;
2. classify setup, deterministic product defect, flaky behavior, data defect, or
   expectation defect;
3. reduce to the smallest reproducible case;
4. record the root cause and why the chosen fix addresses it;
5. add regression protection;
6. rerun affected higher-level gates;
7. update limitations or decisions if the contract changes.
