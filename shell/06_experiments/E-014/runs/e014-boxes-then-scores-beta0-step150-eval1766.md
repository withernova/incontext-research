# e014-boxes-then-scores-beta0-step150-eval1766 · 用户要求停止本次训练并评测step150。独立1766评测，boxes_then_scores_v1、require_eos、greedy192、vision4

- 父 Run：`e014-boxes-then-scores-beta0-sft659-seed11451`
- 来源版本：2026-10-15T15:14:21
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户要求停止本次训练并评测step150。独立1766评测，boxes_then_scores_v1、require_eos、greedy192、vision4096、seed20260901，复用新协议step0评测入口；只替换checkpoint与独立产物路径，不恢复训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：原训练主动停止于8rank共同184；checkpoint150 optimizer.steps=150，完整非空稳定文件核验，policy SHA256=fad960526f97d6642cd84cbb8e31c9a5d929a9b45c2566933be039fdb93fda14。复用新协议step0通用入口，CLI仅替换step150 checkpoint/adapter子目录及独立路径。1766/greedy192/vision4096/seed20260901/require_eos/boxes_then_scores_v1不变；训练来源beta0、两种补偿0。无源码修改、未测试、不自动恢复训练，不持续监控。
- 命令：env HF_HOME=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/cache/huggingface TORCH_HOME=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/cache/torch XDG_CACHE_HOME=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/cache/xdg TRITON_CACHE_DIR=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/cache/triton bash tools/run.sh configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py --cfg-options work_dir=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload test_dataloader.dataset.ann_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/inputs/manifest.json evaluation.inputs_file=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/inputs/inputs.json evaluation.checkpoint=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000150 evaluation.adapter_subdir=adapter/policy evaluation.expected_inputs.checkpoint=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000150 evaluation.expected_inputs.step=150
- 代码版本：41698665d15742276bf22d1376e8d53a367c07db
- 随机种子：20260901
- 配置：configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000150",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 1047.1524307727814,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 1.686478442013185,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 0.9994337485843715,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.7001492194085729,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.8057757644394111,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.7695356738391846,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.6715741789354474,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 1766,
      "min": 0.0,
      "q25": 0.5567538710604685,
      "median": 0.8823529411764706,
      "q75": 0.9609108356498974,
      "max": 1.0,
      "bins": {
        "[0.00,0.10)": 315,
        "[0.10,0.25)": 28,
        "[0.25,0.50)": 64,
        "[0.50,0.75)": 173,
        "[0.75,1.00]": 1186
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 0.9994337485843715,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_output_layout",
    "value": "boxes_then_scores",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "0": 1,
      "1": 1765
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 0.9994337485843715,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.7001492194085729,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.7001492194085729,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 0.9994337485843715,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "parse_rate": 1.0,
        "miou": 0.8088895906335798,
        "acc_iou_0.25": 0.9222222222222223,
        "acc_iou_0.5": 0.8944444444444445,
        "acc_iou_0.75": 0.7888888888888889,
        "iou_distribution": {
          "count": 180,
          "min": 0.0,
          "q25": 0.7835593766908463,
          "median": 0.9209178356186712,
          "q75": 0.9610051212631014,
          "max": 0.9954025932332088,
          "bins": {
            "[0.00,0.10)": 13,
            "[0.10,0.25)": 1,
            "[0.25,0.50)": 5,
            "[0.50,0.75)": 19,
            "[0.75,1.00]": 142
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 180
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.8088895906335798,
        "oracle_miou": 0.8088895906335798,
        "oracle_gap": 0.0,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 1.0,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": null,
        "nonfirst_acc_samples": 0,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "LaSOT": {
        "samples": 600,
        "parse_rate": 1.0,
        "miou": 0.6621054099781741,
        "acc_iou_0.25": 0.8066666666666666,
        "acc_iou_0.5": 0.7466666666666667,
        "acc_iou_0.75": 0.5966666666666667,
        "iou_distribution": {
          "count": 600,
          "min": 0.0,
          "q25": 0.48554082599231885,
          "median": 0.8253426188399657,
          "q75": 0.9257917322084264,
          "max": 0.9911647804364135,
          "bins": {
            "[0.00,0.10)": 104,
            "[0.10,0.25)": 12,
            "[0.25,0.50)": 36,
            "[0.50,0.75)": 90,
            "[0.75,1.00]": 358
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 600
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.6621054099781741,
        "oracle_miou": 0.6621054099781741,
        "oracle_gap": 0.0,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 1.0,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": null,
        "nonfirst_acc_samples": 0,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "TAO": {
        "samples": 986,
        "parse_rate": 0.9989858012170385,
        "miou": 0.7034484271547545,
        "acc_iou_0.25": 0.783975659229209,
        "acc_iou_0.5": 0.7606490872210954,
        "acc_iou_0.75": 0.6957403651115619,
        "iou_distribution": {
          "count": 986,
          "min": 0.0,
          "q25": 0.5477265432941907,
          "median": 0.9125699655117152,
          "q75": 0.9723584724469864,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 198,
            "[0.10,0.25)": 15,
            "[0.25,0.50)": 23,
            "[0.50,0.75)": 64,
            "[0.75,1.00]": 686
          }
        },
        "confidence_format_valid_rate": 0.9989858012170385,
        "confidence_invalid_count": 1,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 1,
          "1": 985
        },
        "variable_candidate_format_valid_rate": 0.9989858012170385,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.7034484271547545,
        "oracle_miou": 0.7034484271547545,
        "oracle_gap": 0.0,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 0.9989858012170385,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": null,
        "nonfirst_acc_samples": 0,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/payload/evaluation/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-step150-eval1766/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
