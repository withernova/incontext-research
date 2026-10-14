# Managed Run Phase 1 operations

Managed execution is an opt-in consumer for an already approved workflow-v2 Run. The browser can explicitly authorize and hand the Run to the local background Steward, but it never receives a lease token and never supplies a command, path, or consumer identity.

## Remote setup

Use a restricted SSH account. Install `bubblewrap` and `tmux` on the bound Server. In the Workspace binding configure absolute `remote_repo`, data/run roots, `environment_policy.allowed_write_roots`, `read_only_roots`, and `execution_isolation`:

```json
{"mode":"bubblewrap","required":true,"network":"none","deny_read_roots":["/home/research/.ssh"],"notes":"Phase 1 managed runner"}
```

`remote_data_root` must be read-only policy data. Run, output, log and metrics paths must resolve beneath an allowed write root. Missing isolation, tools, paths, authorization, snapshot agreement, or lease evidence fails closed. Network `host` is an explicit operator choice; `none` creates a separate network namespace.

Directory policy is structured and defaults to deny writes outside the allowlist. For example:

```json
{
  "environment_policy": {
    "default_deny_write": true,
    "allowed_write_roots": ["/srv/project", "/srv/runs"],
    "read_only_roots": ["/datasets"],
    "forbidden_paths": ["/srv/project/.git", "/home/runner/.ssh"],
    "forbidden_operations": ["sudo", "mount"]
  },
  "dataset_bindings": [
    {"id":"imagenet","label":"ImageNet validation","source_path":"/datasets/imagenet","target_path":"/srv/project/data/imagenet","mode":"bind_ro","required":true,"notes":"Operator-provided read-only dataset"}
  ]
}
```

`notes` never grants access. Phase 1 datasets are directories: a required source must exist and be readable at preflight. An absent `bind_ro` destination is created only as a sandbox mount point (`--dir`) before its read-only bind; an existing destination must be a directory and remain inside the approved write root. `symlink_ro` is an explicit alternative: the host link is created only when absent and an existing link must resolve exactly to the approved source; the source remains read-only in the sandbox. A forbidden child such as `/srv/project/.git` is allowed beneath `/srv/project`, but must already exist and is rebound read-only after every writable bind. A forbidden path that contains/equal an allowed root is rejected. Each `deny_read_root` must be an existing directory and is hidden with an empty tmpfs; this hides host content rather than deleting it. Changing Workspace roots, isolation, activation, or dataset bindings after authorization invalidates the dispatch snapshot and requires fresh authorization.

## Governed flow

1. Create a workflow-v2 Run and complete design/code gates.
2. Submit and approve it. “授权并交给 Steward 后台运行” is the single explicit execution decision: it creates/uses the existing Outbox authorization and starts a detached, prompt-free local supervisor.
3. The supervisor atomically claims only that Run, keeps the raw lease in its own memory, performs the existing managed preflight, and launches the approved command in the fixed remote tmux sandbox.
4. Steward heartbeats and inspects bounded evidence. A short-lived Herdr/Pi session is only for code implementation or failure diagnosis; closing it does not own or stop the Run.
5. After stable, declared metrics and artifacts exist, Steward completes the dispatch. The Run moves to `analysis_pending` with a factual result draft. A human must still review and finalize results; no Claim is approved automatically.

If the local supervisor exits while the remote tmux continues, the UI offers recovery only after the old lease expires. Recovery rotates the lease and resumes monitoring; it never launches the approved command a second time.

For diagnostics, the same lease holder can call `surveyctl.py --project PROJECT managed-run preflight|status ...`. Never paste tokens into logs or browser APIs. A Pi restart intentionally loses its in-memory token. After the old running lease expires, use `survey_run_execution reattach` with the exact dispatch ID; the terminal-only `surveyctl managed-run reattach` rotates and prints a new raw token which the extension captures and redacts. This still creates brief process/stdout exposure, so run it only in the trusted terminal and never redirect output to disk. Active leases, non-managed runs, changed authorization/spec/policy snapshots, and unrelated dispatches are refused. Phase 1 does not provision hosts, install packages, validate scientific conclusions, or provide automatic remediation/code edits.
