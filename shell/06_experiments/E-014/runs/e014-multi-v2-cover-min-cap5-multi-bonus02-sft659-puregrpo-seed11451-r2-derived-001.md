# e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001 · 对 step150 的 ckpt 进行评测一下

- 父 Run：`e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2`
- 来源版本：2026-10-13T23:34:27.083208
- 状态：analysis_pending
- Workspace：03

## 本次任务
对 step150 的 ckpt 进行评测一下

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：本r2 step150，optimizer.steps=150，multi_v2，训练multi_bonus_weight=0.2；greedy192/vision4096，评测seed20260901（父训练seed11451）。仅派生image_path至只读alias；独立payload不覆盖。日志使用根managed_console.log。未运行测试套件。
- 命令：bash tools/run/eval/e014/e014_multi_bonus02_r2_step150_eval1766_8gpu.sh
- 代码版本：090d81885ea22d934aecf3e0db386248b026a1a4
- 随机种子：11451
- 配置：configs/experiments/E-014/evaluation/e014_multi_bonus02_r2_step150_eval1766.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/payload/grpo/checkpoints/step_000150",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 1036.7345352172852,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 1.7034254575399776,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.7018657614736732,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.8029445073612684,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.7638731596828993,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.6789354473386183,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 1766,
      "min": 0.0,
      "q25": 0.5724513914746879,
      "median": 0.8895921825018538,
      "q75": 0.9617858731692633,
      "max": 1.0,
      "bins": {
        "[0.00,0.10)": 319,
        "[0.10,0.25)": 29,
        "[0.25,0.50)": 69,
        "[0.50,0.75)": 150,
        "[0.75,1.00]": 1199
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "1": 1652,
      "2": 104,
      "3": 7,
      "4": 3
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 1.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.06455266138165346,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.7018657614736732,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.7126411223176852,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.010775360844011983,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 0.9801812004530012,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 0.9801812004530012,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.0033975084937712344,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 25,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "parse_rate": 1.0,
        "miou": 0.8153337748613806,
        "acc_iou_0.25": 0.9277777777777778,
        "acc_iou_0.5": 0.8944444444444445,
        "acc_iou_0.75": 0.7888888888888889,
        "iou_distribution": {
          "count": 180,
          "min": 0.0,
          "q25": 0.7827015701660152,
          "median": 0.9295299678838996,
          "q75": 0.9619933998071487,
          "max": 0.998,
          "bins": {
            "[0.00,0.10)": 12,
            "[0.10,0.25)": 1,
            "[0.25,0.50)": 6,
            "[0.50,0.75)": 19,
            "[0.75,1.00]": 142
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 171,
          "2": 9
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.05,
        "first_candidate_miou": 0.8153337748613806,
        "oracle_miou": 0.8206756552032611,
        "oracle_gap": 0.005341880341880545,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 0.9888888888888889,
        "spatial_order_valid_given_format": 0.9888888888888889,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 1,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "LaSOT": {
        "samples": 600,
        "parse_rate": 1.0,
        "miou": 0.6508799098011171,
        "acc_iou_0.25": 0.7866666666666666,
        "acc_iou_0.5": 0.7166666666666667,
        "acc_iou_0.75": 0.6066666666666667,
        "iou_distribution": {
          "count": 600,
          "min": 0.0,
          "q25": 0.43805833680410183,
          "median": 0.8229963534899423,
          "q75": 0.9284058973952336,
          "max": 0.9968102073365231,
          "bins": {
            "[0.00,0.10)": 113,
            "[0.10,0.25)": 15,
            "[0.25,0.50)": 42,
            "[0.50,0.75)": 66,
            "[0.75,1.00]": 364
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 565,
          "2": 32,
          "3": 2,
          "4": 1
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.058333333333333334,
        "first_candidate_miou": 0.6508799098011171,
        "oracle_miou": 0.6576580614215156,
        "oracle_gap": 0.00677815162039852,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 0.9833333333333333,
        "spatial_order_valid_given_format": 0.9833333333333333,
        "near_duplicate_rate": 0.0016666666666666668,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 6,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "TAO": {
        "samples": 986,
        "parse_rate": 1.0,
        "miou": 0.7121773929074924,
        "acc_iou_0.25": 0.7900608519269777,
        "acc_iou_0.5": 0.768762677484787,
        "acc_iou_0.75": 0.7028397565922921,
        "iou_distribution": {
          "count": 986,
          "min": 0.0,
          "q25": 0.6084421552555267,
          "median": 0.9217562298010864,
          "q75": 0.9723531685594069,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 194,
            "[0.10,0.25)": 13,
            "[0.25,0.50)": 21,
            "[0.50,0.75)": 65,
            "[0.75,1.00]": 693
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 916,
          "2": 63,
          "3": 5,
          "4": 2
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.07099391480730223,
        "first_candidate_miou": 0.7121773929074924,
        "oracle_miou": 0.7263770458656539,
        "oracle_gap": 0.014199652958161502,
        "selected_nonfirst_rate": 0.0,
        "spatial_order_valid_rate": 0.9766734279918864,
        "spatial_order_valid_given_format": 0.9766734279918864,
        "near_duplicate_rate": 0.005070993914807302,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 18,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "input_provenance",
    "value": {
      "source_sha256": {
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json": "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/payload/grpo/checkpoints/step_000150/adapter/policy/adapter_config.json": "025b5e8180341469d1fc93319f02ae2be67733f62b16dcaef41aaaf354e096a7",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/payload/grpo/checkpoints/step_000150/adapter/policy/adapter_model.safetensors": "6584172e28c45ce96e5f8a2b2e981bb1c34931d1e8af56b71f0c151f370467d5",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/payload/grpo/checkpoints/step_000150/optimizer.pt": "810ae4cfdef8229fd6e497a7783ef2b01723985443421dcc08d039d0d8e71027",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/payload/grpo/config_snapshot.json": "15fbcc7f765501f690e0db64f8d9aac131ece928d43ff88dccf180655ce9723b"
      },
      "derived_manifest_sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
      "expected_samples": 1766,
      "checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/payload/grpo/checkpoints/step_000150",
      "prompt_variant": "multi_v2",
      "prompt_sha256": "c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba",
      "step": 150,
      "training_reward": {
        "iou_threshold": 0.5,
        "loc_weight": 1.0,
        "cal_weight": 1.1,
        "neg_weight": 1.1,
        "duplicate_weight": 0.06,
        "duplicate_threshold": 0.9,
        "rank_weight": 0.6,
        "rank_margin": 0.1,
        "rank_iou_delta": 0.1,
        "order_weight": 0.12,
        "distractor_weight": 0.6,
        "coverage_weight": 1.0,
        "coverage_mode": "min",
        "count_soft_limit": 5,
        "count_weight": 0.05,
        "multi_bonus_weight": 0.2
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "valid_gt_ap",
    "value": {
      "AP25": 0.7235646587068025,
      "AP50": 0.6681398468764776,
      "AP75": 0.5436457839596058,
      "AP50_95_all_points": 0.5004090317304914,
      "samples": 1756,
      "invalid_predictions": 0
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "legacy_all_query_ap",
    "value": {
      "AP25": 0.7182665088586704,
      "AP50": 0.6632726294484984,
      "AP75": 0.5397099953673007,
      "AP50_95_all_points": 0.4967856909031501,
      "samples": 1766,
      "invalid_predictions": 0
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Previously viewed test set; exploratory checkpoint diagnosis, no matched baseline. AP uses the final score-selected box, not full detection AP.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json"
  }
]
```

### 分析
评测exit0，1766条indices和unique IDs完整；源SHA及实际prompt核验通过。Selected=First mIoU0.7018657614736732，Oracle0.7126411223176852，IoU>=.5为1349/1766。候选数1/2/3/4分别1652/104/7/3，多框114/1766。全部选首框：多框中64条首框score严格最高，50条首框并列最高。25条后续候选IoU更高，其中23条可将IoU<.5提升至>=.5，但score选择均未利用。多框子集Selected/Oracle mIoU=.6566238435459423/.8235474159189673；空间顺序合法79/114，6/114含近重复。

### 局限
单checkpoint、单训练seed、已看测试集；未做同预算无补偿配对对照，不能归因0.2奖励或证明总体性能提升。Oracle只用GT事后选框。多框子集是模型自选子集，不能与单框组直接作因果比较。继承的训练mixed组胜率不是此次greedy评测指标；本轮不提升Claim。

### Claim 边界
主诊断高且multi率下降支持Exploration瓶颈假设，但不能单独确定主要原因或排除Reward Design。该Run不自动validated Claim，不输出因果结论；工程complete不等于收益。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
