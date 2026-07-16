# Recent experiment archive index · 2026-07-16

## E-002 mechanism runs

Exact local note ↔ exact remote directory:

```text
shell/06_experiments/E-002/runs/<RUN_ID>.md
/home/featurize/work/mechanism/explog/E-002/runs/<RUN_ID>/
```

Archived:

```text
R-010-qwen3vl-object-token-shuffle-n50-full-vs-center-vis
R-011-qwen3vl-large-rich-object-shuffle-stratified-n27
R-012-qwen3vl-large-object-token-identity-transfer-n27
R-013-qwen3vl-wrong-class-object-token-replacement-n27
R-014-qwen3vl-partial-support-token-contamination-n27
R-014b-qwen3vl-partial-support-token-contamination-centerout-n27
R-014c-qwen3vl-sampled-centerout-support-contamination-n27
R-015-qwen3vl-support-vs-query-object-shuffle-n27
```

Cross-run summaries:

```text
shell/06_experiments/E-002/result.md
shell/06_experiments/E-002/token_intervention_key_results.md
shell/06_experiments/E-002/experiment_audit_notes.md
```

## E-003 metric audit runs

Exact local note ↔ exact remote directory:

```text
shell/06_experiments/E-003/runs/<RUN_ID>.md
/home/featurize/work/mechanism/explog/E-003/runs/<RUN_ID>/
```

Archived:

```text
E003-R-001-data-rehydrate-local-lasot-n140             completed data prep
E003-R-002-joint-f1-n140-failed-env                    failed, zero records
E003-R-003-torch-compat-smoke-local-lasot-n1           passed smoke
E003-R-004-joint-f1-iou-local-lasot-n140               aborted/superseded
E003-R-004b-joint-f1-iou-local-lasot-n140-t128         completed main diagnostic
```

Summary:

```text
shell/06_experiments/E-003/result.md
```

## Registry limitation

The current `surveyctl.py` build exposes experiment context/handoff but no experiment-create command. E-003 therefore cannot be inserted into `.survey-tool/experiments.json` through the required public interface. Direct editing of `.survey-tool/` is intentionally not performed. The canonical archive for these runs is the exact-ID run notes and remote run-centric directories above. When the workbench adds E-003/create support, these notes contain all mandatory fields needed for synchronization.

The old auto-generated local files `E-002/runs/R-010.md` … `R-017.md` are legacy survey-tool records whose numeric IDs do not correspond to the later descriptive remote run IDs. They are retained for audit history and are not used as the canonical records for the runs listed above.
