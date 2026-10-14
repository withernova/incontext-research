# Bounded Codex automation

This is an explicit, one-shot development helper. It is **not** a polling daemon.

## Behavior

- `run-once.sh` creates an isolated Git branch and worktree.
- It starts exactly one ephemeral `codex exec` process.
- `bash -ic` is used so the user's `~/.bashrc` proxy configuration is loaded.
- Default hard timeout: 300 seconds.
- An exclusive lock prevents overlapping runs.
- There is no loop, cron entry, systemd unit, automatic retry, merge, push, or follow-up invocation.
- Changes and logs remain for human review.
- The main worktree's `start.sh` is never included.

## Commands

Connection-only smoke test:

```bash
SURVEY_CODEX_SMOKE_TIMEOUT=75 automation/codex/smoke.sh
```

One bounded implementation slice:

```bash
automation/codex/run-once.sh
```

Optional tighter timeout:

```bash
SURVEY_AUTOMATION_MAX_SECONDS=180 automation/codex/run-once.sh
```

Up to three bounded rounds in one isolated worktree:

```bash
automation/codex/run-bounded.sh
```

Defaults: 3 rounds, 180 seconds per round, 600 seconds total. It stops early on Codex failure, timeout, `git diff --check` failure, no new diff, or `SURVEY_TOOL_COMPLETE`. It still never merges or pushes.

Local no-token coordinator smoke test:

```bash
automation/codex/test-bounded.sh
```

Do not schedule these scripts unattended. A human must explicitly start a run and review its retained worktree before integration.
