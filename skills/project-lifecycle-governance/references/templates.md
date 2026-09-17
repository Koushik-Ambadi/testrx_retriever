# Conditional Templates

Use only the records that the project needs. Prefer extending an existing owner over creating another file. Replace examples with repository conventions and remove unused fields.

## Project documentation index

```markdown
# Documentation

| Area | Authoritative document | Responsibility | Update trigger |
|---|---|---|---|
| Architecture | path | Current structure and flows | Boundary or contract change |
| Decisions | path | Consequential choices and rationale | Decision accepted or superseded |
| Roadmap | path | Future gates and dependencies | Priority or gate changes |
| Progress | path | Verified chronology | Milestone or gate completion |
| Testing | path | Project-wide strategy | Quality policy changes |
| Limitations | path | Current risks and unsupported cases | Limitation found or resolved |
```

## Architecture section

```markdown
## Component name

- Responsibility:
- Inputs and outputs:
- Public contract:
- Dependencies:
- State and persistence:
- Failure behavior:
- Security and privacy considerations:
- Observability:
- Replaceable implementations:
- Relevant decisions:
```

## Roadmap gate

```markdown
## Gate GNN — Outcome

- Status: proposed | active | blocked | complete
- Goal:
- In scope:
- Out of scope:
- Dependencies:
- Deliverables:
- Acceptance evidence:
- Risks:
- Owner:
- Next gate enabled:
```

## Module README

```markdown
# Module name

## Responsibility

One clear ownership statement.

## Contract

- Inputs:
- Outputs:
- Invariants:
- Errors:
- Side effects:

## Structure

Explain files only when their roles are not obvious.

## Operation

Configuration, invocation, and minimal example.

## Verification

Tests, fixtures, and local checks.

## Constraints

Known local limitations and links to project-level records.
```

## Test strategy

```markdown
# Test Strategy

- Quality risks:
- Test layers and ownership:
- Required checks by change type:
- Fixtures and test-data policy:
- Determinism and isolation policy:
- Performance or model-evaluation policy:
- CI gates:
- Manual verification that remains necessary:
- Evidence retention:
- Known gaps:
```

## Experiment definition

```yaml
experiment_id: stable-id
question: decision-oriented question
hypothesis: expected result and mechanism
decision_enabled: what changes after the result
controls:
  fixed: []
  varied: []
data:
  dataset: name-version
  split: value
  slices: []
  leakage_controls: []
metrics:
  primary: []
  secondary: []
  diagnostic: []
selection_rule: predeclared rule
stopping_rule: condition
resources:
  time_limit: value
  cost_limit: value
reproduction:
  config: path
  command: command
```

## Run metadata

```json
{
  "experiment_id": "stable-id",
  "run_id": "unique-id",
  "status": "completed",
  "started_at": "ISO-8601",
  "completed_at": "ISO-8601",
  "code_revision": "commit",
  "command": "exact command",
  "inputs": [{"uri": "path-or-uri", "sha256": "hash"}],
  "configuration": "path-or-embedded-canonical-config",
  "environment": {},
  "seeds": [],
  "cache_policy": "cold|warm|disabled",
  "timing_boundary": "description",
  "metrics": "path-or-uri",
  "artifacts": [],
  "warnings": [],
  "errors": []
}
```

## Dated review

```markdown
# Review title

- Date:
- Repository revision:
- Scope:
- Method:
- Evidence inspected:

## Findings

Order by severity and include location, impact, and evidence.

## Recommendations

Separate required remediation from optional improvement.

## Limitations of this review

State what was not inspected or verified.
```

## Handoff

```markdown
# Handoff

- Outcome delivered:
- Branch and commit:
- Verification performed:
- Documentation updated:
- Data, configs, and artifacts:
- Commands to reproduce:
- Deployment or migration notes:
- Rollback path:
- Known limitations:
- Remaining work and next gate:
```

