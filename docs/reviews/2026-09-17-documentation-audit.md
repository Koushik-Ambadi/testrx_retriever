# Documentation governance audit

Date: 2026-09-17  
Status: frozen point-in-time review  
Scope: every tracked Markdown file plus visible ignored/generated Markdown  
Author evidence: Git history records `Codex` as the author/committer of every
tracked Markdown document. “Why” below is inferred from the creation commit and
the document's content; Git cannot establish the human sponsor or business owner.

Resolution: the 2026-09-17 documentation reorganization implemented the primary
recommendations. Current ownership and locations are indexed in
`docs/README.md`; paths below describe the pre-reorganization state audited here.

## Executive assessment

The repository has strong documentation coverage but weak document governance.
It records architecture, decisions, plans, progress, schemas, operations,
limitations, experiment evidence, generated reports, source provenance, and
model-store behavior. Those are the right perspectives. The main problem is
that living specifications, historical records, generated evidence, and dated
reviews are stored together without consistent status metadata or update rules.

There are 32 tracked Markdown files and 45 additional visible Markdown files
that are ignored. The ignored files are generated run reports, generated parser
views, hierarchy summaries, or third-party model cards. They are not missing
project documentation and should not be merged into authored documents.

The core project-level documents were updated with the latest code milestone on
2026-09-15: `README.md`, `architecture.md`, `decisions.md`, `plan.md`,
`progress.md`, and `full_pipeline.md`. However, the update was incomplete.
Several statements in living documents still describe the system before model
comparison and hierarchical chunking were implemented.

Recommended outcome:

1. Keep the perspectives, but assign every document one type: living
   specification, living operation guide, append-only decision/history,
   frozen review/study, or generated evidence.
2. Update six stale living documents immediately.
3. Split the oversized schema, runbook, review, and decision collections by
   independently changing responsibility.
4. Freeze dated program reports and audits under `docs/reviews/` rather than
   treating them as current truth.
5. Add one project-level testing guide. Do not create one Markdown file per test
   or per Python module.

## Current documentation model

The current repository already contains these useful views:

| View | Current source | Correct responsibility |
|---|---|---|
| Project entry point | `README.md` | Current purpose, boundary, quick start, navigation |
| Architecture | `docs/architecture.md` | Current subsystem boundaries and dependency direction |
| Decisions | `docs/decisions.md` | Accepted/superseded decisions and rationale |
| Roadmap | `docs/plan.md` | Current and future gates, not detailed history |
| Progress/history | `docs/progress.md` | Chronological completed work and verification |
| Operations | `docs/runbook.md` | Repeatable commands, failure handling, release/freeze gates |
| Contracts | `docs/schema.md` | Stable field and artifact schemas |
| Current limitations | `docs/limitations.md` | Active cross-project constraints only |
| Subsystem rationale | `golden_dataset.md`, `baseline_retrieval.md`, `full_pipeline.md`, `analytics.md` | Why and how a subsystem works |
| Experiment evidence | `docs/experiments/*.md` | Fixed design, measured results, interpretation boundary |
| Point-in-time reviews | `review.md`, `retrieval_program_report.md`, organization audit | Dated evidence, not continuously rewritten truth |
| Retention policy | `docs/artifact_policy.md` | What is versioned, generated, ignored, or immutable |
| Adjacent manifests | `source/README.md`, `model_store/**/README.md` | Rules specific to the containing directory |
| Generated evidence | `output/**/*.md` | Reproducible machine output; never hand-maintained |

This is a good conceptual model. The changes below make each responsibility
exclusive enough that documents complement rather than contradict one another.

## Creation and maintenance history

All tracked Markdown files show `Codex` as their Git author. No document records
a durable human or team owner. Creation dates below are the earliest commit in
the file's history. “Last update” is the latest commit touching that path.

### Project and subsystem documents

