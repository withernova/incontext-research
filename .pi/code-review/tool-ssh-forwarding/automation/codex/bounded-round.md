Complete exactly one small unfinished Survey Tool 2.0 product slice in this isolated worktree, then stop.

Read only the files needed for that slice. Start with `docs/2.0/IMPLEMENTATION_PROGRESS.md` and `git diff --stat`; preserve useful changes left by prior rounds. Prefer an existing backend capability missing a usable UI or a concrete migration/operations gap. Do not broadly refactor or restyle.

Hard boundaries:
- Never access external research projects, especially any `incontext` project.
- Never initialize a real project store, run Worker/MinerU/download/ingest/pi/experiments, or modify `start.sh`.
- Never change Markdown/legacy JSON authority, Run review/authorization/Outbox/Claim gates, or add hard delete.
- Do not commit, merge, push, rebase, or modify other worktrees.
- Change at most 8 source/test/doc files, excluding generated `static/v2` assets.
- Add only focused tests. Do not run full suites.
- Run targeted checks and `git diff --check`.
- Keep the final response under 250 words and never print a full diff.

If the tool has no clear high-value unfinished slice that fits safely, make no changes and end with the exact line `SURVEY_TOOL_COMPLETE`. Otherwise report the slice, files, checks, and risks.