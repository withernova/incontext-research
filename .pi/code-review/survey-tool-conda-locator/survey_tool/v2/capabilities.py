"""Privacy-safe, read-only discovery of optional server capabilities."""

from __future__ import annotations

import os
import re
import selectors
import shutil
import subprocess
import time
from collections.abc import Callable
from typing import Any

HERDR_PROBE_TIMEOUT_SECONDS = 0.75
HERDR_PROBE_OUTPUT_BYTES = 4096


def _run_bounded(command: list[str], *, timeout: float, output_limit: int) -> tuple[int, bytes]:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = bytearray()
    deadline = time.monotonic() + timeout
    selector = selectors.DefaultSelector()
    assert process.stdout is not None
    os.set_blocking(process.stdout.fileno(), False)
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        while process.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout)
            events = selector.select(remaining)
            if not events:
                raise subprocess.TimeoutExpired(command, timeout)
            chunk = os.read(process.stdout.fileno(), min(1024, output_limit + 1 - len(output)))
            if not chunk:
                continue
            output.extend(chunk)
            if len(output) > output_limit:
                raise ValueError("capability probe output limit exceeded")
        remaining = output_limit + 1 - len(output)
        if remaining > 0:
            try:
                output.extend(os.read(process.stdout.fileno(), remaining))
            except BlockingIOError:
                pass
        if len(output) > output_limit:
            raise ValueError("capability probe output limit exceeded")
        return process.returncode or 0, bytes(output)
    finally:
        selector.close()
        if process.poll() is None:
            process.kill()
        process.wait()
        process.stdout.close()


def herdr_capability(
    *,
    environ: dict[str, str] | None = None,
    which: Callable[[str], str | None] = shutil.which,
    runner: Callable[..., tuple[int, bytes]] = _run_bounded,
) -> dict[str, Any]:
    """Return a deliberately small capability summary without session details."""
    managed = (os.environ if environ is None else environ).get("HERDR_ENV") == "1"
    result = {
        "managed": managed,
        "cli_available": False,
        "pi_supported": False,
        "codex_supported": False,
        "probe_status": "unavailable",
        "access": "discovery_only",
    }
    try:
        binary = which("herdr")
        if not binary:
            return result
        result["cli_available"] = True
        returncode, output = runner(
            [binary, "agent"],
            timeout=HERDR_PROBE_TIMEOUT_SECONDS,
            output_limit=HERDR_PROBE_OUTPUT_BYTES,
        )
        # Herdr command-group discovery intentionally exits 2 after printing
        # authoritative usage. Accept it only when the expected help markers
        # are present; arbitrary stderr containing "codex" is not capability data.
        valid_help = b"herdr agent commands:" in output.lower() and b"kinds:" in output.lower()
        if returncode not in {0, 2} or not valid_help:
            return result
        result["codex_supported"] = re.search(rb"\bcodex\b", output, re.IGNORECASE) is not None
        result["pi_supported"] = re.search(rb"\bpi\b", output, re.IGNORECASE) is not None
        result["probe_status"] = "available"
    except Exception:
        pass
    return result
