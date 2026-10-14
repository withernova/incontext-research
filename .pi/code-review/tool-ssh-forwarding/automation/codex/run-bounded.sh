#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE_REF="${SURVEY_AUTOMATION_BASE_REF:-HEAD}"
RUN_ID="${SURVEY_AUTOMATION_RUN_ID:-bounded-$(date -u +%Y%m%dT%H%M%SZ)}"
MAX_ROUNDS="${SURVEY_AUTOMATION_MAX_ROUNDS:-3}"
ROUND_SECONDS="${SURVEY_AUTOMATION_ROUND_SECONDS:-180}"
TOTAL_SECONDS="${SURVEY_AUTOMATION_TOTAL_SECONDS:-600}"
WORK_ROOT="${SURVEY_AUTOMATION_WORK_ROOT:-/tmp/survey-tool-codex}"
WORKTREE="$WORK_ROOT/$RUN_ID"
BRANCH="automation/codex-$RUN_ID"
LOG_DIR="$REPO/.automation/codex/$RUN_ID"
PROMPT="${SURVEY_AUTOMATION_PROMPT:-$REPO/automation/codex/bounded-round.md}"
CODEX_BIN="${SURVEY_AUTOMATION_CODEX_BIN:-codex}"
LOCK_FILE="$WORK_ROOT/automation.lock"

case "$MAX_ROUNDS:$ROUND_SECONDS:$TOTAL_SECONDS" in
  *[!0-9:]*|'') echo "Budgets must be positive integers." >&2; exit 2;;
esac
(( MAX_ROUNDS >= 1 && MAX_ROUNDS <= 5 )) || { echo "MAX_ROUNDS must be 1..5" >&2; exit 2; }
(( ROUND_SECONDS >= 30 && ROUND_SECONDS <= 600 )) || { echo "ROUND_SECONDS must be 30..600" >&2; exit 2; }
(( TOTAL_SECONDS >= ROUND_SECONDS && TOTAL_SECONDS <= 1800 )) || { echo "TOTAL_SECONDS must be ROUND_SECONDS..1800" >&2; exit 2; }

mkdir -p "$WORK_ROOT" "$LOG_DIR"
exec 9>"$LOCK_FILE"
flock -n 9 || { echo "Another Survey Tool Codex automation is active." >&2; exit 3; }
if [[ "${SURVEY_AUTOMATION_ALLOW_DIRTY:-0}" != "1" && -n "$(git -C "$REPO" status --porcelain --untracked-files=no | grep -v '^ M start.sh$' || true)" ]]; then
  echo "Tracked changes other than start.sh exist in the main worktree." >&2; exit 2
fi

git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE_REF" >"$LOG_DIR/worktree.log" 2>&1
start_epoch=$(date +%s)
stop_reason="round_limit"
rounds_completed=0
previous_tree=$(git -C "$WORKTREE" diff | sha256sum | cut -d' ' -f1)

for ((round=1; round<=MAX_ROUNDS; round++)); do
  elapsed=$(( $(date +%s) - start_epoch ))
  remaining=$(( TOTAL_SECONDS - elapsed ))
  if (( remaining < 30 )); then stop_reason="total_timeout"; break; fi
  budget=$ROUND_SECONDS; (( budget > remaining )) && budget=$remaining
  round_dir="$LOG_DIR/round-$round"; mkdir -p "$round_dir"
  set +e
  timeout --signal=TERM --kill-after=10s "$budget" \
    bash -ic 'exec "$3" exec --cd "$1" --approve-for-me --ephemeral --color never --output-last-message "$2" -' \
    survey-codex "$WORKTREE" "$round_dir/final.md" "$CODEX_BIN" <"$PROMPT" >"$round_dir/run.log" 2>&1
  status=$?
  set -e
  printf '%s\n' "$status" >"$round_dir/exit-code.txt"
  # Include newly created files in diff/hash without staging their contents.
  git -C "$WORKTREE" add -N -- .
  git -C "$WORKTREE" status --short >"$round_dir/status.txt"
  git -C "$WORKTREE" diff --stat >"$round_dir/diff-stat.txt"
  if (( status != 0 )); then stop_reason=$([[ $status == 124 || $status == 137 ]] && echo round_timeout || echo codex_failure); break; fi
  if ! git -C "$WORKTREE" diff --check >"$round_dir/diff-check.txt" 2>&1; then stop_reason="diff_check_failure"; break; fi
  current_tree=$(git -C "$WORKTREE" diff | sha256sum | cut -d' ' -f1)
  if [[ "$current_tree" == "$previous_tree" ]]; then stop_reason="no_effective_diff"; break; fi
  previous_tree="$current_tree"; rounds_completed=$round
  if grep -qx 'SURVEY_TOOL_COMPLETE' "$round_dir/final.md" 2>/dev/null; then stop_reason="complete_marker"; break; fi
done

git -C "$WORKTREE" status --short >"$LOG_DIR/status.txt"
git -C "$WORKTREE" diff --stat >"$LOG_DIR/diff-stat.txt"
git -C "$WORKTREE" diff >"$LOG_DIR/changes.patch"
printf '{"run_id":"%s","branch":"%s","worktree":"%s","rounds_completed":%d,"max_rounds":%d,"stop_reason":"%s"}\n' \
  "$RUN_ID" "$BRANCH" "$WORKTREE" "$rounds_completed" "$MAX_ROUNDS" "$stop_reason" >"$LOG_DIR/summary.json"
printf 'Run %s stopped: %s (%d/%d effective rounds)\nWorktree: %s\nBranch: %s\nLog: %s\n' \
  "$RUN_ID" "$stop_reason" "$rounds_completed" "$MAX_ROUNDS" "$WORKTREE" "$BRANCH" "$LOG_DIR"
for final in "$LOG_DIR"/round-*/final.md; do [[ -s "$final" ]] && { printf '\n--- %s ---\n' "$(basename "$(dirname "$final")")"; cat "$final"; }; done
