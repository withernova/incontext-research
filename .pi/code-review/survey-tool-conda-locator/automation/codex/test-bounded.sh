#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TMP="$(mktemp -d /tmp/survey-bounded-test.XXXXXX)"
FAKE="$TMP/fake-codex"
PROMPT="$TMP/prompt.md"
RUN_ID="test-$(date +%s)-$$"
cat >"$FAKE" <<'FAKE'
#!/usr/bin/env bash
set -euo pipefail
out=""; work=""
while (($#)); do
  case "$1" in --cd) work="$2"; shift 2;; --output-last-message) out="$2"; shift 2;; *) shift;; esac
done
count_file="${SURVEY_FAKE_COUNT_FILE:?}"; count=0; [[ -f "$count_file" ]] && count=$(<"$count_file"); count=$((count+1)); printf '%s' "$count" >"$count_file"
if (( count == 1 )); then printf 'bounded smoke\n' >"$work/bounded-smoke.txt"; fi
printf 'fake round %s complete\n' "$count" >"$out"
FAKE
chmod +x "$FAKE"; printf 'fake prompt\n' >"$PROMPT"
export SURVEY_FAKE_COUNT_FILE="$TMP/count"
SURVEY_AUTOMATION_ALLOW_DIRTY=1 SURVEY_AUTOMATION_RUN_ID="$RUN_ID" SURVEY_AUTOMATION_MAX_ROUNDS=3 SURVEY_AUTOMATION_ROUND_SECONDS=30 SURVEY_AUTOMATION_TOTAL_SECONDS=90 SURVEY_AUTOMATION_CODEX_BIN="$FAKE" SURVEY_AUTOMATION_PROMPT="$PROMPT" "$REPO/automation/codex/run-bounded.sh" >"$TMP/output"
SUMMARY="$REPO/.automation/codex/$RUN_ID/summary.json"
grep -q '"stop_reason":"no_effective_diff"' "$SUMMARY"
[[ "$(<"$TMP/count")" == 2 ]]
worktree=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["worktree"])' "$SUMMARY")
branch=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["branch"])' "$SUMMARY")
git -C "$REPO" worktree remove --force "$worktree"; git -C "$REPO" branch -D "$branch" >/dev/null
rm -rf "$TMP"
echo "bounded coordinator smoke passed: stopped after no effective diff; no third round"
