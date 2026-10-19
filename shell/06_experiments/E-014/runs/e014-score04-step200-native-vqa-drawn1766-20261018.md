# e014-score04-step200-native-vqa-drawn1766-20261018 · 用户授权编写代码运行画框VQA。保持原始Qwen3-VL-8B-Instruct无adapter BF16/SDPA、冻结历史score0.4/G4/step2

- 父 Run：`e014-score04-step200-native-vqa-exact1766-20261018`
- 来源版本：2026-10-18T11:49:10
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户授权编写代码运行画框VQA。保持原始Qwen3-VL-8B-Instruct无adapter BF16/SDPA、冻结历史score0.4/G4/step200候选、原顺序、exact_instance prompt及seed20260901/greedy16/EOS/vision4096/8GPU不变。新增Reference绿色REF框、Query红候选框与1-based编号（无裁剪、原图尺寸不变），提示词仅增加颜色编号说明；不画QueryGT/不提供score。791多框VQA，964单框保留，11无候选计0，总1766；独立Run保存渲染图/几何/哈希。比较无画框exact与baseline及原score/Oracle。同测试集探索，不恢复训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance --draw-boxes && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：e104f972ebe14cc84c986b18a0d8ef1d95988eab
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json

## 结果
画框VQA完成exit0：全量1766 mIoU .678265/acc50 .737826，较无画框exact .651328提高2.694pp，但低于原score .691696约1.343pp。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 791,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.6782645720436292,
      "vqa_iou_acc50": 0.7378255945639864,
      "score_iou_mean": 0.6916960157722533,
      "score_iou_acc50": 0.7553793884484711,
      "first_iou_mean": 0.656632485224866,
      "first_iou_acc50": 0.7151755379388448,
      "oracle_iou_mean": 0.7573992982137026,
      "oracle_iou_acc50": 0.8306908267270668,
      "valid_vqa_answers": 786,
      "invalid_vqa_answers": 5,
      "improves_score": 76,
      "worsens_score": 96,
      "fixes_score_miss": 53,
      "breaks_score_hit": 84,
      "oracle_hit_samples": 1467,
      "vqa_hit_given_oracle_hit": 0.8882072256305386
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "vqa_iou_mean": 0.5817626636581641,
      "vqa_iou_acc50": 0.6207332490518331,
      "score_iou_mean": 0.6117499324631576,
      "score_iou_acc50": 0.6599241466498104,
      "first_iou_mean": 0.5334665001664629,
      "first_iou_acc50": 0.5701643489254109,
      "oracle_iou_mean": 0.7584401938937492,
      "oracle_iou_acc50": 0.8280657395701644,
      "valid_vqa_answers": 786,
      "invalid_vqa_answers": 5,
      "improves_score": 76,
      "worsens_score": 96,
      "fixes_score_miss": 53,
      "breaks_score_hit": 84,
      "oracle_hit_samples": 655,
      "vqa_hit_given_oracle_hit": 0.749618320610687
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.802136868521239,
        "vqa_iou_acc50": 0.8666666666666667,
        "score_iou_mean": 0.7959036041152275,
        "score_iou_acc50": 0.8611111111111112,
        "first_iou_mean": 0.782188525520559,
        "first_iou_acc50": 0.85,
        "oracle_iou_mean": 0.8462972143842374,
        "oracle_iou_acc50": 0.9222222222222223,
        "valid_vqa_answers": 51,
        "invalid_vqa_answers": 0,
        "improves_score": 4,
        "worsens_score": 4,
        "fixes_score_miss": 4,
        "breaks_score_hit": 3,
        "oracle_hit_samples": 166,
        "vqa_hit_given_oracle_hit": 0.9397590361445783
      },
      "LaSOT": {
        "samples": 600,
        "vqa_iou_mean": 0.6355869313120589,
        "vqa_iou_acc50": 0.7133333333333334,
        "score_iou_mean": 0.6537116103330052,
        "score_iou_acc50": 0.7366666666666667,
        "first_iou_mean": 0.625383400920118,
        "first_iou_acc50": 0.7,
        "oracle_iou_mean": 0.7167223918508266,
        "oracle_iou_acc50": 0.8083333333333333,
        "valid_vqa_answers": 244,
        "invalid_vqa_answers": 2,
        "improves_score": 26,
        "worsens_score": 34,
        "fixes_score_miss": 17,
        "breaks_score_hit": 31,
        "oracle_hit_samples": 485,
        "vqa_hit_given_oracle_hit": 0.8824742268041237
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.681621134997962,
        "vqa_iou_acc50": 0.72920892494929,
        "score_iou_mean": 0.6957865607639502,
        "score_iou_acc50": 0.7474645030425964,
        "first_iou_mean": 0.652727174200144,
        "first_iou_acc50": 0.6997971602434077,
        "oracle_iou_mean": 0.7659231510605866,
        "oracle_iou_acc50": 0.8275862068965517,
        "valid_vqa_answers": 491,
        "invalid_vqa_answers": 3,
        "improves_score": 46,
        "worsens_score": 58,
        "fixes_score_miss": 32,
        "breaks_score_hit": 50,
        "oracle_hit_samples": 816,
        "vqa_hit_given_oracle_hit": 0.8811274509803921
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "3a67c77b2e548f255f1b891ece30a5ab3d42fa527958fac9f868aa8cfe88a27f",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "image_presentation",
    "value": "outlined_numbered",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "native_bfloat16_no_adapter",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
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
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 16 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
不改Claim；无训练、无自动恢复或失败重试。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-drawn1766-20261018/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
