# e014-selector-linear-decay4041-to5388-eval1766-20261021 · 用户明确要求直接执行所讨论实验。本次从原step4041恢复，保持原数据和总5388步，仅将最后1347更新改为linear学习率5e-5降至5e-6，保留Ad

- 父 Run：`e014-historical-vqa-resume4041-to5388-eval1766-20261020`
- 来源版本：2026-10-20T16:30:35
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确要求直接执行所讨论实验。本次从原step4041恢复，保持原数据和总5388步，仅将最后1347更新改为linear学习率5e-5降至5e-6，保留Adam/history，完成后一次最终1766评测，与已有恒定LR续训对照；使用已部署7caae09，不重复确认授权。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户20261021明确要求执行上轮说明的对照。独立从原4041完整state续训至原5388，新增1347更新/21552呈现；只显式改变scheduler为linear4042..5388/end_factor0.1/overrideTrue。原21552静态均衡train SHA、seed20260901/NF4/r8alpha16/globalbatch16/原warmup与门禁保持；不恢复旧中断Run。起始实际LR5e-5/最终5e-6，核每个真实LR和历史前缀，保留Adam/步数；正常完成后仅最终5388做原1766/791无框exact_instance BF16SDPA评测。原恒定LR续训为对照；未恢复逐rank RNG，不声称逐位连续等价。命令和输入脚本SHA钉住，失败停止，不自动重跑。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'1da136419f1de8ce0ed2e4d0031aaa87602abce61583a317e057b69a87c6025f'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 配置：configs/sft/candidate_selection_lora.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/metrics.json"
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
      "train_seconds": 14007.585590362549,
      "examples_per_second": 1.5385949178014042,
      "loss_before": 6.459710672857e-05,
      "loss_after": 1.8775297752071651e-06,
      "training_pipeline": null,
      "loss_comparison_objective": "configured_loss",
      "adapter_delta_norm": 3.230712580408776,
      "finite_grad_fraction": 1.0,
      "trainable_parameter_count": 21823488,
      "dataset_size": 21552,
      "seed": 20260901,
      "full_metrics_sha256": "d5058ac13b4682582ce343f2eacfa0aa3dd9f87aec939d7a71375ccee1d3fec0",
      "final_adapter_sha256": "68d7107c0ce7c14b1274f4888ca4eb94b30d0a3488edaee0d4d1401ec5087e44",
      "added_updates": 1347,
      "actual_first_lr": 5e-05,
      "actual_final_lr": 5e-06,
      "all_actual_lrs_match_linear": true,
      "source_history_preserved": true,
      "learning_rate_schedule": {
        "contract": "sft_update_decay/v1",
        "policy": {
          "decay": {
            "kind": "linear",
            "start_step": 4042,
            "end_step": 5388,
            "end_factor": 0.1
          },
          "warmup_steps": 270,
          "total_steps": 5388,
          "base_lrs": [
            5e-05
          ]
        },
        "last_epoch": 5388,
        "next_update_lrs": [
          5e-06
        ],
        "transitions": [
          {
            "completed_step": 4041,
            "previous_policy": {
              "kind": "legacy_warmup_constant",
              "warmup_steps": "not recorded in legacy checkpoint",
              "base_lrs": [
                5e-05
              ]
            },
            "previous_next_update_lrs": [
              5e-05
            ],
            "new_policy": {
              "decay": {
                "kind": "linear",
                "start_step": 4042,
                "end_step": 5388,
                "end_factor": 0.1
              },
              "warmup_steps": 270,
              "total_steps": 5388,
              "base_lrs": [
                5e-05
              ]
            },
            "override_explicit": true
          }
        ],
        "indexing": "last_epoch=completed updates; optimizer lr is for last_epoch+1",
        "first_decay_update": 4042,
        "last_decay_update": 5388
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/metrics.json"
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
        "vqa_iou_mean": 0.7194462334134393,
        "vqa_iou_acc50": 0.7859569648924122,
        "score_iou_mean": 0.6916960157722533,
        "score_iou_acc50": 0.7553793884484711,
        "first_iou_mean": 0.656632485224866,
        "first_iou_acc50": 0.7151755379388448,
        "oracle_iou_mean": 0.7573992982137026,
        "oracle_iou_acc50": 0.8306908267270668,
        "valid_vqa_answers": 790,
        "invalid_vqa_answers": 1,
        "improves_score": 102,
        "worsens_score": 41,
        "fixes_score_miss": 79,
        "breaks_score_hit": 25,
        "oracle_hit_samples": 1467,
        "vqa_hit_given_oracle_hit": 0.9461486025903204
      },
      "multi": {
        "samples": 791,
        "vqa_iou_mean": 0.6737055384736944,
        "vqa_iou_acc50": 0.7281921618204804,
        "score_iou_mean": 0.6117499324631576,
        "score_iou_acc50": 0.6599241466498104,
        "first_iou_mean": 0.5334665001664629,
        "first_iou_acc50": 0.5701643489254109,
        "oracle_iou_mean": 0.7584401938937492,
        "oracle_iou_acc50": 0.8280657395701644,
        "valid_vqa_answers": 790,
        "invalid_vqa_answers": 1,
        "improves_score": 102,
        "worsens_score": 41,
        "fixes_score_miss": 79,
        "breaks_score_hit": 25,
        "oracle_hit_samples": 655,
        "vqa_hit_given_oracle_hit": 0.8793893129770992
      },
      "by_dataset": {
        "GOT10k": {
          "samples": 180,
          "vqa_iou_mean": 0.8269725873337589,
          "vqa_iou_acc50": 0.9,
          "score_iou_mean": 0.7959036041152275,
          "score_iou_acc50": 0.8611111111111112,
          "first_iou_mean": 0.782188525520559,
          "first_iou_acc50": 0.85,
          "oracle_iou_mean": 0.8462972143842374,
          "oracle_iou_acc50": 0.9222222222222223,
          "valid_vqa_answers": 51,
          "invalid_vqa_answers": 0,
          "improves_score": 8,
          "worsens_score": 2,
          "fixes_score_miss": 8,
          "breaks_score_hit": 1,
          "oracle_hit_samples": 166,
          "vqa_hit_given_oracle_hit": 0.9759036144578314
        },
        "LaSOT": {
          "samples": 600,
          "vqa_iou_mean": 0.6781810701280799,
          "vqa_iou_acc50": 0.7616666666666667,
          "score_iou_mean": 0.6537116103330052,
          "score_iou_acc50": 0.7366666666666667,
          "first_iou_mean": 0.625383400920118,
          "first_iou_acc50": 0.7,
          "oracle_iou_mean": 0.7167223918508266,
          "oracle_iou_acc50": 0.8083333333333333,
          "valid_vqa_answers": 246,
          "invalid_vqa_answers": 0,
          "improves_score": 31,
          "worsens_score": 12,
          "fixes_score_miss": 24,
          "breaks_score_hit": 9,
          "oracle_hit_samples": 485,
          "vqa_hit_given_oracle_hit": 0.9422680412371134
        },
        "TAO": {
          "samples": 986,
          "vqa_iou_mean": 0.7249273229322606,
          "vqa_iou_acc50": 0.7799188640973631,
          "score_iou_mean": 0.6957865607639502,
          "score_iou_acc50": 0.7474645030425964,
          "first_iou_mean": 0.652727174200144,
          "first_iou_acc50": 0.6997971602434077,
          "oracle_iou_mean": 0.7659231510605866,
          "oracle_iou_acc50": 0.8275862068965517,
          "valid_vqa_answers": 493,
          "invalid_vqa_answers": 1,
          "improves_score": 63,
          "worsens_score": 27,
          "fixes_score_miss": 47,
          "breaks_score_hit": 15,
          "oracle_hit_samples": 816,
          "vqa_hit_given_oracle_hit": 0.9424019607843137
        }
      },
      "source_manifest_sha256": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
      "source_predictions_sha256": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
      "prompt_sha256": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
      "prompt_variant": "exact_instance",
      "image_presentation": "original",
      "selector": "selection_lora_bfloat16",
      "selector_checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/payload/training/checkpoints/samples_00086208_step_005388",
      "candidate_order": "source",
      "settings": {
        "seed": 20260901,
        "max_new_tokens": 16,
        "vision_max_patch_tokens": 4096,
        "do_sample": false,
        "require_eos": true
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/metrics.json"
  }
]
```

### 分析
逐例1766/791及候选IoU、分集指标重算通过。全量mIoU71.944623%、Acc5078.595696%；较常数LR5388 +0.297875pp mIoU，修复16损害13；较step4041 +0.085995pp，修复19损害20，Acc50净少1题。790合法/1越界回复3（K2），按既有规则0分。1347实际LR全匹配5e-5→5e-6；训练passed。单seed且差异小，不能声称稳定提升。证据.pi/analysis/e014/selector-experiments-20261021/completed_comparisons_audit.json。

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
本次仅补原第4epoch，不是再加4epoch；从保存4041开始，不使用未保存4463状态。逐rank RNG不精确恢复，seed重设，不能声称逐位等价不间断续训。测试反复探索，单seed，不修改Claim。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-linear-decay4041-to5388-eval1766-20261021/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
