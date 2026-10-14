#!/bin/bash
# survey-tool launcher — starts the local server and opens the browser.
# Usage:  survey            # default port from config.json (7421)
#         survey 8080       # custom port
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT="${1:-}"
cd "$DIR"

# kill any previous instance on the port (read from local config if present)
if [ -z "$PORT" ]; then
  PORT=$(python3 - <<'PY'
import json, pathlib
p=pathlib.Path("config.json")
print(json.loads(p.read_text()).get("port",7421) if p.exists() else 7421)
PY
)
fi
if lsof -ti :$PORT >/dev/null 2>&1; then
  echo "(killing existing instance on :$PORT)"
  lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
  sleep 1
fi

echo "starting survey-tool → http://127.0.0.1:$PORT"
python3 server.py ${PORT:+--port $PORT} &
SRV=$!
sleep 1.5
URL="http://127.0.0.1:$PORT"
if command -v open >/dev/null 2>&1; then
  open "$URL" >/dev/null 2>&1 || echo "browser open unavailable; visit $URL manually"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL" >/dev/null 2>&1 || echo "browser open unavailable; visit $URL manually"
else
  echo "browser opener unavailable; visit $URL manually"
fi
echo "server pid $SRV — press Ctrl+C to stop"
wait $SRV