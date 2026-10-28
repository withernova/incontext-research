# e014-selection-coordinates-only-lora4epoch-20261019-derived-001 · 用户明确要求评测当前无框原图+文字bbox选择器的step1310 checkpoint。固定原1766候选数据，与已有画框版本对照；使用exact_insta

- 父 Run：`e014-selection-coordinates-only-lora4epoch-20261019`
- 来源版本：2026-10-19T08:50:56
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确要求评测当前无框原图+文字bbox选择器的step1310 checkpoint。固定原1766候选数据，与已有画框版本对照；使用exact_instance但不draw-boxes，greedy16/EOS seed20260901 vision4096。仅评测明确指定step1310，不挑其他checkpoint。尚未授权停止父训练；检查checkpoint完整性和GPU占用后决定能否安全执行，不挤占正在训练资源。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --selector-checkpoint /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/payload/training/checkpoints/samples_00020947_step_001310 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py (existing no-config CLI)
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 791,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.7114867293845031,
      "vqa_iou_acc50": 0.7780294450736127,
      "score_iou_mean": 0.6916960157722533,
      "score_iou_acc50": 0.7553793884484711,
      "first_iou_mean": 0.656632485224866,
      "first_iou_acc50": 0.7151755379388448,
      "oracle_iou_mean": 0.7573992982137026,
      "oracle_iou_acc50": 0.8306908267270668,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 83,
      "worsens_score": 42,
      "fixes_score_miss": 67,
      "breaks_score_hit": 27,
      "oracle_hit_samples": 1467,
      "vqa_hit_given_oracle_hit": 0.9366053169734151
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "vqa_iou_mean": 0.6559350149400645,
      "vqa_iou_acc50": 0.7104930467762326,
      "score_iou_mean": 0.6117499324631576,
      "score_iou_acc50": 0.6599241466498104,
      "first_iou_mean": 0.5334665001664629,
      "first_iou_acc50": 0.5701643489254109,
      "oracle_iou_mean": 0.7584401938937492,
      "oracle_iou_acc50": 0.8280657395701644,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 83,
      "worsens_score": 42,
      "fixes_score_miss": 67,
      "breaks_score_hit": 27,
      "oracle_hit_samples": 655,
      "vqa_hit_given_oracle_hit": 0.8580152671755725
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.8184653299686964,
        "vqa_iou_acc50": 0.8888888888888888,
        "score_iou_mean": 0.7959036041152275,
        "score_iou_acc50": 0.8611111111111112,
        "first_iou_mean": 0.782188525520559,
        "first_iou_acc50": 0.85,
        "oracle_iou_mean": 0.8462972143842374,
        "oracle_iou_acc50": 0.9222222222222223,
        "valid_vqa_answers": 51,
        "invalid_vqa_answers": 0,
        "improves_score": 5,
        "worsens_score": 1,
        "fixes_score_miss": 5,
        "breaks_score_hit": 0,
        "oracle_hit_samples": 166,
        "vqa_hit_given_oracle_hit": 0.963855421686747
      },
      "LaSOT": {
        "samples": 600,
        "vqa_iou_mean": 0.6740348891699394,
        "vqa_iou_acc50": 0.7583333333333333,
        "score_iou_mean": 0.6537116103330052,
        "score_iou_acc50": 0.7366666666666667,
        "first_iou_mean": 0.625383400920118,
        "first_iou_acc50": 0.7,
        "oracle_iou_mean": 0.7167223918508266,
        "oracle_iou_acc50": 0.8083333333333333,
        "valid_vqa_answers": 246,
        "invalid_vqa_answers": 0,
        "improves_score": 27,
        "worsens_score": 15,
        "fixes_score_miss": 22,
        "breaks_score_hit": 9,
        "oracle_hit_samples": 485,
        "vqa_hit_given_oracle_hit": 0.9381443298969072
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.714747333870896,
        "vqa_iou_acc50": 0.7697768762677485,
        "score_iou_mean": 0.6957865607639502,
        "score_iou_acc50": 0.7474645030425964,
        "first_iou_mean": 0.652727174200144,
        "first_iou_acc50": 0.6997971602434077,
        "oracle_iou_mean": 0.7659231510605866,
        "oracle_iou_acc50": 0.8275862068965517,
        "valid_vqa_answers": 494,
        "invalid_vqa_answers": 0,
        "improves_score": 51,
        "worsens_score": 26,
        "fixes_score_miss": 40,
        "breaks_score_hit": 18,
        "oracle_hit_samples": 816,
        "vqa_hit_given_oracle_hit": 0.9301470588235294
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "original",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "selection_lora_bfloat16",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "selector_checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019/payload/training/checkpoints/samples_00020947_step_001310",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  },
  {
    "metric_id": "settings",
    "value": {
      "seed": 20260901,
      "max_new_tokens": 16,
      "vision_max_patch_tokens": 4096,
      "do_sample": false,
      "require_eos": true
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 17 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
只评测用户指定1310，不选择其它checkpoint；同测试已反复探索，不是无偏测试。与画框step2095训练预算不同，warmup不同，不能单独归因无框。父训练中止1374/2096不是4epoch完成。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-coordinates-only-lora4epoch-20261019-derived-001/managed_console.log

### 审核入口
.pi/analysis/e014/selection-sft/coordinates_only_step1310_eval_audit.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
