# e014-structure-score-iou-explore-v1-step150-eval1766 · 现在停止训练，然后开始150step的评测eval：训练已按请求停止在154，评测本父Run保存step150（不是其他奖励训练checkpoint）；原176

- 父 Run：`e014-structure-score-iou-explore-v1-sft659-seed11451`
- 来源版本：2026-10-14T14:09:11
- 状态：analysis_pending
- Workspace：03

## 本次任务
现在停止训练，然后开始150step的评测eval：训练已按请求停止在154，评测本父Run保存step150（不是其他奖励训练checkpoint）；原1766查询/8GPU/multi_v2/greedy192/vision4096/seed20260901，独立新输出，不恢复训练，不覆盖历史产物。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：父训练按用户要求停止，8rank最后154；只评测保存step150。训练SHA1e2caec81668dafaf015005415d219b4e5e4ca2e，scheme structure_score_selected_iou_explore_v1/G4；policy SHA256=2d6b64aec234746230d820e7a4b112f4d23788b036485312a8ba7b2435b24379，读期间stat稳定。新薄配置预期7项新reward/G4/step150，复用现有explicit_binding Shell/tools.evaluate。原1766清单SHA48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b，只迁移image_path至只读alias；8GPU/multi_v2/greedy192/vision4096/eval seed20260901。评测代码指定部署SHAf394b5704a9a258f4863e0d525ca5ca0a2bdec3b，review295cedf073227cf9通过，AST/navigation/diff静态核验通过，未测试；现有必要执行preflight校验optimizer.steps150、GPU空闲、source hashes与prompt。不恢复训练、不覆盖产物，不自动重跑。
- 命令：env E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766 E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/checkpoints/step_000150 E014_EVAL_CONFIG=configs/experiments/E-014/evaluation/e014_structure_score_iou_explore_step150_eval1766.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=150 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh
- 代码版本：f394b5704a9a258f4863e0d525ca5ca0a2bdec3b
- 随机种子：20260901
- 配置：configs/experiments/E-014/evaluation/e014_structure_score_iou_explore_step150_eval1766.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/checkpoints/step_000150",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 992.9537997245789,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 1.7785318919065976,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.7092228483305837,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.8063420158550396,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.7740656851642129,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.6857304643261608,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 1766,
      "min": 0.0,
      "q25": 0.5997328154933423,
      "median": 0.8958163875135847,
      "q75": 0.9655819086890286,
      "max": 1.0,
      "bins": {
        "[0.00,0.10)": 312,
        "[0.10,0.25)": 30,
        "[0.25,0.50)": 57,
        "[0.50,0.75)": 156,
        "[0.75,1.00]": 1211
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "1": 1766
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.7092228483305837,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.7092228483305837,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "parse_rate": 1.0,
        "miou": 0.8259323469072759,
        "acc_iou_0.25": 0.9388888888888889,
        "acc_iou_0.5": 0.9111111111111111,
        "acc_iou_0.75": 0.8055555555555556,
        "iou_distribution": {
          "count": 180,
          "min": 0.0,
          "q25": 0.7916439831404373,
          "median": 0.9345991541729692,
          "q75": 0.9675658976857306,
          "max": 0.9944165170556553,
          "bins": {
            "[0.00,0.10)": 11,
            "[0.10,0.25)": 0,
            "[0.25,0.50)": 5,
            "[0.50,0.75)": 19,
            "[0.75,1.00]": 145
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 180
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.8259323469072759,
        "oracle_miou": 0.8259323469072759,
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
        "miou": 0.6545581450183459,
        "acc_iou_0.25": 0.7833333333333333,
        "acc_iou_0.5": 0.7316666666666667,
        "acc_iou_0.75": 0.605,
        "iou_distribution": {
          "count": 600,
          "min": 0.0,
          "q25": 0.4402592832873338,
          "median": 0.8289760189654671,
          "q75": 0.9342814660249658,
          "max": 0.9966572691485192,
          "bins": {
            "[0.00,0.10)": 111,
            "[0.10,0.25)": 19,
            "[0.25,0.50)": 31,
            "[0.50,0.75)": 76,
            "[0.75,1.00]": 363
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 600
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.6545581450183459,
        "oracle_miou": 0.6545581450183459,
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
        "parse_rate": 1.0,
        "miou": 0.721181380017745,
        "acc_iou_0.25": 0.7961460446247465,
        "acc_iou_0.5": 0.7748478701825557,
        "acc_iou_0.75": 0.7129817444219066,
        "iou_distribution": {
          "count": 986,
          "min": 0.0,
          "q25": 0.6336817333116898,
          "median": 0.9258816232500443,
          "q75": 0.9753115523116126,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 190,
            "[0.10,0.25)": 11,
            "[0.25,0.50)": 21,
            "[0.50,0.75)": 61,
            "[0.75,1.00]": 703
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 986
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.721181380017745,
        "oracle_miou": 0.721181380017745,
        "oracle_gap": 0.0,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 1.0,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": null,
        "nonfirst_acc_samples": 0,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "input_provenance",
    "value": {
      "source_sha256": {
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json": "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/checkpoints/step_000150/adapter/policy/adapter_config.json": "025b5e8180341469d1fc93319f02ae2be67733f62b16dcaef41aaaf354e096a7",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/checkpoints/step_000150/adapter/policy/adapter_model.safetensors": "2d6b64aec234746230d820e7a4b112f4d23788b036485312a8ba7b2435b24379",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/checkpoints/step_000150/optimizer.pt": "7c0e41f71d266db9d13bbb3c892e8cb5b827b301a559a9ff92442673ad6bd1f4",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/config_snapshot.json": "d5d5baaa063a5942ae1c6ad668d358c73890cfada1f56198b630fb8b937cfcd8"
      },
      "derived_manifest_sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
      "expected_samples": 1766,
      "checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/payload/grpo/checkpoints/step_000150",
      "prompt_variant": "multi_v2",
      "prompt_sha256": "c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba",
      "step": 150,
      "training_reward": {
        "correctness_threshold": 0.5,
        "exploration_threshold": 0.3,
        "distinct_threshold": 0.9,
        "score_weight": 1.1,
        "iou_weight": 1.0,
        "order_penalty": 0.12,
        "exploration_penalty": 0.2
      },
      "training_group_size": 4
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "valid_gt_ap",
    "value": {
      "AP25": 0.741951350550596,
      "AP50": 0.700388912690472,
      "AP75": 0.5750203907331239,
      "AP50_95_all_points": 0.5301861264186758,
      "samples": 1756,
      "invalid_predictions": 0
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "legacy_all_query_ap",
    "value": {
      "AP25": 0.7366569291766549,
      "AP50": 0.6954252724153757,
      "AP75": 0.5709873014186733,
      "AP50_95_all_points": 0.526461692600565,
      "samples": 1766,
      "invalid_predictions": 0
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Previously viewed test set; exploratory checkpoint diagnosis, no matched baseline. AP uses the final score-selected box, not full detection AP.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 43 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-step150-eval1766/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
