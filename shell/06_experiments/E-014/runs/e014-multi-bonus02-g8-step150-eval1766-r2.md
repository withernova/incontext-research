# e014-multi-bonus02-g8-step150-eval1766-r2 · 用户明确要求“修正然后评测”，授权修正前次output_dir布局错误后一次新评测。保留失败父Run全部产物，新Run根级outputs为canonical o

- 父 Run：`e014-multi-bonus02-g8-step150-eval1766`
- 来源版本：2026-10-14T08:29:22
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确要求“修正然后评测”，授权修正前次output_dir布局错误后一次新评测。保留失败父Run全部产物，新Run根级outputs为canonical output_dir，根级managed_console.log为log，worker独占payload/evaluation。评测原训练e014-multi-bonus02-g8-sft659-seed11451保存step150，checkpoint policy SHA256=2b1b5343ce77087401fb3bdf2be1dccce5cead814d94f0b006f350c4ab214936；G8/multi_v2/bonus.2。原1766样本/8GPU/greedy192/vision4096/evaluation.seed20260901不变；复用原Shell和worker，薄配置只换新输出绑定。训练已停154但仅评测150，不恢复训练、不启动step400、不改奖励或覆盖历史。核验结果后报告First/Selected/Oracle及评分诊断。本次若再失败保留产物不自动重试。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户本次授权一次重试；changed_config=canonical output_dir从payload/evaluation改outputs；changed_input=全新r2 Run输出身份。共享Shell仍独占创建payload，worker实际产物payload/evaluation。review9b229d52a506b1e7通过；指定26e35eee07dfc1d6274b594005b984d647822017已部署。导航/AST/diff静态通过，未suite/build/import/smoke。
- 命令：E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2 E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000150 E014_EVAL_CONFIG=configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step150_eval1766_r2.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=150 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh
- 代码版本：26e35eee07dfc1d6274b594005b984d647822017
- 随机种子：11451
- 配置：configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step150_eval1766_r2.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json

