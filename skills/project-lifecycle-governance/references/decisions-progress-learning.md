# Decisions, Progress, and Learning

Keep current truth, historical evidence, and future intent distinct. Their documents complement one another but must not compete as authorities.

## Information roles

| Record | Responsibility |
|---|---|
| Architecture | Current system shape, boundaries, flows, and constraints |
| Decision record | Why a consequential choice was made and its effects |
| Progress history | Dated sequence of completed and verified work |
| Roadmap | Future gates, dependencies, priorities, and exit criteria |
| Limitations | Known current gaps, risks, and unsupported cases |
| Review | A dated assessment frozen as of a specific scope and revision |
| Experiment record | Reproducible evidence for a defined question |
| Module documentation | Local contract, operation, and constraints |

Do not turn the roadmap into a completion log or the architecture document into a diary. Link between records instead of duplicating their contents.

## Decision record

Create or update a decision record when a choice affects architecture, data contracts, evaluation, operations, security, compatibility, or future work.

```markdown
## DNNN — Decision title

- Date:
- Status: proposed | accepted | superseded | rejected
- Scope:
- Context:
- Observation or trigger:
- Evidence:
- Options considered:
- Decision:
- Rejected alternatives and why:
- Consequences and trade-offs:
- Implementation references:
- Validation:
- Supersedes / superseded by:
```

Record what influenced the choice: requirements, measurements, failures, resource limits, user feedback, regulation, maintenance cost, or compatibility. Describe expected and observed impact separately.

Never rewrite an accepted historical decision to match the present. Mark it superseded and link the replacement.

## Progress entry

Progress is evidence of movement, not a list of activity.

```markdown
## YYYY-MM-DD — Outcome

- Goal:
- Completed:
- Verified by:
- Measurements or artifacts:
- Decisions made:
- Challenges encountered:
- Resolution:
- Impact on architecture, scope, or schedule:
- Documentation updated:
- Next gate:
```

Use chronological entries. Correct factual errors explicitly; do not silently polish away setbacks or dead ends.

## Problem and learning record

For a recurring, expensive, surprising, or broadly useful problem, retain:

- symptom and detection method;
- affected scope and severity;
- root cause or current best explanation;
- hypotheses and failed attempts;
- final mitigation or resolution;
- evidence that the change worked;
- remaining risk;
- general lesson and conditions where it applies.

Small implementation issues belong in the commit, test, or issue system. Promote them into project knowledge only when the lesson has durable value.

## Keeping records trustworthy

- Cite commits, paths, tests, run IDs, datasets, or external sources.
- Label fact, inference, hypothesis, and opinion distinctly.
- Preserve negative results and limitations.
- State the revision and scope of dated reviews.
- Keep status vocabulary consistent.
- Use one stable identifier for every decision, experiment, run, and milestone.
- Link to owning records rather than copying tables or narratives.

## Content-ready learning without distortion

Engineering records may later support blogs, talks, portfolios, or social posts. Capture the factual source material now: the initial problem, constraint, attempt, failure, insight, change, evidence, limitation, and next question.

Do not write promotional copy into technical records. Keep confidential, personal, customer, security, and licensed information out of reusable notes. The separate content project should own editorial versions, publishing workflows, audience response, impressions, and feedback.

