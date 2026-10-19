# e014-selection-lora-step72-test1766-20261018 · 用户要求开始1700集完整评测，即此前1766例冻结测试集。评测最终step72独立选择LoRA；使用历史score04-step200最高已记录Oracle候

- 父 Run：`e014-selection-lora-step72-validation334-20261018`
- 来源版本：2026-10-18T18:11:18
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户要求开始1700集完整评测，即此前1766例冻结测试集。评测最终step72独立选择LoRA；使用历史score04-step200最高已记录Oracle候选的原始1766清单和预测，冻结候选顺序，exact_instance画框，BF16 SDPA greedy16/EOS vision4096 seed20260901。只执行最终step72一次评测，不训练不评其他checkpoint。与原score/First/Oracle及既有同集原生画框VQA配对比较；报告全量/791多框/数据集指标、合法率与修复损害。测试集已被先前prompt探索使用，结果不声称独立无偏测试。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --draw-boxes --selector-checkpoint /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/checkpoints/samples_00001152_step_000072 && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：53ab7653602f62ffc1d5c9dadfbefccf7ad67474
- 随机种子：20260901
- 配置：tools/evaluate_candidate_vqa.py (standalone CLI)
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json

## 结果
完整1766例已评测：step72选择LoRA mIoU69.9607%，原评分69.1696%（+0.7911pp），原生画框VQA67.8265%（+2.1342pp）；acc50 76.2174%，较原评分+0.6795pp。791多框mIoU62.9412%。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 791,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.6996067241490003,
      "vqa_iou_acc50": 0.7621744054360136,
      "score_iou_mean": 0.6916960157722533,
      "score_iou_acc50": 0.7553793884484711,
      "first_iou_mean": 0.656632485224866,
      "first_iou_acc50": 0.7151755379388448,
      "oracle_iou_mean": 0.7573992982137026,
      "oracle_iou_acc50": 0.8306908267270668,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 74,
      "worsens_score": 52,
      "fixes_score_miss": 54,
      "breaks_score_hit": 42,
      "oracle_hit_samples": 1467,
      "vqa_hit_given_oracle_hit": 0.9175187457396047
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "vqa_iou_mean": 0.6294115139970837,
      "vqa_iou_acc50": 0.6750948166877371,
      "score_iou_mean": 0.6117499324631576,
      "score_iou_acc50": 0.6599241466498104,
      "first_iou_mean": 0.5334665001664629,
      "first_iou_acc50": 0.5701643489254109,
      "oracle_iou_mean": 0.7584401938937492,
      "oracle_iou_acc50": 0.8280657395701644,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 74,
      "worsens_score": 52,
      "fixes_score_miss": 54,
      "breaks_score_hit": 42,
      "oracle_hit_samples": 655,
      "vqa_hit_given_oracle_hit": 0.815267175572519
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.8251014292560699,
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
        "vqa_iou_mean": 0.6648202495413389,
        "vqa_iou_acc50": 0.7466666666666667,
        "score_iou_mean": 0.6537116103330052,
        "score_iou_acc50": 0.7366666666666667,
        "first_iou_mean": 0.625383400920118,
        "first_iou_acc50": 0.7,
        "oracle_iou_mean": 0.7167223918508266,
        "oracle_iou_acc50": 0.8083333333333333,
        "valid_vqa_answers": 246,
        "invalid_vqa_answers": 0,
        "improves_score": 27,
        "worsens_score": 16,
        "fixes_score_miss": 19,
        "breaks_score_hit": 13,
        "oracle_hit_samples": 485,
        "vqa_hit_given_oracle_hit": 0.9237113402061856
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.6978651803815807,
        "vqa_iou_acc50": 0.7474645030425964,
        "score_iou_mean": 0.6957865607639502,
        "score_iou_acc50": 0.7474645030425964,
        "first_iou_mean": 0.652727174200144,
        "first_iou_acc50": 0.6997971602434077,
        "oracle_iou_mean": 0.7659231510605866,
        "oracle_iou_acc50": 0.8275862068965517,
        "valid_vqa_answers": 494,
        "invalid_vqa_answers": 0,
        "improves_score": 40,
        "worsens_score": 34,
        "fixes_score_miss": 28,
        "breaks_score_hit": 28,
        "oracle_hit_samples": 816,
        "vqa_hit_given_oracle_hit": 0.9031862745098039
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "3a67c77b2e548f255f1b891ece30a5ab3d42fa527958fac9f868aa8cfe88a27f",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "outlined_numbered",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "selection_lora_bfloat16",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "selector_checkpoint",
    "value": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-drawn-selection-lora-sft1epoch-20261018-r2/payload/training/checkpoints/samples_00001152_step_000072",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
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
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json"
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
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-selection-lora-step72-test1766-20261018/managed_console.log

### 审核入口
.pi/analysis/e014/selection-sft/test1766_audit.json

### 过程记录
验收队列任务18:30:58 status确认running/tmux alive/exitnull，metrics尚无。仅跟进现有Run，未重新启动。已用本任务指定steward-sequence回调包装器PID204958等待既有Run终止exit文件，inotify事件式等待，无sleep或模型轮询；信号.pi/steward-signals/2b746002-34e7-46c0-b2bc-189a2ed63393.json，日志同目录.wait.log已确认进入等待。收到结果后才验收1766/791/964/11覆盖、1582图、模型快照和指标，并与既有原生画框VQA配对。当前未complete。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