## 结果
exit0且1766覆盖/来源/配置核验通过，09:03:18 managed complete。First/Selected/Oracle mIoU=.697745657/.702426486/.715262965；Selected较First+0.468个百分点。合法多候选88/1766，非首选择24（15改善/6变差/3持平）。训练1..150共19200rollouts/2400G8组；collage多框率54.82→87.13→89.89%，original正13.85→13.43→4.36%、负15.01→10.05→3.07%，不是整体持续消失。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000150",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 1006.9558997154236,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 1.7538007379460117,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 0.9994337485843715,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.7024264856496789,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.8001132502831257,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.7633069082672707,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.67440543601359,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 1766,
      "min": 0.0,
      "q25": 0.5659909172209961,
      "median": 0.8935407615515671,
      "q75": 0.9636544870877096,
      "max": 1.0,
      "bins": {
        "[0.00,0.10)": 324,
        "[0.10,0.25)": 29,
        "[0.25,0.50)": 65,
        "[0.50,0.75)": 157,
        "[0.75,1.00]": 1191
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 0.9994337485843715,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "0": 1,
      "1": 1677,
      "2": 79,
      "3": 7,
      "4": 2
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 0.9994337485843715,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.04983012457531144,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.6977456567462618,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.7152629647612924,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.012836479111613452,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.013590033975084938,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 0.9920724801812004,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 0.9926345609065156,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": 0.39473684210526316,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 38,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "parse_rate": 1.0,
        "miou": 0.80923299537604,
        "acc_iou_0.25": 0.9166666666666666,
        "acc_iou_0.5": 0.8833333333333333,
        "acc_iou_0.75": 0.7888888888888889,
        "iou_distribution": {
          "count": 180,
          "min": 0.0,
          "q25": 0.7937989219068836,
          "median": 0.9284714832523363,
          "q75": 0.9649095437338376,
          "max": 0.9944165170556553,
          "bins": {
            "[0.00,0.10)": 13,
            "[0.10,0.25)": 2,
            "[0.25,0.50)": 6,
            "[0.50,0.75)": 17,
            "[0.75,1.00]": 142
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 175,
          "2": 4,
          "3": 1
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.027777777777777776,
        "first_candidate_miou": 0.7998700528319701,
        "oracle_miou": 0.8123364980271743,
        "oracle_gap": 0.003103502651134349,
        "selected_nonfirst_rate": 0.011111111111111112,
        "spatial_order_valid_rate": 1.0,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": 0.6666666666666666,
        "nonfirst_acc_samples": 3,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "LaSOT": {
        "samples": 600,
        "parse_rate": 0.9983333333333333,
        "miou": 0.6501230285480092,
        "acc_iou_0.25": 0.78,
        "acc_iou_0.5": 0.7233333333333334,
        "acc_iou_0.75": 0.5916666666666667,
        "iou_distribution": {
          "count": 600,
          "min": 0.0,
          "q25": 0.4220866336914687,
          "median": 0.8289479199726935,
          "q75": 0.9318449885604289,
          "max": 0.9987789987789988,
          "bins": {
            "[0.00,0.10)": 115,
            "[0.10,0.25)": 17,
            "[0.25,0.50)": 34,
            "[0.50,0.75)": 79,
            "[0.75,1.00]": 355
          }
        },
        "confidence_format_valid_rate": 0.9983333333333333,
        "confidence_invalid_count": 1,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 1,
          "1": 570,
          "2": 28,
          "4": 1
        },
        "variable_candidate_format_valid_rate": 0.9983333333333333,
        "multiple_candidate_rate": 0.04833333333333333,
        "first_candidate_miou": 0.6515863779279107,
        "oracle_miou": 0.6673736336705997,
        "oracle_gap": 0.017250605122590468,
        "selected_nonfirst_rate": 0.013333333333333334,
        "spatial_order_valid_rate": 0.9933333333333333,
        "spatial_order_valid_given_format": 0.994991652754591,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": 0.25,
        "nonfirst_acc_samples": 12,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "TAO": {
        "samples": 986,
        "parse_rate": 1.0,
        "miou": 0.7147560013801613,
        "acc_iou_0.25": 0.7910750507099391,
        "acc_iou_0.5": 0.7657200811359026,
        "acc_iou_0.75": 0.7038539553752535,
        "iou_distribution": {
          "count": 986,
          "min": 0.0,
          "q25": 0.6173658065210861,
          "median": 0.9279054301983722,
          "q75": 0.9754562340354253,
          "max": 1.0,
          "bins": {
            "[0.00,0.10)": 196,
            "[0.10,0.25)": 10,
            "[0.25,0.50)": 25,
            "[0.50,0.75)": 61,
            "[0.75,1.00]": 694
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "1": 932,
          "2": 47,
          "3": 6,
          "4": 1
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 0.05476673427991886,
        "first_candidate_miou": 0.7071910685064868,
        "oracle_miou": 0.7266832108734178,
        "oracle_gap": 0.011927209493256541,
        "selected_nonfirst_rate": 0.014198782961460446,
        "spatial_order_valid_rate": 0.9898580121703854,
        "spatial_order_valid_given_format": 0.9898580121703854,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": 0.43478260869565216,
        "nonfirst_acc_samples": 23,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "input_provenance",
    "value": {
      "source_sha256": {
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json": "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000150/adapter/policy/adapter_config.json": "025b5e8180341469d1fc93319f02ae2be67733f62b16dcaef41aaaf354e096a7",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000150/adapter/policy/adapter_model.safetensors": "2b1b5343ce77087401fb3bdf2be1dccce5cead814d94f0b006f350c4ab214936",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000150/optimizer.pt": "01d49aa67732d955a5ffefa79fff0cab94dc4ba9b7d953bb320a8c2ab947bcaf",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/config_snapshot.json": "39e07d685717a6df37ad1a1be3333e754d470a3a23e798934f49ecde5d398cfa"
      },
      "derived_manifest_sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
      "expected_samples": 1766,
      "checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000150",
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
      },
      "training_group_size": 8
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "valid_gt_ap",
    "value": {
      "AP25": 0.708913249689,
      "AP50": 0.6540873246464134,
      "AP75": 0.518893202297473,
      "AP50_95_all_points": 0.48731771815465236,
      "samples": 1756,
      "invalid_predictions": 1
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "legacy_all_query_ap",
    "value": {
      "AP25": 0.703463848447071,
      "AP50": 0.6490912452584408,
      "AP75": 0.5149467609869521,
      "AP50_95_all_points": 0.4836112042815448,
      "samples": 1766,
      "invalid_predictions": 1
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Previously viewed test set; exploratory checkpoint diagnosis, no matched baseline. AP uses the final score-selected box, not full detection AP.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json"
  }
]
```

### 分析
# G8 step150：1766样本评测与训练日志诊断

## 结论

- 本次评测已完成。退出码0，1766条输出覆盖完整，来源哈希及实际配置通过核验。受管 complete 于2026-10-14 09:03:18成功。
- 分数选择开始产生实际收益：Selected mIoU为70.243%，First为69.775%，差值为+0.468个百分点。但Oracle为71.526%，仍有1.284个百分点的选择差距。
- 不能把本次训练描述为“多框整体持续消失”。训练collage多框率由54.82%升至89.89%；原始正、负输入的多框率下降。必须按输入条件区分。
- 这是单seed、已查看测试集上的诊断。没有因果结论，也没有Claim升级。

## 执行与完整性

- Run：`e014-multi-bonus02-g8-step150-eval1766-r2`。
- 来源训练：`e014-multi-bonus02-g8-sft659-seed11451`。
- 来源checkpoint：`payload/grpo/checkpoints/step_000150`。先前已读取`optimizer.steps=150`。
- 训练8个rank实际完成154更新，随后按用户要求停止。151–154未保存为本评测checkpoint，也不进入本报告的训练诊断。
- 部署及实际快照SHA：`26e35eee07dfc1d6274b594005b984d647822017`；代码审阅：`9b229d52a506b1e7`。
- 配置：`configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step150_eval1766_r2.py`；复用现有`explicit_binding` Shell及`tools/evaluate.py`。
- 本次修正只涉及新Run输出身份。canonical输出目录为根级`outputs`，日志为根级`managed_console.log`。实际worker产物为`payload/evaluation`。失败旧Run未覆盖。
- 实际评测：8rank、greedy、192 new tokens、vision4096、seed20260901、multi_v2。顶层继承的11451是训练seed。
- 原1766=LaSOT600/GOT10k180/TAO986。只变更image_path别名，其余manifest字段逐条相等。
- 1766个唯一ID，dataset_index恰为0–1765。rank0–5各221条，rank6–7各220条。
- 5个只读来源哈希全部重新核验：原manifest、adapter配置、adapter权重、optimizer、训练配置快照。派生manifest及实际prompt哈希也一致。
- 指标稳定观测：09:00:50至09:03:17，9226 bytes及mtime相同。首次complete因稳定观测不足被拒绝；没有重跑评测，后续complete成功。
- 最终无GPU compute进程；训练退出码254对应用户停止。旧失败Run保留，step400评测目录不存在。训练不恢复。
- 源文件只读复制索引及SHA见`source_hashes.json`；实际核验见`integrity_audit.json`。原日志、checkpoint与结果未修改。

## 评测指标

Selected=最高score，并列取首。Oracle=GT事后最佳候选，不是可部署选择。全量指标分母1766，非法输出按现有评测器记IoU=0。

| 指标 | First | Selected | Oracle |
|---|---:|---:|---:|
| mIoU | 0.697745657 | 0.702426486 | 0.715262965 |
| IoU≥0.25 | 1405/1766 | 1413/1766 | 1438/1766 |
| IoU≥0.50 | 1339/1766 | 1348/1766 | 1374/1766 |
| IoU≥0.75 | 1180/1766 | 1191/1766 | 1212/1766 |

合法率：1765/1766（99.943%）。解析后的候选数0/1/2/3/4分别为1/1677/79/7/2。

原始文本中的完整answer-score对数1/2/3/4/6分别为1677/79/7/2/1。唯一非法样本为LaSOT index446：含6个完整对，随后第7个answer未闭合。不能把解析后的候选数0解释为原始模型没有输出框。未改生成预算、未重新推理该样本。

| 子集 | n | First mIoU | Selected mIoU | Oracle mIoU |
|---|---:|---:|---:|---:|
| LaSOT | 600 | 0.651586378 | 0.650123029 | 0.667373634 |
| GOT10k | 180 | 0.799870053 | 0.809232995 | 0.812336498 |
| TAO | 986 | 0.707191069 | 0.714756001 | 0.726683211 |
| 合法多候选 | 88 | 0.483127255 | 0.577062981 | 0.834667777 |

总平均收益不表示每个数据集都有收益：LaSOT的Selected低于First。

### 多候选评分诊断

- 合法多候选：88/1766（4.983%）。选择非首候选24/1766，亦为24/88。
- 这24次非首选择中，IoU比首框更高15次、更低6次、相同3次。全量Selected与First相同1745/1766。
- 多候选中，首框分数严格最高50/88，首框并列最高14/88；任意最高分并列15/88。
- 后续候选严格优于首框：38/88。Selected命中该非首Oracle为15/38。
- 多候选Selected与最早Oracle索引一致58/88；Selected达到Oracle IoU为59/88。两者差异来自IoU并列。
- 112个候选对中，16对IoU相同；其余96对中，score与IoU顺序一致54、相反24、score并列18。此处是候选对加权描述，不冒充样本等权统计。
- IoU≥0.5：Oracle相对First可挽救35个多候选样本；Selected挽救15个、损失6个，净增9个。
- 空间顺序合法75/88；近重复0/88（候选间IoU≥0.9）。全量空间顺序合法1752/1766。
- AP只是分数选定框的AP，不是完整检测AP。原始metrics同时保留valid-GT分母1756及legacy分母1766，不能互换。

完整逐项统计：`evaluation_audit.json`、`raw_candidate_audit.json`；源指标：`evaluation/metrics.json`。

## 训练日志：仅完成更新1–150

每个rank/update/sample_id为一个G8采样组。rollout.step从0开始，完成更新=step+1。仅取0–149，并与已有group记录及完成窗口交叉核验。

- 共19200 rollouts、2400组；每rank2400条/300组。每个更新每rank恰2组，每组恰8条。
- 逐组重算统计与2400条既有group记录一致；24个已完成rank窗口统计也一致。
- 排除151–154共512条rollouts。任何未完成采样组不进入统计。
- 合法多框8015/19200；非法252/19200。只在合法且终止的输出中定义single与multi。
- 总共462个mixed组，4818个multi×single比较对。

主诊断：每个mixed组先计算`q_g = sum[ R_multi > R_single ] / (n_multi*n_single)`，再对mixed组等权平均。使用实际total reward；严格大于和平局分开；不跨prompt、rank或更新配对。空分母输出null。下表的multi率分母包含非法输出。

| 完成更新 | multi/全部rollout | mixed/全部组 | q：组等权严格胜率 | 组等权平局率 | pooled严格胜率 | mean(multi)-mean(single) | multi正adv/全部multi |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1–50 | 2190/6400（34.219%） | 186/800 | 0.498768 | 0.016919 | 0.508162 | +0.022665 | 1273/2190 |
| 51–100 | 2995/6400（46.797%） | 130/800 | 0.388979 | 0.177047 | 0.377953 | +0.029865 | 1656/2995 |
| 101–150 | 2830/6400（44.219%） | 146/800 | 0.517213 | 0.103510 | 0.524310 | +0.109618 | 1765/2830 |

全1–150：q=0.473704，平局率0.089341，pooled胜率2291/4818=0.475509；组等权mean差+0.052170。best-multi严格胜best-single为250/462，并列57/462；multi正adv为4694/8015。全量multi率41.745%；合法输出内multi率8015/18948=42.300%。

### 条件分层

| 条件 | 窗口1–50 multi率 | 窗口51–100 multi率 | 窗口101–150 multi率 | 对应q序列 |
|---|---:|---:|---:|---|
| original positive | 226/1632（13.848%） | 230/1712（13.435%） | 74/1696（4.363%） | 0.335083 → 0.215476 → 0.283397 |
| original negative | 245/1632（15.012%） | 172/1712（10.047%） | 52/1696（3.066%） | 0.219220 → 0.088676 → 0.093006 |
| collage positive | 1719/3136（54.815%） | 2593/2976（87.130%） | 2704/3008（89.894%） | 0.638111 → 0.746772 → 0.721931 |

| 全1–150条件 | mixed/全部组 | 比较对 | q | 平局率 | 组等权mean差 | best严格胜/并列 | multi正adv |
|---|---:|---:|---:|---:|---:|---:|---:|
| original positive | 99/630 | 1025 | 0.274555 | 0.008899 | −0.280027 | 24/99；0/99 | 263/530 |
| original negative | 106/630 | 1071 | 0.136618 | 0.381082 | −0.086505 | 11/106；57/106 | 221/469 |
| collage positive | 257/1140 | 2722 | 0.689450 | 0 | +0.237333 | 215/257；0/257 | 4210/7016 |

完整分层、窗口、pooled/best/tie及合法分母均见`training_audit.json`。合并使用充分统计量，不平均不同大小rank的概率。

### 既有分数奖励诊断

以下是各窗口全部合法rollout的均值，包含单框；不是仅针对有ranking pair的条件均值。

| 完成更新 | 合法n | calibration_penalty | ranking_loss | distractor_penalty | order_penalty | multi_bonus | total reward | 非首选择/合法n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1–50 | 6223 | 0.346612 | 0.034149 | 0.043641 | 0.013599 | 0.054379 | 0.246527 | 489/6223 |
| 51–100 | 6364 | 0.238042 | 0.036403 | 0.036011 | 0.007593 | 0.081050 | 0.524682 | 1029/6364 |
| 101–150 | 6361 | 0.202224 | 0.028371 | 0.024650 | 0.004657 | 0.084421 | 0.609915 | 1239/6361 |

这些数值来自原日志，不是新损失或重新计算的训练奖励。不同窗口样本和候选组成不同，因此均值变化不能单独证明评分能力的因果改善。每个条件的均值、有效分母和候选数直方图保存在JSON中。

## 解释边界与下一步

事实：本checkpoint的分数选择相对固定首框有净收益，但选择仍未利用全部候选上限。训练中，collage条件的multi奖励优势与multi率上升同时出现；原始输入的mixed组multi收益较低且multi率下降。

推断：当前证据不支持把全部现象归结为统一的“探索不足”。奖励与输入条件之间的差异需要保留。不能仅凭这些相关统计断言某项奖励导致变化，也不能断言多框数量代表有效双实例覆盖。

G8与G4在相同更新数下生成量不同（本次至150为19200 rollouts），不能视为等计算预算对照。本报告未重新评测旧G4，不以未经重新核验的旧记录作主要比较。保持训练暂停；不自动延长训练、改奖励、重跑或升级Claim。


### 局限
单seed、已查看测试集；G8与G4同更新不等rollout预算。训练停154但仅评测保存150；诊断只取1..150，排除512条151..154及未完成组。mixed组选择偏差和窗口样本组成变化，相关性不等因果。43辅助指标未注册为primary，工程complete不等科学validated，无Claim升级。

### Claim 边界
单seed、已查看测试集，探索性诊断；不作因果结论或Claim升级。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766-r2/managed_console.log
shell/06_experiments/E-014/visualizations/g8-step150-20261014/report.md
shell/06_experiments/E-014/visualizations/g8-step150-20261014/source_hashes.json
shell/06_experiments/E-014/visualizations/g8-step150-20261014/integrity_audit.json
shell/06_experiments/E-014/visualizations/g8-step150-20261014/evaluation_audit.json
shell/06_experiments/E-014/visualizations/g8-step150-20261014/raw_candidate_audit.json
shell/06_experiments/E-014/visualizations/g8-step150-20261014/training_audit.json

### 过程记录
逐组与2400原group记录/24完成窗口一致。source_hashes33文件副本重新校验通过。根metrics稳定9226bytes，首次complete因观测不足拒绝、后续成功，无重跑。8GPU无compute进程；父训练仍暂停154；旧失败目录保留、step400目录不存在。上次canonical更新命令因key-results未编码JSON而拒绝，本次去掉该可选字段重新写入，不涉及任何实验重试。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