| File | Created | Last update | Why it was created | Current action |
|---|---|---|---|---|
| `README.md` | 2026-09-09 | 2026-09-15 | Establish the validated parser/project entry point | Keep living; update repository map and authority wording |
| `docs/analytics.md` | 2026-09-12 | 2026-09-12 | Document reusable retrieval analytics and filters | Keep; update stale supported-component statement |
| `docs/architecture.md` | 2026-09-09 | 2026-09-15 | Record data flow, responsibilities, and boundaries | Keep living; reconcile legacy inventory and phase state |
| `docs/artifact_policy.md` | 2026-09-15 | 2026-09-15 | Define source, benchmark, evidence, run, and weight retention | Keep; fix its “four classes” count because the table has five |
| `docs/baseline_retrieval.md` | 2026-09-11 | 2026-09-12 | Freeze baseline design, metrics, and artifact layout | Keep as frozen reference; add date/status |
| `docs/decisions.md` | 2026-09-09 | 2026-09-15 | Preserve accepted and superseded project decisions | Keep append-only; split or index by domain |
| `docs/full_pipeline.md` | 2026-09-15 | 2026-09-15 | Explain runnable model comparison and hierarchy experiment path | Keep as retrieval subsystem guide; clarify it is not parser-to-generation E2E |
| `docs/golden_dataset.md` | 2026-09-09 | 2026-09-12 | Define benchmark authority, lineage, and lifecycle | Keep; move changing counts/results to generated report |
| `docs/limitations.md` | 2026-09-09 | 2026-09-12 | Track known limitations and deferred work | Keep living; remove resolved/study-specific duplication and update stale items |
| `docs/plan.md` | 2026-09-09 | 2026-09-15 | Define Phase 1 work, later extended through Phase 2F | Rename to roadmap; archive completed phase detail |
| `docs/progress.md` | 2026-09-09 | 2026-09-15 | Record chronological implementation and verification | Keep append-only as history; do not use for current contracts |
| `docs/repository_organization_audit.md` | content dated 2026-09-13; committed 2026-09-15 | 2026-09-15 | Audit repository layout and propose migration | Move/freeze under dated reviews; add resolution status because several recommendations are already implemented |
| `docs/retrieval_program_report.md` | 2026-09-15 | 2026-09-15 | Synthesize current retrieval evidence and next design | Freeze as dated program review; move live actions to roadmap |
| `docs/review.md` | 2026-09-09 | 2026-09-12 | Store parser audit and later phase gate reviews | Split into dated review files; do not present as one current review |
| `docs/runbook.md` | 2026-09-09 | 2026-09-12 | Provide parser and later retrieval operating procedures | Split by workflow and add candidate/hierarchy operations |
| `docs/schema.md` | 2026-09-09 | 2026-09-12 | Define canonical, benchmark, retrieval, and experiment records | Split by contract; add newer pipeline/hierarchy artifacts |

Two documents were backfilled: `repository_organization_audit.md` is dated
2026-09-13 but first appears in Git on 2026-09-15, and
`production_model_comparison.md` is dated 2026-09-13 but was committed on
2026-09-15. This is not inherently wrong, but both “event date” and “recorded
date” should be explicit for audit-quality history.

### Experiment documents

| File | Created | Last update | Why it was created | Current action |
|---|---|---|---|---|
| `docs/experiments/README.md` | 2026-09-12 | 2026-09-15 | Define experiment documentation/storage conventions | Keep as index; add production model comparison and correct config locations |
| `chunk_dimension_study.md` | 2026-09-12 | 2026-09-12 | Record token-window and hash-dimension study | Keep frozen |
| `failure_decision_report.md` | 2026-09-12 | 2026-09-12 | Analyze failures and choose the next experiment | Keep frozen; link canonical decisions rather than duplicate them |
| `paraphrase_bias_study.md` | 2026-09-12 | 2026-09-12 | Record controlled paraphrase stress study | Keep frozen |
| `production_model_comparison.md` | content dated 2026-09-13; committed 2026-09-15 | 2026-09-15 | Compare BGE, E5, hybrid retrieval, and MiniLM reranking | Keep frozen; add recorded date/status |
| `hierarchical_chunking.md` | 2026-09-15 | 2026-09-15 | Record hierarchy chunker design and raw experiment contract | Keep; status already clearly says analysis is deferred |

