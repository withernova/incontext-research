# e014-score04-step200-native-vqa-exact1766-20261018 · 用户要求在上一版VQA提示词中强调Reference同一个体exactly出现在Query中，然后重测。只变prompt_variant=exact_insta

- 父 Run：`e014-score04-step200-native-vqa1766-20261018`
- 来源版本：2026-10-18T11:23:46
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户要求在上一版VQA提示词中强调Reference同一个体exactly出现在Query中，然后重测。只变prompt_variant=exact_instance，增加同一个体及位置/尺度/姿态/光照/可见范围变化说明；冻结原1766正样本manifest与历史score0.4/G4/step200候选、原顺序，791多框原始Qwen3-VL-8B-Instruct BF16/SDPA零训练VQA，964单框保留、11无候选0。seed20260901、8rank、greedy16、require_eos、vision4096均同父。禁止原score/QueryGT输入，不声称候选必有正确框。独立输出，配对比较旧prompt/VQA与原score/Oracle；同测试集探索性诊断，不恢复训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：test ! -e /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json && test ! -L /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json && PYTHONPATH=. OMP_NUM_THREADS=1 /songzhengyue/miniconda3/envs/IPLoc/bin/python -m torch.distributed.run --standalone --nproc_per_node=8 tools/evaluate_candidate_vqa.py --manifest /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/inputs/manifest.json --manifest-sha256 8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d --predictions /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-discovery-score04-step200-eval1766-20261015T152856Z/payload/evaluation/predictions.jsonl --predictions-sha256 1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129 --model-path /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/models/Qwen3-VL-8B-Instruct --output-dir /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/payload --expected-samples 1766 --expected-multi 791 --seed 20260901 --max-new-tokens 16 --vision-max-patch-tokens 4096 --prompt-variant exact_instance && cp /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/payload/metrics.json /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json && echo SURVEY_TOOL_RUN_COMPLETE
- 代码版本：1d9357bf452e68d56e9111ad0b0572cf27fa6bf7
- 随机种子：20260901
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json

## 结果
exact-instance VQA exit0，1766完整覆盖/791多框均合法。全量mIoU .651328 vs旧prompt .651664（-0.03355pp），acc50同为.707814；没有改善。原score .691696。

### 辅助指标
```json
[
  {
    "metric_id": "status",
    "value": "completed",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "action",
    "value": "candidate_vqa",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "evaluated_samples",
    "value": 1766,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "world_size",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "vqa_samples",
    "value": 791,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "all",
    "value": {
      "samples": 1766,
      "vqa_iou_mean": 0.6513281044883926,
      "vqa_iou_acc50": 0.7078142695356738,
      "score_iou_mean": 0.6916960157722533,
      "score_iou_acc50": 0.7553793884484711,
      "first_iou_mean": 0.656632485224866,
      "first_iou_acc50": 0.7151755379388448,
      "oracle_iou_mean": 0.7573992982137026,
      "oracle_iou_acc50": 0.8306908267270668,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 55,
      "worsens_score": 131,
      "fixes_score_miss": 35,
      "breaks_score_hit": 119,
      "oracle_hit_samples": 1467,
      "vqa_hit_given_oracle_hit": 0.8520790729379687
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "multi",
    "value": {
      "samples": 791,
      "vqa_iou_mean": 0.5216238498749177,
      "vqa_iou_acc50": 0.5537294563843237,
      "score_iou_mean": 0.6117499324631576,
      "score_iou_acc50": 0.6599241466498104,
      "first_iou_mean": 0.5334665001664629,
      "first_iou_acc50": 0.5701643489254109,
      "oracle_iou_mean": 0.7584401938937492,
      "oracle_iou_acc50": 0.8280657395701644,
      "valid_vqa_answers": 791,
      "invalid_vqa_answers": 0,
      "improves_score": 55,
      "worsens_score": 131,
      "fixes_score_miss": 35,
      "breaks_score_hit": 119,
      "oracle_hit_samples": 655,
      "vqa_hit_given_oracle_hit": 0.6687022900763359
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "by_dataset",
    "value": {
      "GOT10k": {
        "samples": 180,
        "vqa_iou_mean": 0.7518831905179036,
        "vqa_iou_acc50": 0.8111111111111111,
        "score_iou_mean": 0.7959036041152275,
        "score_iou_acc50": 0.8611111111111112,
        "first_iou_mean": 0.782188525520559,
        "first_iou_acc50": 0.85,
        "oracle_iou_mean": 0.8462972143842374,
        "oracle_iou_acc50": 0.9222222222222223,
        "valid_vqa_answers": 51,
        "invalid_vqa_answers": 0,
        "improves_score": 1,
        "worsens_score": 11,
        "fixes_score_miss": 1,
        "breaks_score_hit": 10,
        "oracle_hit_samples": 166,
        "vqa_hit_given_oracle_hit": 0.8795180722891566
      },
      "LaSOT": {
        "samples": 600,
        "vqa_iou_mean": 0.6252419690827077,
        "vqa_iou_acc50": 0.6966666666666667,
        "score_iou_mean": 0.6537116103330052,
        "score_iou_acc50": 0.7366666666666667,
        "first_iou_mean": 0.625383400920118,
        "first_iou_acc50": 0.7,
        "oracle_iou_mean": 0.7167223918508266,
        "oracle_iou_acc50": 0.8083333333333333,
        "valid_vqa_answers": 246,
        "invalid_vqa_answers": 0,
        "improves_score": 23,
        "worsens_score": 38,
        "fixes_score_miss": 12,
        "breaks_score_hit": 36,
        "oracle_hit_samples": 485,
        "vqa_hit_given_oracle_hit": 0.8618556701030928
      },
      "TAO": {
        "samples": 986,
        "vqa_iou_mean": 0.6488451082998522,
        "vqa_iou_acc50": 0.6957403651115619,
        "score_iou_mean": 0.6957865607639502,
        "score_iou_acc50": 0.7474645030425964,
        "first_iou_mean": 0.652727174200144,
        "first_iou_acc50": 0.6997971602434077,
        "oracle_iou_mean": 0.7659231510605866,
        "oracle_iou_acc50": 0.8275862068965517,
        "valid_vqa_answers": 494,
        "invalid_vqa_answers": 0,
        "improves_score": 31,
        "worsens_score": 82,
        "fixes_score_miss": 22,
        "breaks_score_hit": 73,
        "oracle_hit_samples": 816,
        "vqa_hit_given_oracle_hit": 0.8406862745098039
      }
    },
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_manifest_sha256",
    "value": "8a873e3605e7a8b429dda33d84e197b60ee4dd0db262a1949e4cbe5ceb6b1e2d",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "source_predictions_sha256",
    "value": "1a864fdce10f300ec53ddf2945b7e2d063c74280d7a750207dcff99a7ff76129",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_sha256",
    "value": "b737f254c6c86215fa009600eccad51ac741cb46db6e7188aacfe3f390f7f6f2",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "prompt_variant",
    "value": "exact_instance",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "selector",
    "value": "native_bfloat16_no_adapter",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  },
  {
    "metric_id": "candidate_order",
    "value": "source",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
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
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 15 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### Claim 边界
同测试集提示词探索性诊断，不作为独立测试收益；不证明GRPO因果，不训练、不恢复训练。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score04-step200-native-vqa-exact1766-20261018/managed_console.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
