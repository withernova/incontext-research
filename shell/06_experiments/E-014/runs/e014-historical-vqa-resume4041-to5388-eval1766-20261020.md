# e014-historical-vqa-resume4041-to5388-eval1766-20261020 · 用户要求从3epoch checkpoint断点续训完成并看看提升：从samples_00064656_step_004041恢复adapter/AdamW/s

- 父 Run：`e014-historical-balanced-vqa-lora4epoch-20261019`
- 来源版本：2026-10-20T09:23:38
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户要求从3epoch checkpoint断点续训完成并看看提升：从samples_00064656_step_004041恢复adapter/AdamW/scheduler/history/进度，到原总4epoch step5388，仅新增1347更新/21552呈现。复用同一21552行静态均衡train SHA6d2a9b4fcd6825736aa3534afd6b2de895da4f45352d79246ef11125cd2ffc21，无框bbox配置和超参不变。新独立输出，不改原中断Run；逐rank RNG当前接口不恢复，seed重设并记录限制。只有训练成功和原fixed8-loss门禁通过后，串行评测最终4epoch checkpoint一次固定1766，与4041对比；失败停止不retry，不测其他checkpoint，不扩预算。不启Steward/定时轮询。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import json,hashlib,os;from pathlib import Path;b=Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/inputs/command.json'"'"').read_bytes();assert hashlib.sha256(b).hexdigest()=='"'"'c29c594f0a363fe0d08031cb9b7855fedbb7a322a2abb78aacb018cf91f3a6c3'"'"';os.execv("/bin/bash",["bash","-c",json.loads(b)["command"]])'
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py + tools/evaluate_candidate_vqa.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/metrics.json"
  },
  {
    "metric_id": "training",
    "value": {
      "status": "passed",
      "distributed": true,
      "world_size": 8,
      "per_device_batch_size": 1,
      "global_physical_batch_size": 8,
      "gradient_accumulation_steps": 2,
      "updates_per_epoch": 1347,
      "configured_max_epochs": 4,
      "checkpoint_interval_epochs": 0.5,
      "checkpoint_interval_samples": 10776.0,
      "initialized_from": "",
      "resumed_from": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/checkpoints/samples_00064656_step_004041",
      "warmup_ratio": 0.05,
      "warmup_steps": 270,
      "max_grad_norm": 0.3,
      "assistant_only_logits": true,
      "logits_to_keep": 4,
      "effective_global_batch_size": 16,
      "steps": 5388,
      "examples_seen": 86208,
      "session_examples_seen": 21552,
      "train_seconds": 13754.442301273346,
      "examples_per_second": 1.5669119494583055,
      "loss_before": 6.459710672857e-05,
      "loss_after": 2.937922826040662e-05,
      "training_pipeline": null,
      "loss_comparison_objective": "configured_loss",
      "adapter_delta_norm": 5.5452647419556405,
      "finite_grad_fraction": 1.0,
      "trainable_parameter_count": 21823488,
      "dataset_size": 21552,
      "seed": 20260901,
      "full_metrics_sha256": "7796628285e7b09256d57d9360e9d206832151c8c2d5f07f47131dbd2d6efb6d",
      "final_adapter_sha256": "4bebaaa3ef6b13e6fdae2343e5093f18b3545fec28253f747db8da429d8646d3"
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/metrics.json"
  },
  {
    "metric_id": "evaluation",
    "value": {
      "status": "completed",
      "action": "candidate_vqa",
      "evaluated_samples": 1766,
      "world_size": 8,
      "vqa_samples": 791,
      "all": {
        "samples": 1766,
        "vqa_iou_mean": 0.7164674866079094,
        "vqa_iou_acc50": 0.7842582106455266,
        "score_iou_mean": 0.6916960157722533,
        "score_iou_acc50": 0.7553793884484711,
        "first_iou_mean": 0.656632485224866,
        "first_iou_acc50": 0.7151755379388448,
        "oracle_iou_mean": 0.7573992982137026,
        "oracle_iou_acc50": 0.8306908267270668,
        "valid_vqa_answers": 791,
        "invalid_vqa_answers": 0,
        "improves_score": 100,
        "worsens_score": 50,
        "fixes_score_miss": 80,
        "breaks_score_hit": 29,
        "oracle_hit_samples": 1467,
        "vqa_hit_given_oracle_hit": 0.9441036128152692
      },
      "multi": {
        "samples": 791,
        "vqa_iou_mean": 0.6670551378939651,
        "vqa_iou_acc50": 0.7243994943109987,
        "score_iou_mean": 0.6117499324631576,
        "score_iou_acc50": 0.6599241466498104,
        "first_iou_mean": 0.5334665001664629,
        "first_iou_acc50": 0.5701643489254109,
        "oracle_iou_mean": 0.7584401938937492,
        "oracle_iou_acc50": 0.8280657395701644,
        "valid_vqa_answers": 791,
        "invalid_vqa_answers": 0,
        "improves_score": 100,
        "worsens_score": 50,
        "fixes_score_miss": 80,
        "breaks_score_hit": 29,
        "oracle_hit_samples": 655,
        "vqa_hit_given_oracle_hit": 0.8748091603053435
      },
      "by_dataset": {
        "GOT10k": {
          "samples": 180,
          "vqa_iou_mean": 0.8218731461766253,
          "vqa_iou_acc50": 0.8944444444444445,
          "score_iou_mean": 0.7959036041152275,
          "score_iou_acc50": 0.8611111111111112,
          "first_iou_mean": 0.782188525520559,
          "first_iou_acc50": 0.85,
          "oracle_iou_mean": 0.8462972143842374,
          "oracle_iou_acc50": 0.9222222222222223,
          "valid_vqa_answers": 51,
          "invalid_vqa_answers": 0,
          "improves_score": 7,
          "worsens_score": 2,
          "fixes_score_miss": 7,
          "breaks_score_hit": 1,
          "oracle_hit_samples": 166,
          "vqa_hit_given_oracle_hit": 0.9698795180722891
        },
        "LaSOT": {
          "samples": 600,
          "vqa_iou_mean": 0.6803494116945703,
          "vqa_iou_acc50": 0.765,
          "score_iou_mean": 0.6537116103330052,
          "score_iou_acc50": 0.7366666666666667,
          "first_iou_mean": 0.625383400920118,
          "first_iou_acc50": 0.7,
          "oracle_iou_mean": 0.7167223918508266,
          "oracle_iou_acc50": 0.8083333333333333,
          "valid_vqa_answers": 246,
          "invalid_vqa_answers": 0,
          "improves_score": 33,
          "worsens_score": 14,
          "fixes_score_miss": 26,
          "breaks_score_hit": 9,
          "oracle_hit_samples": 485,
          "vqa_hit_given_oracle_hit": 0.9463917525773196
        },
        "TAO": {
          "samples": 986,
          "vqa_iou_mean": 0.7192036186825893,
          "vqa_iou_acc50": 0.7758620689655172,
          "score_iou_mean": 0.6957865607639502,
          "score_iou_acc50": 0.7474645030425964,
          "first_iou_mean": 0.652727174200144,
          "first_iou_acc50": 0.6997971602434077,
          "oracle_iou_mean": 0.7659231510605866,
          "oracle_iou_acc50": 0.8275862068965517,
          "valid_vqa_answers": 494,
          "invalid_vqa_answers": 0,
          "improves_score": 60,
          "worsens_score": 34,
          "fixes_score_miss": 47,
          "breaks_score_hit": 19,
          "oracle_hit_samples": 816,
          "vqa_hit_given_oracle_hit": 0.9375
        }
      },
      "source_manifest_sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
      "source_predictions_sha256": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
      "prompt_sha256": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
      "prompt_variant": "exact_instance",
      "image_presentation": "original",
      "selector": "selection_lora_bfloat16",
      "selector_checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/payload/training/checkpoints/samples_00086208_step_005388",
      "candidate_order": "source",
      "settings": {
        "seed": 20260901,
        "max_new_tokens": 16,
        "vision_max_patch_tokens": 4096,
        "do_sample": false,
        "require_eos": true
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 3 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
本次仅补原第4epoch，不是再加4epoch；从保存4041开始，不使用未保存4463状态。逐rank RNG不精确恢复，seed重设，不能声称逐位等价不间断续训。测试反复探索，单seed，不修改Claim。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-vqa-resume4041-to5388-eval1766-20261020/managed_console.log

### 审核入口
.pi/analysis/e014/historical-candidate-sources-20261019/resume4041_preflight.json
.pi/analysis/e014/historical-candidate-sources-20261019/resume4041_command.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
