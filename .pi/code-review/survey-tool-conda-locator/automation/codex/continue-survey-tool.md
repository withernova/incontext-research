# Survey Tool 2.0 bounded implementation task

You are working in an isolated Git worktree of Survey Tool. Complete exactly one coherent, user-visible vertical slice, then stop.

## Priority

Inspect `docs/2.0/IMPLEMENTATION_PROGRESS.md`, current code, and recent Git history. Select the highest-value unfinished product slice that can be completed safely in one run. Prefer completing existing backend capabilities in the UI over broad redesign. If no clear slice exists, improve the migration identity-index apply experience with persisted checkpoint/history visibility and conflict diagnostics.

## Hard boundaries

- Work only inside the current repository worktree.
- Never access or modify `/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext` or any external research project.
- Never initialize a real project's v2 SQLite store.
- Do not run a v2 Worker, download papers, invoke MinerU, ingest a paper, start pi, or execute experiments.
- Do not modify `start.sh`.
- Do not alter legacy Experiment/Run authority, review gates, execution authorization, Outbox, or Claim validation gates.
- Do not copy research prose into SQLite.
- Do not add hard delete behavior.
- Do not push, merge, rebase, or modify other branches/worktrees.
- Do not use `--dangerously-bypass-approvals-and-sandbox`.

## Engineering expectations

- Read existing contracts before editing.
- Keep each field under one authority.
- Preserve explicit human confirmation and revision checks for writes.
- Add only focused tests for the changed contract. Do not run the full suite.
- Run targeted Python tests or TypeScript build as appropriate, plus `git diff --check`.
- Update `docs/2.0/IMPLEMENTATION_PROGRESS.md` briefly.
- Do not commit; leave changes in the isolated worktree for human review.

## Completion report

End with:

1. selected slice and why;
2. files changed;
3. safety boundaries preserved;
4. targeted checks run and results;
5. remaining risks or manual review items.
