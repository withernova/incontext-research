# e014-structure-score-iou-explore-v1-beta0-step50-eval1766 · 刚刚的训练帮我停止，然后对step50的结果进行一个评测吧：停止当前KL=0新奖励父训练，独立评测其保存step50，原1766样本/8GPU/multi_v2

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-sft659-seed11451`
- 来源版本：2026-10-14T16:32:31
- 状态：analysis_pending
- Workspace：03

## 本次任务
刚刚的训练帮我停止，然后对step50的结果进行一个评测吧：停止当前KL=0新奖励父训练，独立评测其保存step50，原1766样本/8GPU/multi_v2/greedy192/vision4096/eval seed20260901；不使用beta.04父checkpoint，不恢复训练、不覆盖已有产物。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：当前KL0父训练按用户要求停在52，评测保存step50；source snapshot beta=0/new scheme/G4/multi_v2已核验，policy SHA256=d917925092923f0841ecc4cba74b7c8508bb80c95a4f17b3551a333e4fe0e18a，stat稳定，原训练SHAf394b5704a9a258f4863e0d525ca5ca0a2bdec3b。只新增继承原新reward评测配置的step50薄绑定和2导航，现有explicit_binding Shell/tools.evaluate复用。原1766清单hash48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b，只迁移image_path到只读dataset alias，不改GT/身份/split；8GPU/multi_v2/greedy192/vision4096/eval seed20260901。评测SHA599ed6809ba7b9fd36dde7e354605e56d306fbb5，review82abb33bc94855aa passing/current，AST/navigation/diff静态通过，未测试。必要preflight验证optimizer.steps50/源hash/空闲GPU/环境；outputs根与managed_console根，Shell独占payload/evaluation。父保持停止，不自动重跑，不混beta.04 checkpoint或Claim结论。
- 命令：env E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766 E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000050 E014_EVAL_CONFIG=configs/experiments/E-014/evaluation/e014_structure_score_iou_explore_beta0_step50_eval1766.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=50 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh
- 代码版本：599ed6809ba7b9fd36dde7e354605e56d306fbb5
- 随机种子：20260901
- 配置：configs/experiments/E-014/evaluation/e014_structure_score_iou_explore_beta0_step50_eval1766.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000050",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 987.8892512321472,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 1.7876497773382516,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 0.9966024915062288,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.6908383004445021,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.7950169875424689,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.7548131370328426,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.6579841449603624,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 1766,
      "min": 0.0,
      "q25": 0.5227379334239493,
      "median": 0.8870541604060542,
      "q75": 0.9609044725554646,
      "max": 1.0,
      "bins": {
        "[0.00,0.10)": 341,
        "[0.10,0.25)": 21,
        "[0.25,0.50)": 71,
        "[0.50,0.75)": 171,
        "[0.75,1.00]": 1162
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 0.9966024915062288,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 6,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "0": 6,
      "1": 1760
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 0.9966024915062288,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.6908383004445021,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.6908383004445021,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 0.9966024915062288,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "parse_rate": 1.0,
        "miou": 0.7889750318804484,
        "acc_iou_0.25": 0.9,
        "acc_iou_0.5": 0.85,
        "acc_iou_0.75": 0.7777777777777778,
        "iou_distribution": {
          "count": 180,
          "min": 0.0,
          "q25": 0.7747378708394791,
          "median": 0.9228437398329017,
          "q75": 0.9644304367561775,
          "max": 0.9931506849315068,
          "bins": {
            "[0.00,0.10)": 17,
            "[0.10,0.25)": 1,
            "[0.25,0.50)": 9,
            "[0.50,0.75)": 13,
            "[0.75,1.00]": 140
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
        "first_candidate_miou": 0.7889750318804484,
        "oracle_miou": 0.7889750318804484,
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
        "parse_rate": 0.995,
        "miou": 0.6453239844563612,
        "acc_iou_0.25": 0.785,
        "acc_iou_0.5": 0.7283333333333334,
        "acc_iou_0.75": 0.5816666666666667,
        "iou_distribution": {
          "count": 600,
          "min": 0.0,
          "q25": 0.4263865803403192,
          "median": 0.8105288762878564,
          "q75": 0.9289969336985568,
          "max": 0.9968102073365231,
          "bins": {
            "[0.00,0.10)": 120,
            "[0.10,0.25)": 9,
            "[0.25,0.50)": 34,
            "[0.50,0.75)": 88,
            "[0.75,1.00]": 349
          }
        },
        "confidence_format_valid_rate": 0.995,
        "confidence_invalid_count": 3,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 3,
          "1": 597
        },
        "variable_candidate_format_valid_rate": 0.995,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.6453239844563612,
        "oracle_miou": 0.6453239844563612,
        "oracle_gap": 0.0,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 0.995,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": null,
        "nonfirst_acc_samples": 0,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "TAO": {
        "samples": 986,
        "parse_rate": 0.9969574036511156,
        "miou": 0.7006192111284936,
        "acc_iou_0.25": 0.781947261663286,
        "acc_iou_0.5": 0.7535496957403651,
        "acc_iou_0.75": 0.6825557809330629,
        "iou_distribution": {
          "count": 986,
          "min": 0.0,
          "q25": 0.5271303927329469,
          "median": 0.9195796946576643,
          "q75": 0.9724948951082382,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 204,
            "[0.10,0.25)": 11,
            "[0.25,0.50)": 28,
            "[0.50,0.75)": 70,
            "[0.75,1.00]": 673
          }
        },
        "confidence_format_valid_rate": 0.9969574036511156,
        "confidence_invalid_count": 3,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 3,
          "1": 983
        },
        "variable_candidate_format_valid_rate": 0.9969574036511156,
        "multiple_candidate_rate": 0.0,
        "first_candidate_miou": 0.7006192111284936,
        "oracle_miou": 0.7006192111284936,
        "oracle_gap": 0.0,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 0.9969574036511156,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": null,
        "nonfirst_acc_samples": 0,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "input_provenance",
    "value": {
      "source_sha256": {
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json": "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000050/adapter/policy/adapter_config.json": "025b5e8180341469d1fc93319f02ae2be67733f62b16dcaef41aaaf354e096a7",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000050/adapter/policy/adapter_model.safetensors": "d917925092923f0841ecc4cba74b7c8508bb80c95a4f17b3551a333e4fe0e18a",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000050/optimizer.pt": "a1c2cccdeb4b0c9a8903add6bb4d27606f8a3db695a22f0c03f55e680520edda",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/config_snapshot.json": "b428b4e06a0d9f655053f5ac8126ec3453f495b17eafe2f41699d184cc690890"
      },
      "derived_manifest_sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
      "expected_samples": 1766,
      "checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/payload/grpo/checkpoints/step_000050",
      "prompt_variant": "multi_v2",
      "prompt_sha256": "c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba",
      "step": 50,
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
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "valid_gt_ap",
    "value": {
      "AP25": 0.7481587935455205,
      "AP50": 0.6972805141642067,
      "AP75": 0.5640933551033395,
      "AP50_95_all_points": 0.5283958428364377,
      "samples": 1756,
      "invalid_predictions": 5
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "legacy_all_query_ap",
    "value": {
      "AP25": 0.7430121980413933,
      "AP50": 0.6925672393629279,
      "AP75": 0.5603784195298663,
      "AP50_95_all_points": 0.5249008202347796,
      "samples": 1766,
      "invalid_predictions": 6
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Previously viewed test set; exploratory checkpoint diagnosis, no matched baseline. AP uses the final score-selected box, not full detection AP.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json"
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
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-step50-eval1766/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
