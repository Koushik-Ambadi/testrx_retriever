# Documentation ownership

## Principle

Each fact has one authoritative document class. Other documents summarize and
link; they do not become competing sources of truth.

## Project-level records

Keep project-wide documents small and current:

- `README`: purpose, boundary, quick start, navigation, current state.
- architecture: current system boundaries, data flow, dependency direction.
- roadmap: active/future gates only.
- decisions/ADRs: binding choices, alternatives, consequences, supersession.
- progress/history: completed chronology and verification.
- research synthesis: concise cross-study conclusions and how evidence changed
  system/data choices and current direction.
- limitations: constraints that still apply across the project.
- artifact/retention policy: authority, generated data, evidence, caches, models.
- testing strategy: test levels, commands, dependencies, determinism policy.
- dated reviews: frozen audits, gate reviews, retrospectives.

Do not store exhaustive metrics, per-test results, detailed module APIs, or
generated reports in project-level docs.

The research synthesis is a navigation and interpretation layer, not another
results database: link to owned study reports and evidence, then to decisions,
implemented changes, and the next gate. Update it only when a finding materially
changes cross-study understanding or direction.

## Local records

Colocate details with their owner:

- module/subsystem behavior beside code;
- config rationale and experiment record beside configuration;
- schema beside the package/artifact contract;
- runbook beside the workflow it operates;
- source manifest beside immutable input;
- model/data card beside the model/dataset;
- generated reports beside the run that generated them.

One test strategy is normally enough. Add folder-level test documentation only
for unique fixtures, environments, or execution contracts. Prefer test names,
fixtures, docstrings, and assertions for individual behavior.

## Document states

Use explicit status:

- `living`: must describe the current system;
- `append-only`: history grows; old entries are not silently rewritten;
- `frozen`: point-in-time evidence; corrections use errata/resolution notes;
- `superseded`: retained with a link to the replacement;
- `generated`: produced by code; never manually edited.

Recommended authored metadata:

```markdown
Status: living | append-only | frozen | superseded
Owner: accountable role
Created: YYYY-MM-DD
Last reviewed: YYYY-MM-DD
Update trigger: event requiring review
Source of truth for: one responsibility
Does not own: neighboring concerns
Related: relative links
```

Generated records should identify generator, schema version, resolved run/input
identity, and a do-not-edit warning.

## Update triggers

- Boundary/dependency changes update architecture.
- Field or artifact changes update schemas and contract tests.
- Command/config/output changes update runbooks.
- Metric meaning changes update evaluation docs and invalidate comparisons unless
  versioned.
- A choice with tradeoffs updates a decision record.
- Completed verified work updates progress.
- Future sequencing updates roadmap.
- Resolved/new constraints update limitations.
- Experiment completion freezes its record and generated evidence.

## Anti-patterns

- one broad `docs/` folder containing every detail;
- a dated report called “current authoritative plan” indefinitely;
- copied metric tables across README, roadmap, decisions, and studies;
- resolved problems remaining in living limitations;
- future work duplicated in reports and roadmap;
- manually edited generated output;
- new audit files for ordinary edits;
- generic `notes.md`, `misc.md`, or `utils.md` with no owner.

## Documentation review

Periodically verify:

- links resolve;
- commands execute;
- filenames and locations match the repository;
- every document has a distinct owner and update trigger;
- living claims match current code;
- frozen records are clearly dated;
- generated files are distinguishable from authored guidance;
- duplicate facts have one canonical owner.
