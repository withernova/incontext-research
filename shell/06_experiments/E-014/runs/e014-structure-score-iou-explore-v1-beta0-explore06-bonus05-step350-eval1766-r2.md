# e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2 · 继续完成用户已授权的暂停0.5训练并评测step350任务。首次仅目录preflight失败，无输入准备/模型加载/预测。保留失败Run全部产物。独立修正版Ru

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766`
- 来源版本：2026-10-15T08:38:08
- 状态：analysis_pending
- Workspace：03

## 本次任务
继续完成用户已授权的暂停0.5训练并评测step350任务。首次仅目录preflight失败，无输入准备/模型加载/预测。保留失败Run全部产物。独立修正版Run采用managed根目录与execution子目录分离：Run/config保存参数绑定，managed根outputs保持空，冻结worker独占新Run/execution/payload，execution在启动前不存在。仍评测同一父训练step350/SHA2399a6db32649adc219f4e85f859dd052cbc634fe85571e5aee087ccdb235a84，原1766/8GPU/multi_v2/greedy192/vision4096/eval seed20260901；同已部署7bb09c源码不变，输入科学参数不变。不是重新训练或重用失败payload，是本任务首次实际评测。评测后父保持暂停，只启动健康/配置核验，不持续监控日志。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：继续完成用户已授权的暂停0.5训练并评测step350任务。首次仅目录preflight失败，无输入准备/模型加载/预测。保留失败Run全部产物。独立修正版Run采用managed根目录与execution子目录分离：Run/config保存参数绑定，managed根outputs保持空，冻结worker独占新Run/execution/payload，execution在启动前不存在。仍评测同一父训练step350/SHA2399a6db32649adc219f4e85f859dd052cbc634fe85571e5aee087ccdb235a84，原1766/8GPU/multi_v2/greedy192/vision4096/eval seed20260901；同已部署7bb09c源码不变，输入科学参数不变。不是重新训练或重用失败payload，是本任务首次实际评测。评测后父保持暂停，只启动健康/配置核验，不持续监控日志。 配置SHA48be697131cc3e21cc1d02a87adbb45f4ef063fbdf6c49836958ea36382df008，source_config_review静态通过、未测试/build/import-smoke。code prepare fetch仍受阻，仅Run内参数文件，不修改代码仓库或退回SSH源码patch。source原已部署7bb09c762b4e6030fe870b34f9c1a119d7c81425；metadata metrics_path指向execution/metrics.json，managed log为Run根managed_console.log，worker额外console仅准备时检查新execution不存在。源输入/权重/optimizer350/provenance沿原Shell核验。
- 命令：env E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350 E014_EVAL_CONFIG=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/config/evaluation_config.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=350 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：20260901
- 配置：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/config/evaluation_config.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json

## 结果
step350正式评测完成：1766条/8GPU/exit0，indices与ID完整，逐条Selected/First/Oracle mIoU重算一致。Selected .6437733，First .6486097，Oracle .6540893，gap .0103161；1764条全部两个框、2非法，多框99.88675%。第二框meanIoU .0129444，仅13/1764≥.5，平均score .0358163；23条改善First，10条从First<.5救至Oracle≥.5，20条Selected错而Oracle正确。多框大量出现但有效新增定位很少，与低分错误第二框领取.5补偿的奖励投机解释一致；不宣称因果或量化下降，尚无用户指定同协议基线。训练暂停，不改奖励/重训/Claim，未额外测试，正式评测及完整性验收完成。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "evaluate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "dataloader",
    "value": "test_dataloader",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "dataset_size",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "max_new_tokens",
    "value": 192,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "vision_max_patch_tokens",
    "value": 4096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "vision_max_pixels",
    "value": 1048576,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "selection",
    "value": "head",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "selection_seed",
    "value": null,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "seconds",
    "value": 1609.7308859825134,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "samples_per_second",
    "value": 1.0970777882056393,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "parse_rate",
    "value": 0.9988674971687429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "miou",
    "value": 0.6437732573308876,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.25",
    "value": 0.7400906002265005,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.5",
    "value": 0.7106455266138165,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "acc_iou_0.75",
    "value": 0.6126840317100792,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "iou_distribution",
    "value": {
      "count": 1766,
      "min": 0.0,
      "q25": 0.16702682583354592,
      "median": 0.8580939862846902,
      "q75": 0.9529275108868056,
      "max": 0.9985652797704447,
      "bins": {
        "[0.00,0.10)": 423,
        "[0.10,0.25)": 36,
        "[0.25,0.50)": 52,
        "[0.50,0.75)": 173,
        "[0.75,1.00]": 1082
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "confidence_format_valid_rate",
    "value": 0.9988674971687429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "confidence_invalid_count",
    "value": 2,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "candidate_selection",
    "value": "highest_score_then_first",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "candidate_count_policy",
    "value": "variable_nonempty_no_box_count_cap",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "candidate_count_histogram",
    "value": {
      "0": 2,
      "2": 1764
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "variable_candidate_format_valid_rate",
    "value": 0.9988674971687429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "multiple_candidate_rate",
    "value": 0.9988674971687429,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "first_candidate_miou",
    "value": 0.6486097176006531,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "oracle_miou",
    "value": 0.6540893193817121,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "oracle_gap",
    "value": 0.01031606205082447,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "selected_nonfirst_rate",
    "value": 0.020385050962627407,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_rate",
    "value": 0.9847112117780294,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "spatial_order_valid_given_format",
    "value": 0.985827664399093,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "near_duplicate_rate",
    "value": 0.0016987542468856172,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc",
    "value": 0.2608695652173913,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "nonfirst_acc_samples",
    "value": 23,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "iou_argmax_tie_policy",
    "value": "earliest_candidate",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "parse_rate": 1.0,
        "miou": 0.7789611895078606,
        "acc_iou_0.25": 0.8833333333333333,
        "acc_iou_0.5": 0.8611111111111112,
        "acc_iou_0.75": 0.7833333333333333,
        "iou_distribution": {
          "count": 180,
          "min": 0.0,
          "q25": 0.7789838546877024,
          "median": 0.905543129383136,
          "q75": 0.9620563899356651,
          "max": 0.9972022382094324,
          "bins": {
            "[0.00,0.10)": 21,
            "[0.10,0.25)": 0,
            "[0.25,0.50)": 4,
            "[0.50,0.75)": 14,
            "[0.75,1.00]": 141
          }
        },
        "confidence_format_valid_rate": 1.0,
        "confidence_invalid_count": 0,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "2": 180
        },
        "variable_candidate_format_valid_rate": 1.0,
        "multiple_candidate_rate": 1.0,
        "first_candidate_miou": 0.7841883034142197,
        "oracle_miou": 0.7884490293090172,
        "oracle_gap": 0.009487839801156528,
        "selected_nonfirst_rate": 0.005555555555555556,
        "spatial_order_valid_rate": 1.0,
        "spatial_order_valid_given_format": 1.0,
        "near_duplicate_rate": 0.0,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 1,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "LaSOT": {
        "samples": 600,
        "parse_rate": 0.9983333333333333,
        "miou": 0.5999799324665352,
        "acc_iou_0.25": 0.7216666666666667,
        "acc_iou_0.5": 0.6833333333333333,
        "acc_iou_0.75": 0.5416666666666666,
        "iou_distribution": {
          "count": 600,
          "min": 0.0,
          "q25": 0.09033642848072174,
          "median": 0.7871569048750687,
          "q75": 0.9166199515378229,
          "max": 0.9971860498176288,
          "bins": {
            "[0.00,0.10)": 152,
            "[0.10,0.25)": 15,
            "[0.25,0.50)": 23,
            "[0.50,0.75)": 85,
            "[0.75,1.00]": 325
          }
        },
        "confidence_format_valid_rate": 0.9983333333333333,
        "confidence_invalid_count": 1,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 1,
          "2": 599
        },
        "variable_candidate_format_valid_rate": 0.9983333333333333,
        "multiple_candidate_rate": 0.9983333333333333,
        "first_candidate_miou": 0.602882813426633,
        "oracle_miou": 0.6038805700485614,
        "oracle_gap": 0.0039006375820261896,
        "selected_nonfirst_rate": 0.011666666666666667,
        "spatial_order_valid_rate": 0.99,
        "spatial_order_valid_given_format": 0.991652754590985,
        "near_duplicate_rate": 0.0016666666666666668,
        "nonfirst_acc": 0.0,
        "nonfirst_acc_samples": 2,
        "iou_argmax_tie_policy": "earliest_candidate"
      },
      "TAO": {
        "samples": 986,
        "parse_rate": 0.9989858012170385,
        "miou": 0.6457430008671525,
        "acc_iou_0.25": 0.7251521298174443,
        "acc_iou_0.5": 0.6997971602434077,
        "acc_iou_0.75": 0.6247464503042597,
        "iou_distribution": {
          "count": 986,
          "min": 0.0,
          "q25": 0.060239121418723625,
          "median": 0.8845360963100388,
          "q75": 0.9613832372649138,
          "max": 0.9985652797704447,
          "bins": {
            "[0.00,0.10)": 250,
            "[0.10,0.25)": 21,
            "[0.25,0.50)": 25,
            "[0.50,0.75)": 74,
            "[0.75,1.00]": 616
          }
        },
        "confidence_format_valid_rate": 0.9989858012170385,
        "confidence_invalid_count": 1,
        "candidate_selection": "highest_score_then_first",
        "candidate_count_policy": "variable_nonempty_no_box_count_cap",
        "candidate_count_histogram": {
          "0": 1,
          "2": 985
        },
        "variable_candidate_format_valid_rate": 0.9989858012170385,
        "multiple_candidate_rate": 0.9989858012170385,
        "first_candidate_miou": 0.6516847653267904,
        "oracle_miou": 0.6601141690906136,
        "oracle_gap": 0.014371168223461073,
        "selected_nonfirst_rate": 0.028397565922920892,
        "spatial_order_valid_rate": 0.9787018255578094,
        "spatial_order_valid_given_format": 0.9796954314720813,
        "near_duplicate_rate": 0.002028397565922921,
        "nonfirst_acc": 0.3,
        "nonfirst_acc_samples": 20,
        "iou_argmax_tie_policy": "earliest_candidate"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "input_provenance",
    "value": {
      "source_sha256": {
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json": "48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350/adapter/policy/adapter_config.json": "025b5e8180341469d1fc93319f02ae2be67733f62b16dcaef41aaaf354e096a7",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350/adapter/policy/adapter_model.safetensors": "2399a6db32649adc219f4e85f859dd052cbc634fe85571e5aee087ccdb235a84",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350/optimizer.pt": "62cd9c94877c71d8e3e4b7513febaf5e7bfd941b1e64e457ab08c391374bc574",
        "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/config_snapshot.json": "5f4d159fa043ecb743e05a1decb6b751d7cab926d96a907f2a2c530623f2e763"
      },
      "derived_manifest_sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
      "expected_samples": 1766,
      "checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/payload/grpo/checkpoints/step_000350",
      "prompt_variant": "multi_v2",
      "prompt_sha256": "c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba",
      "step": 350,
      "training_reward": {
        "correctness_threshold": 0.5,
        "exploration_threshold": 0.3,
        "distinct_threshold": 0.9,
        "score_weight": 1.1,
        "iou_weight": 1.0,
        "order_penalty": 0.12,
        "exploration_penalty": 0.6,
        "multibox_bonus_weight": 0.5
      },
      "training_group_size": 4
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "valid_gt_ap",
    "value": {
      "AP25": 0.6996394952019535,
      "AP50": 0.664447143360461,
      "AP75": 0.5395393702317284,
      "AP50_95_all_points": 0.5033309086543435,
      "samples": 1756,
      "invalid_predictions": 2
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "legacy_all_query_ap",
    "value": {
      "AP25": 0.6952255173367237,
      "AP50": 0.6602822269847525,
      "AP75": 0.536206853084534,
      "AP50_95_all_points": 0.5002184053789084,
      "samples": 1766,
      "invalid_predictions": 2
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Previously viewed test set; exploratory checkpoint diagnosis, no matched baseline. AP uses the final score-selected box, not full detection AP.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json"
  }
]
```

