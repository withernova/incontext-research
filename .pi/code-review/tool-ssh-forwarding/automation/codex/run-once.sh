#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_REF="${SURVEY_AUTOMATION_BASE_REF:-HEAD}"
RUN_ID="${SURVEY_AUTOMATION_RUN_ID:-$(date -u +%Y%m%dT%H%M%SZ)}"
WORK_ROOT="${SURVEY_AUTOMATION_WORK_ROOT:-/tmp/survey-tool-codex}"
WORKTREE="$WORK_ROOT/$RUN_ID"
BRANCH="automation/codex-$RUN_ID"
LOG_DIR="$REPO/.automation/codex/$RUN_ID"
PROMPT="$REPO/automation/codex/continue-survey-tool.md"
MAX_SECONDS="${SURVEY_AUTOMATION_MAX_SECONDS:-300}"
LOCK_FILE="$WORK_ROOT/automation.lock"

mkdir -p "$WORK_ROOT" "$LOG_DIR"
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Refusing to start: another Survey Tool Codex automation is active." >&2
  exit 3
fi
if [[ -n "$(git -C "$REPO" status --porcelain --untracked-files=no | grep -v '^ M start.sh$' || true)" ]]; then
  echo "Refusing to start: tracked changes other than start.sh exist in the main worktree." >&2
  exit 2
fi

git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE_REF" >"$LOG_DIR/worktree.log" 2>&1
cleanup_note() {
  printf 'Worktree retained for review: %s\nBranch: %s\n' "$WORKTREE" "$BRANCH"
}
trap cleanup_note EXIT

# Use an interactive shell so ~/.bashrc loads the user's proxy configuration.
set +e
timeout --signal=TERM --kill-after=10s "$MAX_SECONDS" \
  bash -ic 'exec codex exec --cd "$1" --approve-for-me --ephemeral --color never --output-last-message "$2" -' \
  survey-codex "$WORKTREE" "$LOG_DIR/final.md" <"$PROMPT" >"$LOG_DIR/run.log" 2>&1
status=$?
set -e

git -C "$WORKTREE" status --short >"$LOG_DIR/status.txt"
git -C "$WORKTREE" diff --stat >"$LOG_DIR/diff-stat.txt"
git -C "$WORKTREE" diff >"$LOG_DIR/changes.patch"
printf '%s\n' "$status" >"$LOG_DIR/exit-code.txt"
printf 'Run: %s\nWorktree: %s\nBranch: %s\nLog: %s\nExit: %s\n' "$RUN_ID" "$WORKTREE" "$BRANCH" "$LOG_DIR" "$status"
if [[ -s "$LOG_DIR/final.md" ]]; then printf '\n--- Codex final summary ---\n'; cat "$LOG_DIR/final.md"; fi
exit "$status"
