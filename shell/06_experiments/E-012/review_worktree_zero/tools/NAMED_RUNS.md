# Timestamped named runs

## 通用 FOCUS branch config

推荐入口为 `tools/run/run_branch.sh`，默认读取
`configs/sft/qwen3vl_8b_focus_branch.py`。配置中的 `branch.source` 可以在
`native`、E011 early-GT-mask checkpoint 和旧 E009 checkpoint 之间切换；
profile 会同步设置 `experiment_id`、`parent_checkpoint` 和父 checkpoint
校验开关。旧的 `run_e009_branch.sh` 与 `run_focus_tasks.sh` 保留为兼容入口。

只解析配置、不创建 run：

```bash
bash tools/run/run_branch.sh --inspect branch.source=e011_gt_mask
```

正式创建训练 branch（运行前应同时给出有辨识度的 run name）：

```bash
bash tools/run/run_branch.sh \
  branch.source=e011_gt_mask \
  named_run.run_name=gt-mask-step1398-branch
```

使用其他兼容配置时，把 config 路径作为第一个参数；后面仍可继续传
`--inspect` 和 `key=value` overrides：

```bash
bash tools/run/run_branch.sh configs/sft/qwen3vl_8b_focus_tasks.py --inspect
```

## Legacy E-009 branch config

`configs/sft/e009_qwen3vl8b_1shot_branch.py` selects a parent config and one
of three isolated actions:

- `branch.action=train`: resume the parent checkpoint and train with runtime
  overrides;
- `branch.action=evaluate`: autoregressively generate boxes and save per-sample
  predictions plus parse rate, mIoU, and IoU-threshold accuracy;
- `branch.action=head_screen`: load adapter weights and run one standalone
  teacher-forced head screen without an optimizer step.

Changes below `runtime` are deep-merged onto `branch.parent_config`.  Command
line overrides use the same structure, for example
`runtime.runner.optimizer.lr=1e-5`.  Inspect composition without allocating a
run:

```bash
bash tools/run_e009_branch.sh --inspect \
  branch.action=evaluate \
  branch.parent_config=qwen3vl_8b_lora_focus_1shot_ddp4_4bit.py
```

The unified E-009 template now adds a frozen `test_dataloader` backed by
`val_lasot_fixed35_1shot_focus.json`: 700 sequences from the 35-category
complement of the project-frozen LaSOT training categories, with zero LaSOT
sequence overlap.  A bounded evaluation uses reproducible seeded-random
indices instead of the first manifest rows.  Set `evaluation.limit=None` to
evaluate all 700 validation sequences.

Examples (replace `<checkpoint>` with the directory containing `adapter/` and
`trainer_state.pt`):

```bash
# Autoregressive diagnostic evaluation; no optimizer step.
bash tools/run_e009_branch.sh \
  branch.action=evaluate \
  named_run.parent_checkpoint=<checkpoint> \
  named_run.run_name=eval-checkpoint-05 \
  evaluation.limit=100

# One standalone 100-sample head screen; no optimizer step.
bash tools/run_e009_branch.sh \
  branch.action=head_screen \
  named_run.parent_checkpoint=<checkpoint> \
  named_run.run_name=headscreen-checkpoint-05 \
  head_screening.probe.samples_per_screening=100

# New training branch with changed optimizer/runtime parameters.
bash tools/run_e009_branch.sh \
  branch.action=train \
  named_run.parent_checkpoint=<checkpoint> \
  named_run.run_name=lr1e5-epoch2 \
  runtime.runner.optimizer.lr=1e-5 \
  runtime.runner.max_epochs=2

# New training branch plus two head screens per epoch.
bash tools/run_e009_branch.sh \
  branch.action=train \
  branch.periodic_head_screening=True \
  named_run.parent_checkpoint=<checkpoint> \
  named_run.run_name=train-with-headscreen
```

Each run family is grouped below its root run.  Descendants stay flat inside
the root's `branches/` directory instead of recursively nesting by generation:

```text
experiments/E-009/<root run>/
  checkpoints/
  branches/
    <UTC timestamp>--<run name>/
      run_manifest.json
      events.jsonl
      logs/train.log
      checkpoints/
      head_screening/
      metrics.json
```

`experiments/E-009/run_index.jsonl` is an append-only experiment index.  Each
event records `run_id`, status, run kind, parent run, parent checkpoint, root
run and lineage generation.  `run_manifest.json` is the current per-run view.
Existing non-named runs remain the family root and are indexed as
`legacy-root` when their first child is prepared.  Their derived runs are
placed under `branches/`; existing logs, checkpoints, and configuration are
not rewritten.

## New branch from a checkpoint

Use `mode=new`; this creates a different timestamped directory and restores
weights and optimizer state from the parent checkpoint without writing into
the parent run:

```bash
bash tools/train_focus_1shot_ddp4_4bit_named.sh \
  named_run.run_name=loss-ablation-checkpoint-05 \
  named_run.run_kind=branch-train-loss-ablation \
  named_run.parent_checkpoint=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/<checkpoint>
```

For the training-plus-head-screening branch:

```bash
bash tools/train_focus_1shot_ddp4_4bit_head_screening.sh \
  named_run.run_name=headscreen-n100-checkpoint-05 \
  named_run.parent_checkpoint=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-focus-qwen3vl8b-lora-1shot-nf4-ddp4/checkpoints/<checkpoint>
```

Choose a meaningful `run_kind`, for example `branch-train-loss-ablation`,
`validation-only`, or `head-screen-only`.  The name is descriptive; the UTC
timestamp is generated automatically.

## Continue the same named run

Use `mode=resume` only when the checkpoint belongs to the same named run.  It
keeps the original work directory and therefore intentionally appends its log:

```bash
bash tools/train_focus_1shot_ddp4_4bit_head_screening.sh \
  named_run.mode=resume \
  named_run.run_dir=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/<named-run> \
  named_run.resume_checkpoint=/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/<named-run>/checkpoints/<checkpoint>
```

Trying to resume a different run in `mode=resume` fails closed.  Trying to
reuse a timestamp/run-name pair or overwrite an existing checkpoint directory
also fails closed.

## Inspect the index

```bash
python tools/named_run.py list --experiment-dir \
  /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009

python tools/named_run.py tree --experiment-dir \
  /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009
```

Config overrides passed to the launcher are saved in `run_manifest.json`, so
small loss, validation, or screening variants remain attributable.

### E-009 post-hoc combined held-out test

After checkpoint selection, the project-specific combined manifest is:

```text
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json
```

It combines LaSOT test600, GOT-10k official validation (180 episodes), and
TAO official validation (986 eligible videos). It has zero recorded sequence
and image overlap with `train_only_1shot_focus.json`, but is not the exact
IPLoc or FOCUS test split. Select it only by explicit
`runtime.test_dataloader.dataset.ann_file` override. Evaluation writes both
sample-weighted aggregate metrics and primary `by_dataset` metrics; do not
compare the aggregate directly with a paper table that averages datasets.
