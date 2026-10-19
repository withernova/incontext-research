# e014-selection-fulltrain-step2095-test1766-20261019 · 用户要求暂停当前训练，用最后完整checkpoint评测全部1766。训练已SIGINT退出释放GPU，固定samples_00033516_step_0020

- 父 Run：`e014-selection-fulltrain-gt-lora5epoch-20261019`
- 来源版本：2026-10-19T08:14:14
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户要求暂停当前训练，用最后完整checkpoint评测全部1766。训练已SIGINT退出释放GPU，固定samples_00033516_step_002095（约4epoch），adapter SHA297f0fe750bb3c44b09c6608d5589dafcd0d4aee76d677ce04f31090b88c832a。复用同一冻结1766清单/791多候选/原score04step200候选；exact_instance画框、seed20260901、BF16 SDPA/greedy16/EOS/vision4096，只有选择LoRA改变。不加Query GT、不重训或自动恢复训练，不走Steward队列，不短周期轮询。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --draw-boxes --selector-checkpoint /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-gt-lora5epoch-20261019/payload/training/checkpoints/samples_00033516_step_002095 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py (CLI)
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json

## 结果
1766评测exit0并全量核验通过；791多框回答全合法。全量mIoU71.1392/Acc50 77.6897%，多框mIoU65.5724%。比小集step360全量mIoU+0.8239pp、净增19命中；比原score+1.9696pp、净增38命中。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 791,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.7113920875821294,
      "vqa_iou_acc50": 0.7768969422423556,
      "score_iou_mean": 0.6916960157722533,
      "score_iou_acc50": 0.7553793884484711,
      "first_iou_mean": 0.656632485224866,
      "first_iou_acc50": 0.7151755379388448,
      "oracle_iou_mean": 0.7573992982137026,
      "oracle_iou_acc50": 0.8306908267270668,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 90,
      "worsens_score": 44,
      "fixes_score_miss": 71,
      "breaks_score_hit": 33,
      "oracle_hit_samples": 1467,
      "vqa_hit_given_oracle_hit": 0.9352419904567144
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "vqa_iou_mean": 0.655723716048798,
      "vqa_iou_acc50": 0.7079646017699115,
      "score_iou_mean": 0.6117499324631576,
      "score_iou_acc50": 0.6599241466498104,
      "first_iou_mean": 0.5334665001664629,
      "first_iou_acc50": 0.5701643489254109,
      "oracle_iou_mean": 0.7584401938937492,
      "oracle_iou_acc50": 0.8280657395701644,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 90,
      "worsens_score": 44,
      "fixes_score_miss": 71,
      "breaks_score_hit": 33,
      "oracle_hit_samples": 655,
      "vqa_hit_given_oracle_hit": 0.8549618320610687
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.8279080296222866,
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
        "vqa_iou_mean": 0.6743913465674425,
        "vqa_iou_acc50": 0.7583333333333333,
        "score_iou_mean": 0.6537116103330052,
        "score_iou_acc50": 0.7366666666666667,
        "first_iou_mean": 0.625383400920118,
        "first_iou_acc50": 0.7,
        "oracle_iou_mean": 0.7167223918508266,
        "oracle_iou_acc50": 0.8083333333333333,
        "valid_vqa_answers": 246,
        "invalid_vqa_answers": 0,
        "improves_score": 31,
        "worsens_score": 14,
        "fixes_score_miss": 25,
        "breaks_score_hit": 12,
        "oracle_hit_samples": 485,
        "vqa_hit_given_oracle_hit": 0.9381443298969072
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.7126370926952978,
        "vqa_iou_acc50": 0.7657200811359026,
        "score_iou_mean": 0.6957865607639502,
        "score_iou_acc50": 0.7474645030425964,
        "first_iou_mean": 0.652727174200144,
        "first_iou_acc50": 0.6997971602434077,
        "oracle_iou_mean": 0.7659231510605866,
        "oracle_iou_acc50": 0.8275862068965517,
        "valid_vqa_answers": 494,
        "invalid_vqa_answers": 0,
        "improves_score": 51,
        "worsens_score": 28,
        "fixes_score_miss": 38,
        "breaks_score_hit": 20,
        "oracle_hit_samples": 816,
        "vqa_hit_given_oracle_hit": 0.9252450980392157
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "3a67c77b2e548f255f1b891ece30a5ab3d42fa527958fac9f868aa8cfe88a27f",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "outlined_numbered",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "selection_lora_bfloat16",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "selector_checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-gt-lora5epoch-20261019/payload/training/checkpoints/samples_00033516_step_002095",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
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
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json"
  }
]
```

### 分析
08:28:40 managed complete成功；1766唯一覆盖/冻结候选GT重算/791合法VQA/1582渲染SHA与小集step72及360完全一致，step2095 adapter SHA与推理快照已核。全量mIoU71.1392/Acc50 77.6897%，多框mIoU65.5724/Acc50 70.7965%。较小集step360全量mIoU+0.8239pp，103选择变化，48 IoU改善/28损害，41命中修复/22损害净19；较小集step72+1.1785pp，净26命中。相对score90改善/44损害、71修复/33损害净38，全量mIoU+1.9696pp。GOT/LaSOT/TAO mIoU82.7908/67.4391/71.2637；较小集step360分别约-0.0019/+0.9901/+0.8736pp。全量Oracle75.7399仍差4.6007pp，多框Oracle75.8440仍差10.2716pp。

### 局限
扩大独立训练源、加入TAO、补GT及更新预算同时变化，不能单独归因GT补框。重复探索测试集、单seed，无显著性检验，不是无偏独立测试。辅助指标不升级主指标或Claim。训练保持用户中断状态，无自动恢复/追加评测。

### Claim 边界
重复使用的探索测试集，不是无偏独立测试；新增训练数据/TAO与训练预算同时变化，不能将差异单独归因于GT补框。父训练仅约4epoch用户停止，未完成5epoch，不自动恢复或增加评测。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-fulltrain-step2095-test1766-20261019/managed_console.log

### 审核入口
.pi/analysis/e014/selection-sft/test1766_fulltrain_step2095_audit.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
