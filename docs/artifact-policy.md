# Artifact retention policy

Status: living  
Owner: project architecture  
Last reviewed: 2026-09-29
Source of truth for: versioning and retention of source, benchmark, run, evidence,
and model artifacts

The repository distinguishes authored study material, generated metrics, full
reference bundles, and ordinary workflow runs. They have different owners and
retention rules; see [research synthesis](research-synthesis.md) for the
high-level evidence-to-decision path.

| Class | Current location | Versioned | Policy |
|---|---|---|---|
| Authoritative source | `source/` | Yes | Immutable input plus checksum manifest |
| Reviewed benchmark | `output/datasets/golden/` | Yes | Durable evaluation contract |
| Retrieval experiment design and frozen interpretation | `studies/retrieval/` | Yes | Versioned question, configuration, protocol, and findings per study |
| Pipeline experiment configuration and report | `configs/pipelines/` | Yes | Keep pipeline-specific run configuration beside its interpretation |
| Frozen research evidence | `output/retrieval/reference/`, `output/retrieval/experiment_store/` | Yes by explicit exception | Auditable reference and compact historical metrics |
| Ordinary runs | `output/parsing/`, `output/retrieval/pipeline_<purpose>/` | No | One isolated output root per workflow contract; reproducible and ignored |
| Model weights | `model_store/*/artifacts/` | No | Pinned by registry ID/revision; installed locally |

The legacy `source/` and durable `output/` paths are not moved in the current
compatibility stage because existing hashes, configs, and scripts are running.
A later data/artifact migration must update all paths in one characterized
change and prove that retrieval metrics and retained hashes remain unchanged.

The `pipeline_<purpose>/` folders separate the reference baseline, candidate
comparison, hierarchy matrix, production evaluation, and manual smoke workflow.
They keep full workflow artifacts isolated; the parameter-grid sweep instead
upserts normalized records into one `experiment_store/` to avoid a directory per
parameter combination.

## Retrieval output map

| Output directory | Producer/configuration | Responsibility |
|---|---|---|
| `output/retrieval/reference/` | `configs/retrieval/reference.json` | Designated full reference bundle with chunks, index, raw rankings, and evaluation |
| `output/retrieval/experiment_store/` | `studies/retrieval/*/experiment.json` | Shared normalized experiment, run, and question-level metrics; no full per-parameter bundles |
| `output/retrieval/pipeline_baseline/` | `configs/pipelines/baseline.json` | Engineering baseline comparison across configured retrieval systems |
| `output/retrieval/pipeline_candidates/` | `configs/pipelines/candidates.json` | Production encoder/fusion/reranker candidate comparison |
| `output/retrieval/pipeline_hierarchy_chunking/` | `configs/pipelines/hierarchical_chunking_experiment.json` | Eight-variant hierarchy/chunk-size matrix and timing capture |
| `output/retrieval/pipeline_production_evaluation/` | `configs/pipelines/production_evaluation.json` | Full configured evaluation of the selected production retriever |
| `output/retrieval/pipeline_manual_smoke/` | `scripts/manual_retrieval_smoke.py` | Small manually authored query/evidence inspection, separate from the golden benchmark |

The `pipeline_*` directories are separate because each workflow preserves a
different resolved configuration and artifact contract. They are not separate
copies of the compact parameter-grid store. Ordinary pipeline directories are
ignored by Git and can be recreated from the listed producer/configuration.
