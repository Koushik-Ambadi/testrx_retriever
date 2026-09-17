# Git and Delivery

Git history is part of the engineering evidence. Keep it understandable, attributable, reversible, and synchronized deliberately.

## Before changing the repository

Inspect:

- working-tree and index status;
- current branch and upstream;
- local and remote branches;
- remotes and primary branch;
- author and committer identity;
- recent history and repository-specific instructions.

Treat existing uncommitted changes as user-owned unless their origin is known. Avoid destructive reset, checkout, clean, force-push, or broad deletion as a shortcut.

## Branch and commit discipline

Use the repository's naming convention. If none exists, use short purpose-oriented names such as `feature/run-manifests`, `fix/parser-boundary`, or `docs/experiment-policy`.

Create small coherent commits that each leave the repository in a valid state. Conventional prefixes are useful when the project accepts them:

- `feat:` new capability;
- `fix:` defect correction;
- `test:` test or fixture changes;
- `data:` governed dataset or manifest changes;
- `docs:` documentation only;
- `refactor:` structural change without intended behavior change;
- `chore:` tooling or maintenance.

Separate generated output from source changes. Do not mix unrelated cleanup into a feature commit. A commit message should explain the outcome and, when not obvious, why it matters.

Configure and verify the intended owner identity before committing. Do not attribute automated work to the tool unless the owner explicitly wants that identity.

## Integration and cleanup

1. Fetch and inspect divergence.
2. Verify the branch against its intended base.
3. Run proportionate tests and documentation checks.
4. Prefer a fast-forward or normal reviewed merge according to project policy.
5. Push only when authorized and after verifying the destination.
6. Delete a branch only after proving its work is safely integrated or otherwise retained.
7. Recheck local and remote status after integration.

Never force-update a shared primary branch without explicit authorization and a recovery plan. Do not delete unmerged work merely to make the branch list look tidy.

## Large and generated artifacts

Define repository policy for datasets, model weights, logs, reports, and run outputs. Choose among Git, Git LFS, releases, artifact storage, or reproducible regeneration based on size, immutability, access, and audit needs.

Track compact manifests, schemas, checksums, configurations, and summaries even when payloads live elsewhere. Generated artifacts must state their source revision and reproduction method.

## Delivery checklist

Before handing off or releasing:

- requested behavior is implemented;
- relevant automated and manual checks pass;
- migration and rollback needs are understood;
- architecture, decisions, tests, progress, limitations, and runbooks are current where affected;
- configurations and commands are reproducible;
- secrets and private data are absent;
- commits are coherent and correctly attributed;
- the working tree is clean or remaining changes are explicitly reported;
- branch, upstream, commit IDs, artifacts, and known limitations are reported.

