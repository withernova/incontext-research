# e014-selector-step4041-localviews-validation334-20261021 · 用户明确要求运行局部图方案。使用固定validation334/123多候选、step4041，比较无框原图两张与原图+Reference和候选裁剪K+3张，p

- 父 Run：`e014-selection-lora-step72-validation334-20261018`
- 来源版本：2026-10-18T18:11:18
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户明确要求运行局部图方案。使用固定validation334/123多候选、step4041，比较无框原图两张与原图+Reference和候选裁剪K+3张，padding.15，其他推理设置一致，共246次VQA。等待当前LR实验释放GPU后自动执行，不重复确认；单独记录，不训练、不改候选/GT。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确执行局部图方案。先在已有固定validation334（123多候选）做成对推理对照：同step4041、同冻结候选/顺序/seed20260901，original两图与local K+3无框图分别一次，共246模型调用。两端均BF16SDPA/8GPU/greedy16/EOS/vision4096每图/exact_instance；local每侧padding.15、不读取QueryGT裁剪。实际grid/裁剪SHA由既有评测器保存。未训练此checkpoint的多图适配，收益/下降均据实记录，不将单次推理对照冒称多图训练收益。任务文件事件等待LRRun退出释放8GPU，等待阶段无模型载入，无短周期轮询；依赖失败也仅释放资源，不冒称其成功。
- 命令：/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'e062caa03b2c20bafa2c3d7c9bcdf4693bb30497a3d8664cb01b0ed8ada0eed6'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'
- 代码版本：7caae090351c9c71ce65fd8c98a0bbbbb1825bc6
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json