### 分析
step350正式评测完成：1766条/8GPU/exit0，indices与ID完整，逐条Selected/First/Oracle mIoU重算一致。Selected .6437733，First .6486097，Oracle .6540893，gap .0103161；1764条全部两个框、2非法，多框99.88675%。第二框meanIoU .0129444，仅13/1764≥.5，平均score .0358163；23条改善First，10条从First<.5救至Oracle≥.5，20条Selected错而Oracle正确。多框大量出现但有效新增定位很少，与低分错误第二框领取.5补偿的奖励投机解释一致；不宣称因果或量化下降，尚无用户指定同协议基线。训练暂停，不改奖励/重训/Claim，未额外测试，正式评测及完整性验收完成。 奖励构造例：正确单框u=.8/s=1得2.9；distinct两框u=.4/0、s=0/0得3.0，较差Selected定位可因.5补偿获更高R。结论仍需匹配对照验证。 横向位置核对（同predictions SHA、不重推理）：1756有效GT左/右半区893/863，第一框mIoU .6413275/.6636608，右半区也由第一框有效定位；1764个第一框有986个中心x≥500。第二框均值中心912.17，中位916.5，1676/1764=95.01%中心≥850，1486中心≥900，显示最右端低分补框模式；生成序号1不等于图像左侧真实实例。GT半区不等于AB/BA实例排名，不能替代拼图专项评测。

### 局限
此前已查看测试集；未指定匹配对照，不能报告下降幅度或单独归因于0.5；指标未注册为Experiment主证据，无Solid结果，不提升Claim。未额外测试。

### 结论范围
同一用户授权单checkpoint评测的独立目录修正版；原科学参数不变，训练保持暂停，不覆盖失败Run或自动恢复。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/execution/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2/managed_console.log
.pi/analysis/e014/e014-bonus05-step350-eval-r2/report.md
.pi/analysis/e014/e014-bonus05-step350-eval-r2/final_metrics.json
.pi/analysis/e014/e014-bonus05-step350-eval-r2/final_integrity_audit.json
.pi/analysis/e014/e014-bonus05-step350-eval-r2/spatial_candidate_audit.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
