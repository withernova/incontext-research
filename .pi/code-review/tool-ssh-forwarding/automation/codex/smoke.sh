#!/usr/bin/env bash
set -euo pipefail

MAX_SECONDS="${SURVEY_CODEX_SMOKE_TIMEOUT:-90}"
LOG="${SURVEY_CODEX_SMOKE_LOG:-/tmp/survey-codex-smoke.log}"
set +e
timeout --signal=TERM --kill-after=5s "$MAX_SECONDS" \
  bash -ic 'exec codex exec --ephemeral --sandbox read-only --color never --skip-git-repo-check "Do not use tools and do not read files. Reply with exactly: SURVEY_CODEX_SMOKE_OK"' \
  2>&1 | tee "$LOG"
status=${PIPESTATUS[0]}
set -e

if [[ "$status" -eq 124 || "$status" -eq 137 ]]; then
  echo "Smoke timed out safely; no retry loop was started." >&2
  exit "$status"
fi
if [[ "$status" -ne 0 ]]; then
  echo "Smoke failed once and stopped; no automatic retry will occur." >&2
  exit "$status"
fi
grep -q 'SURVEY_CODEX_SMOKE_OK' "$LOG"
echo "Smoke passed once and exited; no background process or polling loop remains."