These files are correctly separated by experiment. Do not merge them into one
large retrieval document. Each has a distinct fixed configuration and evidence
boundary. A short index should connect them in chronological order and identify
the decision produced by each.

### Adjacent source and model-store documentation

| File | Created | Last update | Why it was created | Current action |
|---|---|---|---|---|
| `source/README.md` | 2026-09-09 | 2026-09-09 | Preserve source identity, checksum, and immutability policy | Keep adjacent; update only when source changes |
| `model_store/README.md` | 2026-09-15 | 2026-09-15 | Define runtime-role-separated model storage | Keep adjacent |
| `model_store/encoders/README.md` | 2026-09-15 | 2026-09-15 | Explain first-stage encoder artifacts | Keep; small duplication is justified by directory locality |
| `model_store/rerankers/README.md` | 2026-09-15 | 2026-09-15 | Explain pairwise reranker artifacts | Keep |
| `model_store/generators/README.md` | 2026-09-15 | 2026-09-15 | Reserve and constrain the future generator store | Keep only while the empty directory is intentionally part of the architecture |

The three six-line role READMEs could be merged into the parent README, but that
would make each artifact directory less self-describing. Their small, local
repetition is beneficial and should remain.

### Tracked generated reports

| File | First tracked | Last update | Generator purpose | Current action |
|---|---|---|---|---|
| `output/datasets/golden/golden_dataset_report.md` | 2026-09-12 | 2026-09-12 | Generated dataset distribution summary | Keep generated/versioned under artifact policy |
| `output/datasets/golden/quality_control_report.md` | 2026-09-12 | 2026-09-12 | Generated QC warnings and review candidates | Keep separate; it answers a different question |
| `output/datasets/golden/source_coverage_report.md` | 2026-09-12 | 2026-09-12 | Generated section/element coverage | Keep separate |
| `output/retrieval/reference/evaluation/retrieval_analytics.md` | 2026-09-12 | 2026-09-12 | Generated compact slice summary | Keep separate from detailed results |
| `output/retrieval/reference/evaluation/retrieval_report.md` | 2026-09-12 | 2026-09-12 | Generated per-question reference report | Keep generated; never duplicate it manually |

These reports were committed by Codex but should identify their generating
command/module, input hashes, and “do not edit” status. The golden reports are
three complementary projections, not redundant copies. The retrieval analytics
and detailed report are summary/detail views and should also remain separate.

## Ignored Markdown is not authored documentation

Forty-five visible Markdown files are ignored by Git. They fall into four
classes:

1. `output/parsing/semantic_structure.md`: generated human-readable parse view.
2. `output/retrieval/pipeline_*/**/*.md`: generated model/category and hierarchy
   run reports.
3. Repeated hierarchy `summary.md` files: one generated summary per configured
   variant.
4. `model_store/*/artifacts/**/README.md`: downloaded third-party model cards.

Do not merge or manually curate these files. They should be regenerated or
reinstalled with their owning artifact. They may be referenced by a dated study,
but they are not sources of current project policy.

## Redundancy findings

### R1: the same metric values are copied into too many authored documents

Baseline and candidate metrics appear in combinations of `README.md`,
`baseline_retrieval.md`, experiment studies, `retrieval_program_report.md`, and
generated output reports. A concise summary is useful, but each copied number
creates another update obligation.

Policy:

- generated report owns exhaustive numbers;
- experiment document owns the minimal table required to support its conclusion;
- decision log owns the decision, not another metrics table;
- README owns only current status and links;
- roadmap owns no measured results.

