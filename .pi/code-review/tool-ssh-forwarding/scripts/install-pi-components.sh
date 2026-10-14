#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PI_HOME="${PI_AGENT_DIR:-$HOME/.pi/agent}"
mkdir -p "$PI_HOME/extensions" "$PI_HOME/skills"
link_component() {
  local source="$1" target="$2"
  if [[ -e "$target" && ! -L "$target" ]]; then
    printf 'Refusing to replace existing non-symlink: %s\n' "$target" >&2
    exit 1
  fi
  ln -sfn "$source" "$target"
  printf 'linked %s -> %s\n' "$target" "$source"
}
OLD_TARGET="$PI_HOME/extensions/experiment-watchdog"
if [[ -L "$OLD_TARGET" ]]; then
  OLD_SOURCE="$(readlink "$OLD_TARGET")"
  if [[ "$OLD_SOURCE" = /* ]]; then OLD_CANDIDATE="$OLD_SOURCE"; else OLD_CANDIDATE="$(dirname "$OLD_TARGET")/$OLD_SOURCE"; fi
  OLD_RESOLVED="$(realpath -m "$OLD_CANDIDATE")"
  REPO_OLD_RESOLVED="$(realpath -m "$ROOT/extensions/experiment-watchdog")"
  REPO_NEW_RESOLVED="$(realpath -m "$ROOT/extensions/experiment-steward")"
  if [[ "$OLD_RESOLVED" == "$REPO_OLD_RESOLVED" || "$OLD_RESOLVED" == "$REPO_NEW_RESOLVED" ]]; then
    rm "$OLD_TARGET"
    printf 'removed deprecated repository symlink %s\n' "$OLD_TARGET"
  else
    printf 'Refusing to remove unrelated deprecated symlink: %s -> %s\n' "$OLD_TARGET" "$OLD_SOURCE" >&2
    exit 1
  fi
elif [[ -e "$OLD_TARGET" ]]; then
  printf 'Refusing to replace existing deprecated non-symlink: %s\n' "$OLD_TARGET" >&2
  exit 1
fi
link_component "$ROOT/extensions/experiment-steward" "$PI_HOME/extensions/experiment-steward"
link_component "$ROOT/extensions/research-explorer" "$PI_HOME/extensions/research-explorer"
link_component "$ROOT/extensions/light-plan" "$PI_HOME/extensions/light-plan"
link_component "$ROOT/extensions/code-change-review" "$PI_HOME/extensions/code-change-review"
link_component "$ROOT/extensions/copy-code" "$PI_HOME/extensions/copy-code"
link_component "$ROOT/skills/research-survey" "$PI_HOME/skills/research-survey"
link_component "$ROOT/skills/research-explorer" "$PI_HOME/skills/research-explorer"
printf '\nReload pi with /reload or restart it.\n'
