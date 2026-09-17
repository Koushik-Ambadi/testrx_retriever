# Experiments and Reproducibility

Use this guidance for model, data, retrieval, ranking, pipeline, or performance comparisons. The goal is not merely to produce a score; it is to produce evidence that another person can inspect and recreate.

## Define the experiment before running it

Record:

- the question being answered;
- the hypothesis and expected mechanism;
- the decision the result will inform;
- the primary metric and acceptance threshold;
- secondary and diagnostic metrics;
- controlled variables and intentionally changed variables;
- datasets, splits, slices, exclusions, and leakage controls;
- stopping, selection, and tie-breaking rules;
- resource, time, and cost limits.

Benchmark the simplest deterministic baseline before tuning. When comparing one component family, freeze the inputs, evaluator, splits, surrounding pipeline, and measurement boundary. If several families must change, run them as distinct stages so their effects remain attributable.

## Separate the layers of evidence

Do not collapse the following into one number:

- input or corpus coverage;
- candidate generation or retrieval recall;
- ranking or reranking quality;
- evidence coverage and faithfulness;
- end-task correctness;
- latency, throughput, cost, memory, and failure rate.

A reranker cannot recover an item that candidate generation omitted. Diagnose upstream coverage before interpreting downstream ranking metrics.

Use aggregate metrics together with meaningful slices, examples, and failure counts. Typical slices include source type, difficulty, length, domain, language, paraphrase level, and failure category.

## Run metadata contract

Every retained run should identify at least:

```yaml
experiment_id: stable-family-id
run_id: unique-run-id
started_at: ISO-8601 timestamp
code_revision: git-commit
command: exact invocation or workflow entry point
environment:
  runtime: version
  platform: value
inputs:
  dataset: name-and-version
  split: split-name
  manifests: [path-or-uri]
  checksums: {artifact: sha256}
components:
  model: {name: value, version: value, parameters: {}}
  pipeline: {name: value, version: value, parameters: {}}
randomness:
  seeds: [value]
measurement:
  timing_boundary: explicit-start-and-stop
  cache_policy: cold-warm-or-disabled
outputs:
  metrics: path-or-uri
  artifacts: [path-or-uri]
status: planned|running|completed|failed|invalidated
```

Add domain-specific fields, but do not silently remove provenance fields. Use stable identifiers rather than display names as join keys.

## Artifact organization

Keep authored experiment definitions separate from generated run outputs. A common pattern is:

```text
experiments/
  definitions/
  analysis/
runs/
  <experiment-id>/
    <run-id>/
      metadata.json
      metrics.json
      logs/
      artifacts/
```

Store repeated scalar results in a normalized table or metrics file. Avoid copying the same large payload into every run. If a full diagnostic artifact is expensive, designate a reference run and link other runs to it with content hashes.

Ordinary generated runs should usually be ignored by Git. Commit compact fixtures, schemas, manifests, summaries, and irreplaceable evidence; place large or regenerable artifacts in an artifact store, release, or data registry according to project policy.

## Long-running and expensive work

- Validate one small run end to end before launching the grid.
- Calculate expected row and artifact counts in advance.
- Make work resumable and idempotent.
- Save progress atomically at meaningful checkpoints.
- Record partial failure without presenting an incomplete grid as complete.
- Define cache isolation and warm-up behavior.
- Measure only the intended boundary.
- Preserve logs needed to distinguish code, data, infrastructure, and resource failures.

## Analysis and selection

Before drawing conclusions:

1. Validate schemas, row counts, identifiers, checksums, missingness, duplicates, and completion status.
2. Confirm comparability of inputs, code, evaluator, timing, and cache policy.
3. Inspect failures and negative results, not only winners.
4. Report uncertainty or variation when repeated runs are meaningful.
5. Apply the predeclared selection rule.
6. Confirm the selected option on a held-out set or independent scenario when the decision warrants it.

Treat invalid runs as evidence about the process, but exclude them transparently from performance claims. Never overwrite a prior run to make the chronology look cleaner.

## Reproduction checklist

A competent contributor should be able to locate:

- the immutable or versioned input;
- its checksum or manifest;
- the code revision;
- the exact configuration and command;
- dependency and hardware requirements where material;
- seeds and nondeterminism notes;
- raw logs and metrics;
- the analysis that transformed raw results;
- the decision or progress entry that consumed the evidence.

