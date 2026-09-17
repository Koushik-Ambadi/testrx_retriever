---
name: project-lifecycle-governance
description: Govern a software or data project across discovery, architecture, implementation, experiments, testing, documentation, decisions, progress, reproducibility, and clean Git delivery. Use when starting a project, planning a major phase, running comparative work, or maintaining project-wide engineering records; skip isolated edits that do not affect lifecycle contracts.
---

# Project Lifecycle Governance

Build projects whose code, evidence, reasoning, and history remain understandable
and reproducible after the immediate task is over. Adapt the ceremony to project
risk and size; do not scaffold empty processes or documents merely to satisfy a
template.

## Operating invariants

1. Inspect the repository, instructions, data authority, environment, Git state,
   and existing conventions before proposing structure or making changes.
2. Establish the factual source of truth and distinguish it from every derived
   representation, benchmark, metric, report, and narrative.
3. Convert the request into phase gates with explicit scope, exclusions,
   acceptance criteria, and stop conditions. Do not silently begin a later phase.
4. Create the simplest valid, measurable baseline before optimizing components.
5. Preserve comparability: freeze inputs, splits, evaluator semantics, controls,
   and unchanged components before varying one factor or component family.
6. Design reusable interfaces and configuration-driven workflows so the same
   pipeline can run across models, datasets, stages, and parameter grids.
7. Make every meaningful run reconstructable from code revision, input identity,
   resolved configuration, environment, component versions, random seeds,
   outputs, metrics, and checksums where justified.
8. Treat failure analysis, negative results, constraints, and interpretation
   boundaries as first-class evidence. Never select from one aggregate metric.
9. Give each fact one documentation owner. Update code, tests, schema, operations,
   decisions, roadmap, and progress in the same change when their contract moves.
10. Keep Git clean with small verified commits that tell the development story.
    Never discard unmerged or user-owned work to simplify history.

## Lifecycle routing

Read only the references needed for the current work:

- Starting, scoping, replanning, or closing a phase: read
  [references/lifecycle-and-gates.md](references/lifecycle-and-gates.md).
- Creating or reorganizing documents: read
  [references/documentation-ownership.md](references/documentation-ownership.md).
- Designing packages, modules, interfaces, or repository layout: read
  [references/architecture-and-code.md](references/architecture-and-code.md).
- Adding or changing verification: read
  [references/testing-and-quality.md](references/testing-and-quality.md).
- Building baselines, experiments, evaluations, or model/data comparisons: read
  [references/experiments-and-reproducibility.md](references/experiments-and-reproducibility.md).
- Recording decisions, challenges, progress, learnings, or retrospectives: read
  [references/decisions-progress-learning.md](references/decisions-progress-learning.md).
- Branching, committing, merging, releasing, or cleaning Git: read
  [references/git-and-delivery.md](references/git-and-delivery.md).
- Preserving material for later blogs, portfolios, or content analytics: read
  [references/knowledge-and-content-reuse.md](references/knowledge-and-content-reuse.md).
- Creating a concrete record: use the relevant form in
  [references/templates.md](references/templates.md).

## Default workflow

### 1. Discover

- Inventory files, dependencies, commands, data, generated artifacts, Git refs,
  active changes, and prior records.
- Read project instructions and the current architecture, roadmap, decisions,
  progress, limitations, testing strategy, and subsystem contracts when present.
- Identify uncertainty and ask only questions that materially change scope,
  authority, risk, or architecture.

### 2. Frame the next gate

Define:

- problem and user outcome;
- authoritative inputs and ownership;
- current state and evidence;
- in-scope and explicitly excluded work;
- proposed architecture boundary;
- acceptance tests and measurable outcomes;
- artifacts and records to retain;
- stopping condition and next-phase handoff.

If the user requests planning/approval before implementation, stop at the gate
and wait. Otherwise proceed within the authorized scope.

### 3. Characterize before refactoring

Protect current behavior with tests, hashes, schemas, representative fixtures,
or recorded metrics. Separate intended behavior from accidental behavior. When
moving files or responsibilities, prefer compatibility shims and incremental
migration over simultaneous redesign.

### 4. Implement reusable boundaries

- Separate domain logic, I/O, configuration, orchestration, evaluation, and CLI.
- Depend on small protocols or typed contracts across replaceable components.
- Put component selection and parameter grids in validated configuration.
- Avoid duplicated scoring, serialization, path resolution, or report logic.
- Make reruns safe: deterministic overwrite, content-addressed output, or
  explicit upsert semantics.

### 5. Verify proportionally

Run focused tests during development and full relevant verification before a
commit or phase close. Check both behavior and artifact contracts. Validate
failure paths, determinism, metadata completeness, stale files, and Git status.

### 6. Record the change

Update the one owning record for each changed fact:

- architecture for current structure;
- schema for fields/contracts;
- runbook for operations;
- testing guide for verification policy;
- decision record for a binding choice and alternatives;
- roadmap for active/future work;
- progress for completed, verified chronology;
- limitations for constraints that remain true;
- experiment record for fixed design, results, and interpretation boundary;
- generated report for exhaustive measurements.

Capture the problem, influence, alternatives, challenge, solution, impact, and
remaining uncertainty when they materially explain why the project evolved.

### 7. Deliver incrementally

Commit coherent verified layers such as implementation, tests, evidence/data,
and documentation. Use the repository owner's configured identity. Merge only
after verifying branch ancestry and preserve unmerged work. Push only when
authorized.

## Completion check

Before claiming completion, confirm:

- requested outcome and current gate are complete;
- relevant tests and quality checks pass;
- configuration and artifact schemas match implementation;
- runs can be reconstructed from stored metadata;
- docs contain no stale claims or duplicated owners;
- decisions, progress, limitations, and roadmap reflect the new state;
- temporary/generated material follows retention policy;
- Git worktree and branch state are intentional;
- final handoff states what changed, evidence, commit/ref, limitations, and next
  decision—not only files edited.

Do not create a new report for every task. Prefer updating the owning living
record or adding a dated frozen review only when a genuine review/audit occurred.