### R2: future work exists in both `plan.md` and `retrieval_program_report.md`

The program report contains a staged plan, gates, actions, fallbacks, and stop
conditions while `plan.md` is the nominal work plan. Freeze the report as the
evidence snapshot and move its still-active actions into one living
`roadmap.md`.

### R3: limitations are repeated in study documents and `limitations.md`

Study-specific threats to validity belong in the frozen study. The living
limitations document should contain only constraints that remain true for the
current project. This prevents resolved items such as “learned embeddings and
reranking are pending” from surviving after implementation.

### R4: decisions are repeated as study conclusions

It is correct for a study to state what its evidence supports. The binding
project decision should exist once in `decisions.md`/an ADR. Experiment files
should link the decision ID, and decision records should link the evidence.

### R5: operational commands are scattered

README quick-start commands, subsystem-specific reproduction commands, and a
central runbook can coexist if their scopes are explicit:

- README: shortest happy path;
- runbook: supported operational procedures and troubleshooting;
- experiment file: exact reproduction command for that frozen study.

Avoid repeating installation and generic test instructions in every document.

## Stale or internally inconsistent living documents

### Immediate updates required

1. `docs/analytics.md` says the current implementation supports only token
   windows, lexical hashing, exact cosine retrieval, and no reranking. The code
   now includes hierarchical chunking, BGE/E5-compatible sentence-transformer
   encoders, fusion, and reranking.
2. `docs/architecture.md` says advanced chunking and retrieval are future phases
   and its responsibility list still foregrounds legacy flat modules. Its new
   subsystem inventory and old phase text contradict one another.
3. `docs/limitations.md` lists learned embeddings and reranking as deliberately
   pending even though production candidate comparison is complete. It also
   repeats historical study limitations that belong in dated studies.
4. `docs/runbook.md` stops at the paraphrase analytics workflow. It lacks model
   candidate installation/comparison and hierarchical experiment operations.
5. `docs/schema.md` stops at the shared experiment store. It does not describe
   model-comparison summaries, hierarchy nodes/statistics, latency records, or
   newer pipeline output contracts.
6. `docs/experiments/README.md` does not list
   `production_model_comparison.md` and still states that experiment configs
   belong only under `configs/retrieval/experiments/`, while newer controlled
   runs use `configs/pipelines/`.

### Lower-priority corrections

- `README.md` describes `configs/retrieval/` as the whole configuration area,
  omitting `configs/pipelines/`. Its source-tree description also understates the
  new retrieval/evaluation/workflow packages.
- `docs/artifact_policy.md` says “four artifact classes” but lists five.
- `docs/full_pipeline.md` uses “end-to-end,” although the project explicitly
  excludes answer generation. Rename it “retrieval pipeline” or define the exact
  endpoints in the title.
- `docs/baseline_retrieval.md` is a historical anchor but lacks explicit
  `Status: frozen reference` metadata.
- `docs/review.md` was last updated before production-model and hierarchy work.
  It should not be described as the current project review.
- `docs/retrieval_program_report.md` is called “authoritative current retrieval
  evidence” in README. A dated report cannot safely be both frozen evidence and
  permanent current authority. Make current decisions/roadmap authoritative and
  label the report as a snapshot.
- Authored documents use backtick paths but no navigable Markdown links. An index
  with actual relative links would improve discoverability and allow link
  checking in CI.

## Merge, split, keep, and archive recommendations

### Keep separate

- Architecture, decisions, roadmap, progress, runbooks, schemas, limitations,
  and artifact policy: each answers a materially different question.
- Golden dataset, baseline retrieval, pipeline, and analytics subsystem guides.
- One document per experiment.
- Generated dataset summary, QC, and coverage reports.
- Parent and role-specific model-store READMEs.
- Source manifest beside the source file.

### Merge or consolidate

- Consolidate all active future work into `docs/roadmap.md`; remove duplicate
  live actions from the dated retrieval program report.
