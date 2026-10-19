#!/usr/bin/env bash
# Read-only wait for the already approved Run. Does not start/retry any Run.
set -euo pipefail
ssh -o BatchMode=yes -o ClearAllForwardings=yes SZY-3090 'python3 -' <<'PY'
import ctypes
import json
import os
from pathlib import Path
import select
import time

root = Path('/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018')
exit_file = root / '.survey-tool-exit-code'
lib = ctypes.CDLL(None, use_errno=True)
fd = lib.inotify_init1(os.O_NONBLOCK)
if fd < 0:
    raise OSError(ctypes.get_errno(), 'inotify_init1')
# Root-level close-write/create/move events; no repeated model or sleep polling.
if lib.inotify_add_watch(fd, str(root).encode(), 0x8 | 0x80 | 0x100) < 0:
    raise OSError(ctypes.get_errno(), 'inotify_add_watch')
deadline = time.monotonic() + 7200
print('Waiting for existing Run terminal exit file; no scientific execution.', flush=True)
try:
    while True:
        code = exit_file.read_text().strip() if exit_file.exists() else ''
        if code:
            code = int(code)
            print(json.dumps({'run_id': root.name, 'observed_exit_code': code,
                              'metrics_exists': (root / 'metrics.json').is_file()}), flush=True)
            if code == 0 and not (root / 'metrics.json').is_file():
                raise RuntimeError('Exit 0 without required metrics; requires artifact audit')
            raise SystemExit(code if 0 <= code <= 255 else 1)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            print('Wait deadline reached; Run outcome remains unverified.', flush=True)
            raise SystemExit(124)
        readable, _, _ = select.select([fd], [], [], remaining)
        if readable:
            try:
                os.read(fd, 65536)
            except BlockingIOError:
                pass
finally:
    os.close(fd)
PY
