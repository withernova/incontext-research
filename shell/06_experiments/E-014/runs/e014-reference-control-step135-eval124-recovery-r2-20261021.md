# e014-reference-control-step135-eval124-recovery-r2-20261021 · 继续完成用户原定control组124条最终评测；前次评测命令遗漏PYTHONPATH在导入阶段失败。恢复原环境导出，使用同一个已完成135步checkpoin

- 父 Run：`e014-reference-control-step135-eval124-recovery-20261021`
- 来源版本：2026-10-21T13:40:14
- 状态：analysis_pending
- Workspace：03

## 本次任务
继续完成用户原定control组124条最终评测；前次评测命令遗漏PYTHONPATH在导入阶段失败。恢复原环境导出，使用同一个已完成135步checkpoint和原数据/seed/评测参数，不训练，不改历史。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：补完用户已授权的control组124条/62pair最终评测。原135步训练完成且passed，但一次性收尾脚本误将fresh空字符串判错导致未评测。只复用原最终checkpoint，不重训、不改科学参数或旧失败记录；新独立评测Run。 原始训练adapterSHA=aabda9732a7e4a70eec1f01b774f05ee3ed41ee959950094b951e9b704f0208f；验证manifest/predictions SHA沿原命令，seed20260901/BF16SDPA/greedy16/EOS/vision4096/8GPU/exact_instance双全图/原候选保持。只有一次性输入验收脚本兼容实际空字符串，并分别读取旧训练与新评测目录；仓库源码和部署SHA未变。A-only答案位置分布混杂及23视频相关性限制保留。 前次补评测遗漏PYTHONPATH在模块导入阶段退出，本次恢复原命令的PYTHONPATH/OMP_NUM_THREADS/IPLOC_PYTHON，不改评测计算。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'189c7ac5fb90b5952ac2592c064aee995379db9d15f10279832e8e5ff9a8cdea'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json"
  },
  {
    "metric_id": "arm",
    "value": "control",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json"
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
      "updates_per_epoch": 45,
      "configured_max_epochs": 3,
      "checkpoint_interval_epochs": 0.5,
      "checkpoint_interval_samples": 359.0,
      "initialized_from": "",
      "resumed_from": "",
      "warmup_ratio": 0.05,
      "warmup_steps": 7,
      "max_grad_norm": 0.3,
      "assistant_only_logits": true,
      "logits_to_keep": 4,
      "effective_global_batch_size": 16,
      "steps": 135,
      "examples_seen": 2160,
      "session_examples_seen": 2160,
      "train_seconds": 1338.5422813892365,
      "examples_per_second": 1.613695756967942,
      "loss_before": 1.201930193696029,
      "loss_after": 7.027085923949627e-05,
      "training_pipeline": null,
      "loss_comparison_objective": "configured_loss",
      "adapter_delta_norm": 3.8179090821113917,
      "finite_grad_fraction": 1.0,
      "trainable_parameter_count": 21823488,
      "dataset_size": 718,
      "seed": 20260901,
      "full_metrics_sha256": "aa18ab9cdefeeb09f6774b00ceb03f018852d4c1dc4f01f68982cd4c720d492a",
      "final_adapter_sha256": "aabda9732a7e4a70eec1f01b774f05ee3ed41ee959950094b951e9b704f0208f",
      "checkpoint_directory_target_samples": 2154,
      "actual_presentations": 2160,
      "arm": "control",
      "training_source_run": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-fresh3epoch-validation124-20261021",
      "training_checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-fresh3epoch-validation124-20261021/payload/training/checkpoints/samples_00002154_step_000135"
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json"
  },
  {
    "metric_id": "evaluation",
    "value": {
      "status": "completed",
      "action": "candidate_vqa",
      "evaluated_samples": 124,
      "world_size": 8,
      "vqa_samples": 124,
      "all": {
        "samples": 124,
        "vqa_iou_mean": 0.5610441529990836,
        "vqa_iou_acc50": 0.6048387096774194,
        "score_iou_mean": 0.45333765432469036,
        "score_iou_acc50": 0.47580645161290325,
        "first_iou_mean": 0.4614600568486682,
        "first_iou_acc50": 0.4838709677419355,
        "oracle_iou_mean": 0.9154467999238126,
        "oracle_iou_acc50": 1.0,
        "valid_vqa_answers": 124,
        "invalid_vqa_answers": 0,
        "improves_score": 24,
        "worsens_score": 10,
        "fixes_score_miss": 24,
        "breaks_score_hit": 8,
        "oracle_hit_samples": 124,
        "vqa_hit_given_oracle_hit": 0.6048387096774194
      },
      "multi": {
        "samples": 124,
        "vqa_iou_mean": 0.5610441529990836,
        "vqa_iou_acc50": 0.6048387096774194,
        "score_iou_mean": 0.45333765432469036,
        "score_iou_acc50": 0.47580645161290325,
        "first_iou_mean": 0.4614600568486682,
        "first_iou_acc50": 0.4838709677419355,
        "oracle_iou_mean": 0.9154467999238126,
        "oracle_iou_acc50": 1.0,
        "valid_vqa_answers": 124,
        "invalid_vqa_answers": 0,
        "improves_score": 24,
        "worsens_score": 10,
        "fixes_score_miss": 24,
        "breaks_score_hit": 8,
        "oracle_hit_samples": 124,
        "vqa_hit_given_oracle_hit": 0.6048387096774194
      },
      "by_dataset": {
        "TAO": {
          "samples": 124,
          "vqa_iou_mean": 0.5610441529990836,
          "vqa_iou_acc50": 0.6048387096774194,
          "score_iou_mean": 0.45333765432469036,
          "score_iou_acc50": 0.47580645161290325,
          "first_iou_mean": 0.4614600568486682,
          "first_iou_acc50": 0.4838709677419355,
          "oracle_iou_mean": 0.9154467999238126,
          "oracle_iou_acc50": 1.0,
          "valid_vqa_answers": 124,
          "invalid_vqa_answers": 0,
          "improves_score": 24,
          "worsens_score": 10,
          "fixes_score_miss": 24,
          "breaks_score_hit": 8,
          "oracle_hit_samples": 124,
          "vqa_hit_given_oracle_hit": 0.6048387096774194
        }
      },
      "source_manifest_sha256": "67536ed1f2463e09dfc7afec87f2e3aa88d256825786c7f95b8e0288101330ff",
      "source_predictions_sha256": "2c38ba5fce978582210a4543f97ba6ecda2736ddab9b7f74e3ff48e2f9ac764d",
      "prompt_sha256": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
      "prompt_variant": "exact_instance",
      "image_presentation": "original",
      "selector": "selection_lora_bfloat16",
      "selector_checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-fresh3epoch-validation124-20261021/payload/training/checkpoints/samples_00002154_step_000135",
      "candidate_order": "source",
      "settings": {
        "seed": 20260901,
        "max_new_tokens": 16,
        "vision_max_patch_tokens": 4096,
        "do_sample": false,
        "require_eos": true
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json"
  },
  {
    "metric_id": "pair_diagnostics",
    "value": {
      "pairs": 62,
      "both_correct": 20,
      "both_valid": 62,
      "changed_choice_with_reference": 28,
      "both_correct_fraction": 0.3225806451612903
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json"
  },
  {
    "metric_id": "limitations",
    "value": "Small fresh-LoRA TAO-only comparison, correlated candidate sets across 23 validation videos; A-only and paired answer-position distributions differ. No independent evidence on general localization or isolated Reference causality.",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json"
  }
]
```

### 分析
原定最终step135评测已真实exit0；124ID/候选/IoU/原训练adapterSHA/62pair独立核验通过。arm=control，mIoU=0.561044152999，Acc50=0.604838709677，两题均正确20/62，换Reference改选择28/62；124回答全部有效。控制→配对mIoU56.104415→72.044781%（+15.940366pp），修复25损害3净+22命中，both20→38。只23个验证视频，候选来源相关，两组答案位置分布不同，单seed，不隔离Reference因果或证明一般泛化。只复用原训练模型补评测，无重新训练。原收尾与导入失败均保留。证据.pi/analysis/e014/selector-experiments-20261021/reference_final_audit.json；完整比较shell/06_experiments/E-014/执行对照-20261021.md。

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
仅生成，绝不补GT/混组/选择SFT或测试集生成，不自动恢复任何旧训练。指标仅描述训练候选而非泛化。legacy evaluator不记录逐例EOS标记；EOS停止默认生效但不是显式终止审计，后续入库需声明限制。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reference-control-step135-eval124-recovery-r2-20261021/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