- Consolidate the documentation catalog and ownership metadata in
  `docs/README.md`. The root README should show only the shortest documentation
  map.
- Consolidate current cross-project limitations in one living limitations file;
  retain study-specific caveats only in study files.

### Split

- Split `docs/runbook.md` into:
  - `docs/runbooks/parsing.md`
  - `docs/runbooks/golden_dataset.md`
  - `docs/runbooks/retrieval.md`
  - `docs/runbooks/experiments.md`
- Split `docs/schema.md` into:
  - `docs/schemas/canonical_document.md`
  - `docs/schemas/golden_dataset.md`
  - `docs/schemas/retrieval_artifacts.md`
  - `docs/schemas/experiment_store.md`
- Split `docs/review.md` into immutable dated reviews under `docs/reviews/`.
- Split `docs/decisions.md` into indexed ADRs by decision only if the team is
  ready to preserve IDs and links. Until then, add a domain/status index at the
  top instead of performing a risky mechanical split.
- Split completed phases out of `plan.md`; keep them in
  `docs/history/phase-plans/` and leave active gates in `roadmap.md`.

### Archive or reclassify

- Move `repository_organization_audit.md` to a dated review and record which
  recommendations were resolved by the modularization commit.
- Move `retrieval_program_report.md` to a dated program-review path once its
  active actions are represented in the roadmap.
- Treat `progress.md` as append-only history, not a current design source.
- Treat `baseline_retrieval.md` as a frozen characterization baseline.

## Test-level and module-level documentation

### Tests

There is no test-level Markdown documentation today. That is acceptable and
preferable to one document per test file. Individual tests should explain their
intent through names, fixtures, docstrings where necessary, and assertions.

Add one project-level `docs/testing.md` because the suite now spans different
cost and dependency levels. It should own:

- unit, integration, contract, and slow/model-test definitions;
- the canonical local and CI commands;
- required versus optional dependencies;
- test data and fixture ownership;
- network/download policy;
- generated-output and temporary-directory behavior;
- determinism expectations;
- how to add tests for a new encoder, reranker, chunker, schema, or workflow.

If test directories are later split into `unit/`, `integration/`, and
`contract/`, this guide should explain the taxonomy. Do not add READMEs to each
test folder unless a folder has a unique setup or fixture contract.

### Python modules

There is no need for one Markdown file per Python module. Module docstrings and
API/type documentation are the correct level for implementation details.
Markdown should exist at subsystem level only when it explains concepts that
span modules or are needed by operators/reviewers.

Recommended subsystem documentation:

- parsing architecture and canonical-data rationale;
- retrieval pipeline and component protocols;
- evaluation metric semantics;
- experiment conventions;
- workflow/runbook operations.

The existing `architecture.md`, `full_pipeline.md`, `analytics.md`, schema files,
and experiment index can cover these needs after their responsibilities are
tightened.

## Required metadata for authored documents

Use this header for every authored living, frozen, or append-only document:

```markdown
# Title

Status: living | append-only | frozen | superseded
Owner: project role or team
Created: YYYY-MM-DD
Last reviewed: YYYY-MM-DD
Update trigger: event that requires review
Source of truth for: one sentence
Does not own: neighboring concerns
Related: relative Markdown links
```

Generated documents should instead state:

```markdown
Generated: do not edit
Generator: module or command
Generated at/from: deterministic run identity or input hashes
Schema version: ...
```

Use an owner role such as “retrieval evaluation,” “parser,” or “benchmark
governance,” not `Codex`. Git author answers who typed/committed the text; it
does not answer who is accountable for keeping it correct.

## Proposed documentation tree

