# Project documentation

Status: living index  
Owner: project architecture  
Created: 2026-09-17  
Last reviewed: 2026-09-29
Source of truth for: documentation ownership and navigation

`docs/` contains project-wide information only. Subsystem implementation guides,
schemas, runbooks, benchmark descriptions, and experiment records live beside
the code, configuration, or durable artifact they describe. Generated Markdown
under `output/` is evidence and must not be edited manually.

## Living project documents

- [Architecture](architecture.md): current subsystem boundaries, data flow, and
  dependency direction.
- [Roadmap](roadmap.md): active gates, sequencing, and future work.
- [Limitations](limitations.md): constraints that remain true across the current
  project.
- [Artifact policy](artifact-policy.md): source, benchmark, evidence, run, and
  model-weight retention.
- [Testing](testing.md): test levels, dependencies, commands, and extension rules.

## Append-only project records

- [Decisions](decisions.md): accepted and superseded choices with rationale.
- [Progress](progress.md): chronological implementation and verification history.

## Frozen reviews

`reviews/` contains dated audits and program reviews. Review files are historical
evidence. Correct factual errors with an explicit erratum or resolution note;
do not silently make an old review describe the current repository.

- [Project review history](reviews/2026-09-12-project-review-history.md)
- [Repository organization audit](reviews/2026-09-13-repository-organization-audit.md)
- [Retrieval program review](reviews/2026-09-15-retrieval-program-review.md)
- [Documentation governance audit](reviews/2026-09-17-documentation-audit.md)

## Subsystem and artifact documentation

- [Parsing subsystem](../src/testrx_retriever/parsing/README.md)
- [Package schemas](../src/testrx_retriever/SCHEMA.md)
- [Retrieval baseline](../src/testrx_retriever/retrieval/baseline.md)
- [Evaluation analytics](../src/testrx_retriever/evaluation/analytics.md)
- [Retrieval pipeline](../src/testrx_retriever/workflows/retrieval-pipeline.md)
- [Workflow runbook](../src/testrx_retriever/workflows/runbook.md)
- [Golden dataset](../output/datasets/golden/README.md)
- [Experiment index](../experiments/README.md)
- [Candidate model comparison](../configs/pipelines/candidate-model-comparison.md)
- [Hierarchy experiment](../configs/pipelines/hierarchical-chunking-experiment.md)
- [Frozen retrieval configuration](../configs/retrieval/production.md)
- [Source manifest](../source/README.md)
- [Model store](../model_store/README.md)
- [Reusable project lifecycle skill](../skills/project-lifecycle-governance/SKILL.md)

## Ownership rules

- Architecture owns structure; schemas own fields; runbooks own operations.
- Decisions own binding choices; roadmap owns future work; progress owns completed
  chronology.
- Limitations owns only current cross-project constraints.
- Experiment files own fixed designs, measurements, and interpretation limits.
- Generated reports own exhaustive results.
- README files adjacent to a directory own that directory's local contract.

Review the owning document in the same change whenever code alters a command,
configuration shape, artifact schema, metric definition, subsystem boundary, or
retention rule.
