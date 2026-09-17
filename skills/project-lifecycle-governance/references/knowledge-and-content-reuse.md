# Knowledge and Content Reuse

Technical work and published content have different authorities. Capture durable engineering knowledge in the project, then transform it in a separate content system.

## What the engineering project should preserve

- the problem and intended users;
- requirements, constraints, and assumptions;
- architecture and how it changed;
- decisions, alternatives, and influences;
- implementation milestones and commits;
- experiments, runs, metrics, and raw evidence;
- failures, challenges, solutions, and negative results;
- limitations, risks, and unanswered questions;
- reusable lessons with provenance.

Keep these records factual and close to their owners. Do not create a second narrative file that duplicates decisions, progress, and experiment results merely for future content.

## Provenance for reusable insights

When a lesson may be valuable beyond the project, make its source traceable:

```yaml
insight_id: stable-id
topic: concise-topic
statement: factual-or-qualified-lesson
evidence:
  commits: []
  decisions: []
  runs: []
  reviews: []
conditions: when-the-lesson-applies
limitations: where-it-may-not-apply
audience: engineering|product|research|general
confidentiality: public|internal|restricted
reuse_status: candidate|approved|published
```

This may live in an existing decision, progress entry, or review. Create a dedicated knowledge index only after the volume justifies another owner.

## Separate content project responsibilities

The content project should own derivative artifacts and channel operations:

- blog, portfolio, talk, video, newsletter, and social drafts;
- editorial calendar and publishing status;
- platform-specific variants and media assets;
- source-to-claim mapping and permissions;
- publication URLs and dates;
- impressions, reach, engagement, conversions, comments, and feedback;
- content experiments and retrospective analysis.

Link every technical claim back to a stable engineering source such as a commit, decision, review, or run. Snapshot or version sources used by published content so later engineering updates do not alter the historical basis of a claim.

## Feedback loop

Audience feedback is not automatically engineering truth. Classify it as observation, request, hypothesis, or validated requirement. If it changes the product or research direction, promote it through the normal requirement and decision process, then link that decision back to the content feedback record.

## Safety and quality

- Remove secrets, credentials, personal information, customer data, private repository details, and exploitable security information.
- Respect licenses, attribution, employer or client policy, and embargoes.
- Distinguish measured results from interpretation and storytelling.
- Preserve uncertainty and limitations in public claims.
- Avoid cherry-picking a successful run when the full experiment tells a different story.

## Useful narrative structure

For later editorial work, the most reusable technical sequence is:

1. Problem and stakes.
2. Initial assumptions and constraints.
3. First approach and why it was reasonable.
4. Failure or surprising evidence.
5. Insight and decision.
6. Implementation change.
7. Verification and measurable impact.
8. Limitations and next question.

Capture these facts during engineering; craft the story only in the content project.