```text
docs/
├── README.md                       documentation catalog and ownership
├── architecture.md                current project architecture overview
├── roadmap.md                     only active and future gates
├── limitations.md                 only active project-wide limitations
├── artifact_policy.md             retention and generated-data policy
├── testing.md                     suite taxonomy and commands
├── adr/
│   ├── README.md                  decision index
│   └── 00xx-*.md                  one immutable decision each
├── schemas/
│   ├── canonical_document.md
│   ├── golden_dataset.md
│   ├── retrieval_artifacts.md
│   └── experiment_store.md
├── runbooks/
│   ├── parsing.md
│   ├── golden_dataset.md
│   ├── retrieval.md
│   └── experiments.md
├── subsystems/
│   ├── golden_dataset.md
│   ├── baseline_retrieval.md
│   ├── retrieval_pipeline.md
│   └── analytics.md
├── experiments/
│   ├── README.md
│   └── <one dated/fixed study per file>
├── reviews/
│   ├── 2026-09-03-parser-review.md
│   ├── 2026-09-13-repository-organization-audit.md
│   ├── 2026-09-15-retrieval-program-review.md
│   └── 2026-09-17-documentation-audit.md
└── history/
    ├── progress.md
    └── phase-plans/
```

This tree is a responsibility model, not a request to move everything at once.
Preserve Git history with `git mv`, update references in the same change, and
avoid creating empty directories or placeholder documents.

## Update cadence and ownership rules

| Document type | Update rule |
|---|---|
| README | Review on every user-visible capability, command, or top-level tree change |
| Architecture | Review on subsystem/dependency/artifact-flow changes |
| ADR/decisions | Append when a material choice is made; never rewrite history silently |
| Roadmap | Update when a gate starts, changes, completes, or is abandoned |
| Progress/history | Append only after verified milestones |
| Limitations | Review when a limitation is added, resolved, or materially narrowed |
| Schema | Update in the same commit as a contract change |
| Runbook | Validate commands in the same commit as CLI/config/output changes |
| Experiment study | Freeze after conclusion; corrections receive an erratum |
| Review/audit | Freeze; add resolution links instead of rewriting findings |
| Generated report | Regenerate only through its owning command |
| Adjacent README | Review when the containing directory's contract changes |

Add a pull-request or commit checklist:

- Does this change alter a command, config shape, artifact, metric, or boundary?
- Which living document owns that fact?
- Does an ADR need to record the choice?
- Does a runbook command still execute?
- Is a generated report being edited manually?
- Is a point-in-time report being mistaken for current authority?

## Recommended action order

### P0: correctness

1. Update `analytics.md`, `architecture.md`, `limitations.md`, `runbook.md`,
   `schema.md`, and `experiments/README.md` for the current model/hierarchy code.
2. Correct the README repository/config map and remove “authoritative current”
   wording from the dated retrieval program report entry.
3. Fix the artifact-class count.

### P1: governance

1. Add `docs/README.md` with document type, owner, status, source-of-truth scope,
   update trigger, and links.
2. Add metadata headers to authored docs.
3. Add `docs/testing.md`.
4. Mark generated Markdown with generator identity and do-not-edit metadata.

### P2: structural cleanup

1. Split runbooks and schemas.
2. Reclassify audits/program reports as dated reviews.
3. Convert `plan.md` into a living roadmap and archive completed phase plans.
4. Split or index decisions and reviews while preserving identifiers/history.

### P3: enforcement

1. Add a documentation check that verifies local links and required metadata.
2. Add tests or smoke commands for runbook commands/config paths.
3. Optionally fail CI when generated tracked reports do not match regeneration.

## Final recommendation

Do not merge the documentation into fewer broad files. The multiple points of
view are appropriate for this research/engineering project. Instead, reduce
redundancy by assigning one owner for each fact:

- architecture owns structure;
- schemas own fields;
- runbooks own operations;
- decisions own choices;
- roadmap owns future work;
- progress owns completed chronology;
- limitations own only current constraints;
- studies own fixed evidence and interpretation;
- generated reports own exhaustive measurements.

The immediate risk is stale living documentation, not excessive document count.
Fix the six contradictions first, then introduce metadata and a documentation
index before performing larger file moves.
