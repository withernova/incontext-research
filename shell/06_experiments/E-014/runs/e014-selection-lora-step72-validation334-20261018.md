# e014-selection-lora-step72-validation334-20261018 · 用户同意评测训练后的独立选择LoRA。按刚才建议仅做内部验证集334例（123多候选）评测，使用r2最终step72 adapter及已验收数据Run的vali

- 父 Run：`e014-drawn-selection-lora-sft1epoch-20261018-r2`
- 来源版本：2026-10-18T16:42:26
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户同意评测训练后的独立选择LoRA。按刚才建议仅做内部验证集334例（123多候选）评测，使用r2最终step72 adapter及已验收数据Run的validation_manifest.json与validation_predictions.jsonl；冻结候选和顺序，exact-instance画框VQA，复用现有evaluate_candidate_vqa.py --selector-checkpoint，单次生成评测，不训练、不更改checkpoint或重试父Run。与相同候选的原score/First/Oracle比较，报告全量和多框mIoU/acc50/合法率/修复损害。此次不执行1766测试集，不用结果追加训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/selection_data/validation_manifest.json --manifest-sha256 65fa13a466f819b5c25a2d641c8996c280be107c1229970bba670efa8987454c --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-sft-data-step200-20261018/payload/selection_data/validation_predictions.jsonl --predictions-sha256 7064e524fc57a66243329e7d5bfd8489544d4338e0f7b90cdc02bb47cbf648c1 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/payload --expected-samples 334 --expected-multi 123 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --draw-boxes --selector-checkpoint /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/checkpoints/samples_00001152_step_000072 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py (standalone CLI)
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json

## 结果
内部验证334例完整评测，step72选择LoRA mIoU77.082%，原score75.095%（+1.987pp）；acc50 87.126% vs84.431%（+2.695pp）。123多框mIoU70.253% vs64.858%（+5.395pp），123回答全合法。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 123,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 334,
      "vqa_iou_mean": 0.7708168134092559,
      "vqa_iou_acc50": 0.8712574850299402,
      "score_iou_mean": 0.7509487019169863,
      "score_iou_acc50": 0.844311377245509,
      "first_iou_mean": 0.7072451457806614,
      "first_iou_acc50": 0.7964071856287425,
      "oracle_iou_mean": 0.8139758001455013,
      "oracle_iou_acc50": 0.9221556886227545,
      "valid_vqa_answers": 123,
      "invalid_vqa_answers": 0,
      "improves_score": 15,
      "worsens_score": 7,
      "fixes_score_miss": 15,
      "breaks_score_hit": 6,
      "oracle_hit_samples": 308,
      "vqa_hit_given_oracle_hit": 0.9448051948051948
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 123,
      "vqa_iou_mean": 0.7025326816825269,
      "vqa_iou_acc50": 0.8048780487804879,
      "score_iou_mean": 0.6485818748661201,
      "score_iou_acc50": 0.7317073170731707,
      "first_iou_mean": 0.5299071777154494,
      "first_iou_acc50": 0.6016260162601627,
      "oracle_iou_mean": 0.8197286294053391,
      "oracle_iou_acc50": 0.943089430894309,
      "valid_vqa_answers": 123,
      "invalid_vqa_answers": 0,
      "improves_score": 15,
      "worsens_score": 7,
      "fixes_score_miss": 15,
      "breaks_score_hit": 6,
      "oracle_hit_samples": 116,
      "vqa_hit_given_oracle_hit": 0.853448275862069
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 315,
        "vqa_iou_mean": 0.7741987772460945,
        "vqa_iou_acc50": 0.873015873015873,
        "score_iou_mean": 0.7560306707700121,
        "score_iou_acc50": 0.8476190476190476,
        "first_iou_mean": 0.7048937028978083,
        "first_iou_acc50": 0.7904761904761904,
        "oracle_iou_mean": 0.8121540255082557,
        "oracle_iou_acc50": 0.9174603174603174,
        "valid_vqa_answers": 114,
        "invalid_vqa_answers": 0,
        "improves_score": 14,
        "worsens_score": 7,
        "fixes_score_miss": 14,
        "breaks_score_hit": 6,
        "oracle_hit_samples": 289,
        "vqa_hit_given_oracle_hit": 0.9515570934256056
      },
      "LaSOT": {
        "samples": 19,
        "vqa_iou_mean": 0.7147474129564034,
        "vqa_iou_acc50": 0.8421052631578947,
        "score_iou_mean": 0.6666950077747154,
        "score_iou_acc50": 0.7894736842105263,
        "first_iou_mean": 0.7462295935753321,
        "first_iou_acc50": 0.8947368421052632,
        "oracle_iou_mean": 0.8441789059735151,
        "oracle_iou_acc50": 1.0,
        "valid_vqa_answers": 9,
        "invalid_vqa_answers": 0,
        "improves_score": 1,
        "worsens_score": 0,
        "fixes_score_miss": 1,
        "breaks_score_hit": 0,
        "oracle_hit_samples": 19,
        "vqa_hit_given_oracle_hit": 0.8421052631578947
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "65fa13a466f819b5c25a2d641c8996c280be107c1229970bba670efa8987454c",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "7064e524fc57a66243329e7d5bfd8489544d4338e0f7b90cdc02bb47cbf648c1",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "3a67c77b2e548f255f1b891ece30a5ab3d42fa527958fac9f868aa8cfe88a27f",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "outlined_numbered",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "selection_lora_bfloat16",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "selector_checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/checkpoints/samples_00001152_step_000072",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  },
  {
    "metric_id": "settings",
    "value": {
      "seed": 20260901,
      "max_new_tokens": 16,
      "vision_max_patch_tokens": 4096,
      "do_sample": false,
      "require_eos": true
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 17 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
训练数据来源没有新增评测原视频重叠，但固定生成器过去曾见部分同源视频，不能宣称整链无泄漏泛化。无TAO训练来源，属选择器诊断。保持GRPO停止。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-validation334-20261018/managed_console.log

### 审核入口
.pi/analysis/e014/selection-sft/validation334_audit.json

### 过程记录
这是独立验证Run，不改父训练gate_failed标记；无训练或追加测试推理，未改变代码。尚无同内部验证集原生零样本画框VQA对照，不能隔离SFT增益。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
