# Lifecycle and gates

## Project start

Begin with evidence, not scaffolding.

1. Inventory the repository, data, tools, constraints, licenses, secrets, and
   Git state.
2. Identify stakeholders, users, owner roles, and the intended decision or
   product outcome.
3. Declare authoritative inputs and preservation rules. Record identity with a
   checksum/version when derived outputs must be auditable.
4. Separate facts already known from assumptions and questions.
5. Define the smallest phase that produces independently verifiable value.

Do not design later phases in implementation detail before earlier contracts
are measured. Record likely future boundaries only when they constrain current
choices.

## Gate contract

Every material phase should have:

- objective and decision enabled by the phase;
- inputs and their authority;
- included and excluded capabilities;
- implementation boundary and dependencies;
- outputs and retention class;
- acceptance criteria and tests;
- human review or approval requirement, if any;
- stop condition;
- handoff to the next gate.

Examples of useful gates:

- source ingestion before transformation;
- canonical representation before downstream modeling;
- benchmark before optimization;
- simple baseline before component comparison;
- candidate coverage before reranking;
- retrieval freeze before generation;
- generation/evaluation before UI and telemetry.

These are patterns, not mandatory phases. Choose gates that isolate uncertainty
and prevent downstream work from hiding upstream failures.

## Change control

When scope changes:

1. State the new evidence or requirement.
2. Identify which current assumption or decision it invalidates.
3. Estimate affected contracts, artifacts, tests, and history.
4. Add or supersede a decision; do not silently rewrite the original rationale.
5. Update roadmap and acceptance criteria before implementation diverges.

## Phase close

A phase closes only when:

- acceptance criteria pass;
- artifacts are complete and reproducible at the promised level;
- known failures and limitations are explicit;
- decisions and progress records are updated;
- operating instructions match actual commands;
- temporary data is removed or classified;
- the repository is clean and changes are committed coherently.

Avoid declaring success from implementation alone. Verification, evidence,
operability, and records are part of the deliverable.

## Long-running work

For expensive jobs:

- pre-register the grid, controls, timing boundary, and retention plan;
- estimate cost and checkpoint granularity;
- make partial output detectable and resumable where practical;
- validate row counts, shapes, ranges, identities, and manifests before analysis;
- isolate measurement from caches or shared mutable state;
- capture raw evidence before plots or winner selection;
- keep the user informed without interpreting incomplete results as final.
