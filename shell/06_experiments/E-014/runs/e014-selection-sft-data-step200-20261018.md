# e014-selection-sft-data-step200-20261018 · 用户授权独立画框选择LoRA训练的必要数据阶段：从现有2000正训练对排除与1766评测集同身份/原视频来源（只读审计59）后约1941，以原视频/序列seed

- 父 Run：`e014-score04-step200-native-vqa-drawn1766-20261018`
- 来源版本：2026-10-18T12:15:17
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户授权独立画框选择LoRA训练的必要数据阶段：从现有2000正训练对排除与1766评测集同身份/原视频来源（只读审计59）后约1941，以原视频/序列seed20260901固定15%内部验证。用冻结score0.4/G4/step200 checkpoint在剩余训练来源生成候选（boxes_then_scores_v1 greedy192 EOS vision4096，8GPU），保留数据分组；只将多框Oracle>=.5且领先次优>.05的样本制成画框编号SFT，随机基础排列+全部循环移位，验证组不增强。仅数据准备与候选推理，不更新任何权重；保存输入/生成/过滤/渲染/SHA。后续独立fresh LoRA一epoch训练，不恢复GRPO，不从测试集构造SFT。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：bash -c 'set -euo pipefail; export PYTHONPATH=. OMP_NUM_THREADS=1 IPLOC_PYTHON=/songzhengyue/miniconda3/envs/IPLoc/bin/python; /songzhengyue/miniconda3/envs/IPLoc/bin/python tools/prepare_candidate_selection.py manifest --source /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/overnight-train-2k/trainable_pairs.json --source-sha256 017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130 --exclude-manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --exclude-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --path-map /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/dataset=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/dataset --validation-fraction 0.15 --seed 20260901 --output /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/inputs; MH=$(sha256sum /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/inputs/manifest.json); MH=${MH%% *}; bash tools/run.sh configs/eval/variable_candidates.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/generation model.model_path=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct test_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/inputs/manifest.json test_dataloader.dataset.ann_file_sha256=$MH test_dataloader.dataset.prompt_variant=boxes_then_scores_v1 evaluator.prompt_variant=boxes_then_scores_v1 evaluation.checkpoint=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/20261015-172638__discovery-priority__score0.4-selected0.2-coverage0.5__kl0__sft659__200step__seed11451/payload/grpo/checkpoints/step_000200 evaluation.require_eos=True evaluation.seed=20260901; PH=$(sha256sum /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/generation/evaluation/predictions.jsonl); PH=${PH%% *}; /songzhengyue/miniconda3/envs/IPLoc/bin/python tools/prepare_candidate_selection.py sft --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/inputs/manifest.json --manifest-sha256 $MH --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/generation/evaluation/predictions.jsonl --predictions-sha256 $PH --seed 20260901 --min-oracle 0.5 --min-gap 0.05 --output /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/selection_data; cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/selection_data/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json; echo SURVEY_TOOL_RUN_COMPLETE'
- 代码版本：a45d11a9c1ebe9953e7f4522eb463cef9650db02
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json

## 结果
数据阶段exit0完成，1941候选生成覆盖完整。过滤后501唯一训练源/361groups，重排增强1152例；115唯一验证源/72groups，不与训练group交叠。按global batch16一epoch对应72更新。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "source_samples",
    "value": 1941,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "eligible_sources",
    "value": {
      "train": 501,
      "validation": 115
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "examples",
    "value": {
      "train": 1152,
      "validation": 115
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "rejected",
    "value": {
      "train:fewer_than_two": 1060,
      "validation:fewer_than_two": 211,
      "train:oracle_below_threshold": 43,
      "validation:oracle_below_threshold": 7,
      "train:ambiguous_best": 3,
      "validation:ambiguous_best": 1
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "manifest_hashes",
    "value": {
      "train": "89dda90ab573b0305bf02f5e0c302c59812b6438428008e8a95f1a0009481403",
      "validation": "1da387d5fa297bb31a462541732eafa7f2a5b2a8c915969142cab5d0eb9d24c7"
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "validation_samples",
    "value": 334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "validation_multi",
    "value": 123,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "validation_manifest_sha256",
    "value": "65fa13a466f819b5c25a2d641c8996c280be107c1229970bba670efa8987454c",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "validation_predictions_sha256",
    "value": "7064e524fc57a66243329e7d5bfd8489544d4338e0f7b90cdc02bb47cbf648c1",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "69e09a47c592803ce03894e2b6ed37b90af48a4556be93a52fe04b0773612add",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "f2a4c201f8bf508278681bc27115376f8577619bace6166a5874e18024681615",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "min_oracle",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "min_gap",
    "value": 0.05,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "seed",
    "value": 20260901,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "3a67c77b2e548f255f1b891ece30a5ab3d42fa527958fac9f868aa8cfe88a27f",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "rotation_policy",
    "value": "random base permutation plus all cyclic rotations in train; one shuffled validation order",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  },
  {
    "metric_id": "dataset_counts",
    "value": {
      "train": {
        "GOT10k": 1027,
        "LaSOT": 125
      },
      "validation": {
        "LaSOT": 9,
        "GOT10k": 106
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 18 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
训练数据来源没有新增评测原视频重叠，但固定生成器过去曾见部分同源视频，不能宣称整链无泄漏泛化。无TAO训练来源，属选择器诊断。保持GRPO停止。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/managed_console.log

### 审核入口
.pi/analysis/e014/selection-sft/data_integrity_audit.json

### 过程记录
当前仅数据验收任务，不提前启动后续训练。信号exit0仅触发核验；第一次managed complete因稳定观察门禁未满足，后续复核关闭。证据.pi/analysis/e014/selection-sft/data_integrity_audit.json，全部源/结果SHA及渲染哈希汇总在内。此为产物完整性检查，不是额外测试或模型推理。固定候选生成器曾接触部分评测同源视频，因此不宣称完整链条无泄漏泛化；无TAO训练，Claim不改。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
