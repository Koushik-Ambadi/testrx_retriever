# Artifact retention policy

Status: living  
Owner: project architecture  
Last reviewed: 2026-09-17  
Source of truth for: versioning and retention of source, benchmark, run, evidence,
and model artifacts

The repository distinguishes five artifact classes even where legacy paths are
temporarily retained for compatibility.

| Class | Current location | Versioned | Policy |
|---|---|---|---|
| Authoritative source | `source/` | Yes | Immutable input plus checksum manifest |
| Reviewed benchmark | `output/datasets/golden/` | Yes | Durable evaluation contract |
| Frozen research evidence | `output/retrieval/reference/`, `output/retrieval/experiments/` | Yes by explicit exception | Auditable reference and compact historical metrics |
| Ordinary runs | `output/parsing/`, `output/retrieval/pipeline_*` | No | Reproducible and ignored |
| Model weights | `model_store/*/artifacts/` | No | Pinned by registry ID/revision; installed locally |

The legacy `source/` and durable `output/` paths are not moved in the current
compatibility stage because existing hashes, configs, and scripts are running.
A later data/artifact migration must update all paths in one characterized
change and prove that retrieval metrics and retained hashes remain unchanged.
