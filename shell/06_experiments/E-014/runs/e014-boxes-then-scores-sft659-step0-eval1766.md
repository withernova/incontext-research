# e014-boxes-then-scores-sft659-step0-eval1766 · 用户授权新协议先全部bbox后全部score；对原SFT659做新协议step0既有1766评测，作为随后新GRPO训练基线。使用新配置和实际EOS完整回答校验

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2`
- 来源版本：2026-10-15T09:23:21
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户授权新协议先全部bbox后全部score；对原SFT659做新协议step0既有1766评测，作为随后新GRPO训练基线。使用新配置和实际EOS完整回答校验，不恢复旧训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：新协议boxes_then_scores_v1：先所有bbox再按序score；解析/奖励/评测显式路由；原始序列重放不变；review3086e33f5f827fb4通过，静态检查通过，未测试。原SFT659新协议step0，1766条，greedy192/vision4096/EOS完整性；只迁移image_path，不改变身份GT/split。
- 命令：env HF_HOME=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/cache/huggingface TORCH_HOME=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/cache/torch XDG_CACHE_HOME=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/cache/xdg TRITON_CACHE_DIR=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/cache/triton bash tools/run.sh configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py
- 代码版本：41698665d15742276bf22d1376e8d53a367c07db
- 随机种子：20260901
- 配置：configs/experiments/E-014/evaluation/e014_boxes_then_scores_sft659_step0_eval1766.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/focus-confidence-sft/checkpoints/samples_00042136_step_000659",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 2774.6594824790955,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 0.6364744975560457,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 0.49037372593431483,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.410754205234509,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.45413363533408835,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.43997734994337484,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.40770101925254815,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 1766,
      "min": 0.0,
      "q25": 0.0,
      "median": 0.0,
      "q75": 0.9427041958546978,
      "max": 1.0,
      "bins": {
        "[0.00,0.10)": 951,
        "[0.10,0.25)": 13,
        "[0.25,0.50)": 25,
        "[0.50,0.75)": 57,
        "[0.75,1.00]": 720
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 0.49037372593431483,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 900,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_output_layout",
    "value": "boxes_then_scores",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "0": 900,
      "1": 428,
      "2": 388,
      "3": 37,
      "4": 11,
      "5": 1,
      "6": 1
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 0.49037372593431483,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.2480181200453001,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.4202643030761741,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.4307172873764207,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.01996308214191167,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.010758776896942242,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 0.41959229898074746,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 0.8556581986143187,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.11947904869762174,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 34,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "parse_rate": 0.6611111111111111,
        "miou": 0.5765655584580957,
        "acc_iou_0.25": 0.65,
        "acc_iou_0.5": 0.6277777777777778,
        "acc_iou_0.75": 0.5611111111111111,
        "iou_distribution": {
          "count": 180,
          "min": 0.0,
          "q25": 0.0,
          "median": 0.8574372176653837,
          "q75": 0.9585201372028119,
          "max": 0.9936626621378257,
          "bins": {
            "[0.00,0.10)": 62,
            "[0.10,0.25)": 1,
            "[0.25,0.50)": 4,
            "[0.50,0.75)": 12,
            "[0.75,1.00]": 101
          }
        },
        "confidence_format_valid_rate": 0.6611111111111111,
        "confidence_invalid_count": 61,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 61,
          "1": 82,
          "2": 32,
          "3": 4,
          "4": 1
        },
        "variable_candidate_format_valid_rate": 0.6611111111111111,
        "multiple_candidate_rate": 0.20555555555555555,
        "first_candidate_miou": 0.5765655584580957,
        "oracle_miou": 0.5858383321357298,
        "oracle_gap": 0.009272773677634127,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 0.6111111111111112,
        "spatial_order_valid_given_format": 0.9243697478991597,
        "near_duplicate_rate": 0.12777777777777777,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 4,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "LaSOT": {
        "samples": 600,
        "parse_rate": 0.49166666666666664,
        "miou": 0.3848142272202982,
        "acc_iou_0.25": 0.445,
        "acc_iou_0.5": 0.4216666666666667,
        "acc_iou_0.75": 0.37333333333333335,
        "iou_distribution": {
          "count": 600,
          "min": 0.0,
          "q25": 0.0,
          "median": 0.0,
          "q75": 0.9013738320849429,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 324,
            "[0.10,0.25)": 9,
            "[0.25,0.50)": 14,
            "[0.50,0.75)": 29,
            "[0.75,1.00]": 224
          }
        },
        "confidence_format_valid_rate": 0.49166666666666664,
        "confidence_invalid_count": 305,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 305,
          "1": 132,
          "2": 148,
          "3": 10,
          "4": 5
        },
        "variable_candidate_format_valid_rate": 0.49166666666666664,
        "multiple_candidate_rate": 0.27166666666666667,
        "first_candidate_miou": 0.4006013622656091,
        "oracle_miou": 0.4108901593118331,
        "oracle_gap": 0.026075932091534915,
        "selected_nonfirst_rate": 0.018333333333333333,
        "spatial_order_valid_rate": 0.4216666666666667,
        "spatial_order_valid_given_format": 0.8576271186440678,
        "near_duplicate_rate": 0.15666666666666668,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 15,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "TAO": {
        "samples": 986,
        "parse_rate": 0.45841784989858014,
        "miou": 0.3962693606384463,
        "acc_iou_0.25": 0.4239350912778905,
        "acc_iou_0.5": 0.41683569979716023,
        "acc_iou_0.75": 0.40060851926977686,
        "iou_distribution": {
          "count": 986,
          "min": 0.0,
          "q25": 0.0,
          "median": 0.0,
          "q75": 0.9621371808566648,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 565,
            "[0.10,0.25)": 3,
            "[0.25,0.50)": 7,
            "[0.50,0.75)": 16,
            "[0.75,1.00]": 395
          }
        },
        "confidence_format_valid_rate": 0.45841784989858014,
        "confidence_invalid_count": 534,
        "candidate_selection": "highest_score_then_first",
        "candidate_output_layout": "boxes_then_scores",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 534,
          "1": 214,
          "2": 208,
          "3": 23,
          "4": 5,
          "5": 1,
          "6": 1
        },
        "variable_candidate_format_valid_rate": 0.45841784989858014,
        "multiple_candidate_rate": 0.2413793103448276,
        "first_candidate_miou": 0.40369588372282156,
        "oracle_miou": 0.4144642334028691,
        "oracle_gap": 0.018194872764422776,
        "selected_nonfirst_rate": 0.008113590263691683,
        "spatial_order_valid_rate": 0.38336713995943206,
        "spatial_order_valid_given_format": 0.8362831858407079,
        "near_duplicate_rate": 0.09533468559837728,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 15,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json"
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
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/payload/evaluation/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-sft659-step0-eval1766/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
