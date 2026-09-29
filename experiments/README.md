# Experiment index

Status: living index
Owner: retrieval research
Last reviewed: 2026-09-29
Source of truth for: experiment design and result-record locations

Retrieval studies moved here from `configs/retrieval/experiments/`; each owns
its configuration and frozen interpretation together. Pipeline experiment
setups and their reports remain paired in `configs/pipelines/`. Shared runtime
and dataset defaults stay in `configs/`, and raw generated run artifacts stay
in `output/` under the retention policy.

## Retrieval studies

- [Chunk-size and hashing-dimension sweep](retrieval/chunk-dimension-sweep/results.md):
  [experiment definition](retrieval/chunk-dimension-sweep/experiment.json),
  fixed findings, diagnostics, and reproduction.
- [Paraphrase-bias baseline](retrieval/paraphrase-bias-baseline/results.md):
  [experiment definition](retrieval/paraphrase-bias-baseline/experiment.json),
  controlled paraphrase protocol, results, and interpretation.
- [Retrieval failure analysis](retrieval/failure-analysis.md): cross-study
  synthesis of persistent failure modes and the next discriminating work.

## Pipeline studies

- [Candidate-model comparison](../configs/pipelines/candidate-model-comparison.md)
  and [configuration](../configs/pipelines/candidates.json).
- [Hierarchical-chunking study](../configs/pipelines/hierarchical-chunking-experiment.md)
  and [configuration](../configs/pipelines/hierarchical_chunking_experiment.json).

## Ownership rules

- `experiment.json` owns the concrete study configuration and stable
  `experiment_id`.
- `results.md` owns the fixed protocol, interpretation, and links to raw output.
- `output/` owns generated run records, metrics, and artifacts; generated data is
  not copied into study configuration files.
- `configs/pipelines/` owns pipeline-specific configurations and their reports;
  shared runtime presets and dataset construction settings remain in `configs/`.
- Project-wide decisions and completed chronology remain in `docs/decisions.md`
  and `docs/progress.md`; experiment records link to them where appropriate.