## 结果
尚无结果。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "paired_view_comparison",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json"
  },
  {
    "metric_id": "source_samples",
    "value": 334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json"
  },
  {
    "metric_id": "multi_samples",
    "value": 123,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json"
  },
  {
    "metric_id": "total_model_calls",
    "value": 246,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json"
  },
  {
    "metric_id": "arms",
    "value": {
      "original": {
        "status": "completed",
        "action": "candidate_vqa",
        "evaluated_samples": 334,
        "world_size": 8,
        "vqa_samples": 123,
        "all": {
          "samples": 334,
          "vqa_iou_mean": 0.7708631237899211,
          "vqa_iou_acc50": 0.8712574850299402,
          "score_iou_mean": 0.7509487019169863,
          "score_iou_acc50": 0.844311377245509,
          "first_iou_mean": 0.7072451457806614,
          "first_iou_acc50": 0.7964071856287425,
          "oracle_iou_mean": 0.8139758001455013,
          "oracle_iou_acc50": 0.9221556886227545,
          "valid_vqa_answers": 123,
          "invalid_vqa_answers": 0,
          "improves_score": 18,
          "worsens_score": 10,
          "fixes_score_miss": 18,
          "breaks_score_hit": 9,
          "oracle_hit_samples": 308,
          "vqa_hit_given_oracle_hit": 0.9448051948051948
        },
        "multi": {
          "samples": 123,
          "vqa_iou_mean": 0.7026584350739263,
          "vqa_iou_acc50": 0.8048780487804879,
          "score_iou_mean": 0.6485818748661201,
          "score_iou_acc50": 0.7317073170731707,
          "first_iou_mean": 0.5299071777154494,
          "first_iou_acc50": 0.6016260162601627,
          "oracle_iou_mean": 0.8197286294053391,
          "oracle_iou_acc50": 0.943089430894309,
          "valid_vqa_answers": 123,
          "invalid_vqa_answers": 0,
          "improves_score": 18,
          "worsens_score": 10,
          "fixes_score_miss": 18,
          "breaks_score_hit": 9,
          "oracle_hit_samples": 116,
          "vqa_hit_given_oracle_hit": 0.853448275862069
        },
        "by_dataset": {
          "GOT10k": {
            "samples": 315,
            "vqa_iou_mean": 0.7742478809513077,
            "vqa_iou_acc50": 0.873015873015873,
            "score_iou_mean": 0.7560306707700121,
            "score_iou_acc50": 0.8476190476190476,
            "first_iou_mean": 0.7048937028978083,
            "first_iou_acc50": 0.7904761904761904,
            "oracle_iou_mean": 0.8121540255082557,
            "oracle_iou_acc50": 0.9174603174603174,
            "valid_vqa_answers": 114,
            "invalid_vqa_answers": 0,
            "improves_score": 17,
            "worsens_score": 10,
            "fixes_score_miss": 17,
            "breaks_score_hit": 9,
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
        "source_manifest_sha256": "65fa13a466f819b5c25a2d641c8996c280be107c1229970bba670efa8987454c",
        "source_predictions_sha256": "7064e524fc57a66243329e7d5bfd8489544d4338e0f7b90cdc02bb47cbf648c1",
        "prompt_sha256": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
        "prompt_variant": "exact_instance",
        "image_presentation": "original",
        "selector": "selection_lora_bfloat16",
        "selector_checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/checkpoints/samples_00064656_step_004041",
        "candidate_order": "source",
        "settings": {
          "seed": 20260901,
          "max_new_tokens": 16,
          "vision_max_patch_tokens": 4096,
          "do_sample": false,
          "require_eos": true
        }
      },
      "local": {
        "status": "completed",
        "action": "candidate_vqa",
        "evaluated_samples": 334,
        "world_size": 8,
        "vqa_samples": 123,
        "all": {
          "samples": 334,
          "vqa_iou_mean": 0.7736242493814879,
          "vqa_iou_acc50": 0.874251497005988,
          "score_iou_mean": 0.7509487019169863,
          "score_iou_acc50": 0.844311377245509,
          "first_iou_mean": 0.7072451457806614,
          "first_iou_acc50": 0.7964071856287425,
          "oracle_iou_mean": 0.8139758001455013,
          "oracle_iou_acc50": 0.9221556886227545,
          "valid_vqa_answers": 123,
          "invalid_vqa_answers": 0,
          "improves_score": 18,
          "worsens_score": 9,
          "fixes_score_miss": 18,
          "breaks_score_hit": 8,
          "oracle_hit_samples": 308,
          "vqa_hit_given_oracle_hit": 0.948051948051948
        },
        "multi": {
          "samples": 123,
          "vqa_iou_mean": 0.7101561257046846,
          "vqa_iou_acc50": 0.8130081300813008,
          "score_iou_mean": 0.6485818748661201,
          "score_iou_acc50": 0.7317073170731707,
          "first_iou_mean": 0.5299071777154494,
          "first_iou_acc50": 0.6016260162601627,
          "oracle_iou_mean": 0.8197286294053391,
          "oracle_iou_acc50": 0.943089430894309,
          "valid_vqa_answers": 123,
          "invalid_vqa_answers": 0,
          "improves_score": 18,
          "worsens_score": 9,
          "fixes_score_miss": 18,
          "breaks_score_hit": 8,
          "oracle_hit_samples": 116,
          "vqa_hit_given_oracle_hit": 0.8620689655172413
        },
        "by_dataset": {
          "GOT10k": {
            "samples": 315,
            "vqa_iou_mean": 0.7771755506261752,
            "vqa_iou_acc50": 0.8761904761904762,
            "score_iou_mean": 0.7560306707700121,
            "score_iou_acc50": 0.8476190476190476,
            "first_iou_mean": 0.7048937028978083,
            "first_iou_acc50": 0.7904761904761904,
            "oracle_iou_mean": 0.8121540255082557,
            "oracle_iou_acc50": 0.9174603174603174,
            "valid_vqa_answers": 114,
            "invalid_vqa_answers": 0,
            "improves_score": 17,
            "worsens_score": 9,
            "fixes_score_miss": 17,
            "breaks_score_hit": 8,
            "oracle_hit_samples": 289,
            "vqa_hit_given_oracle_hit": 0.9550173010380623
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
        "source_manifest_sha256": "65fa13a466f819b5c25a2d641c8996c280be107c1229970bba670efa8987454c",
        "source_predictions_sha256": "7064e524fc57a66243329e7d5bfd8489544d4338e0f7b90cdc02bb47cbf648c1",
        "prompt_sha256": "bf745775ff20fac3efa1e8b221ea0d67ffde5f8dccb8917db10dd021d4414490",
        "prompt_variant": "exact_instance",
        "image_presentation": "unmarked_full_plus_local_views",
        "selector": "selection_lora_bfloat16",
        "selector_checkpoint": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-historical-balanced-vqa-lora4epoch-20261019/payload/training/checkpoints/samples_00064656_step_004041",
        "candidate_order": "source",
        "settings": {
          "seed": 20260901,
          "max_new_tokens": 16,
          "vision_max_patch_tokens": 4096,
          "do_sample": false,
          "require_eos": true,
          "record_input_metadata": true
        },
        "crop_padding": 0.15,
        "image_count": "K+3 per multi-candidate sample"
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json"
  },
  {
    "metric_id": "all_miou_delta",
    "value": 0.0027611255915668265,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json"
  }
]
```

### 分析
原图/局部图各334/123逐例核验；653输入图SHA与尺寸、407裁剪像素/边界/padding.15和实际K+3 grid通过。全量mIoU77.086312→77.362425%（+0.276113pp）；多候选70.265844→71.015613%（+0.749769pp）。5题改变选择，修复3损害2，净多1题；246回答全合法。是固定两图训练checkpoint直接加裁剪的推理对照，单seed小收益不等于多图训练收益。证据.pi/analysis/e014/selector-experiments-20261021/completed_comparisons_audit.json。

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
训练数据来源没有新增评测原视频重叠，但固定生成器过去曾见部分同源视频，不能宣称整链无泄漏泛化。无TAO训练来源，属选择器诊断。保持GRPO停止。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selector-step4041-localviews-validation334-20261021/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
