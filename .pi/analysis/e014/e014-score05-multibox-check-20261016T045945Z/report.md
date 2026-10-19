# E-014 一次性检查

仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。

窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。

存在较大选框差距；优先离线检查正确候选低分与错误候选高分，针对评分目标优化，不仅提高框数收益。

```json
{
  "run_id": "e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451",
  "observed_utc": "2026-10-16T05:00:07.323575+00:00",
  "complete_step_count": 51,
  "window_steps": [
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50
  ],
  "overall": {
    "total": 2560,
    "valid": 2529,
    "valid_rate": 0.987890625,
    "valid_multibox": 1749,
    "multibox_per_all": 0.683203125,
    "multibox_per_valid": 0.6915776986951364,
    "valid_positive": 1949,
    "valid_positive_multibox": 1482,
    "selected_iou": 0.5400933377337829,
    "oracle_selected_gap": 0.22607350065784437,
    "unterminated": 23,
    "tiers": {
      "None": 1949
    }
  },
  "by_source": {
    "collage": {
      "total": 1376,
      "valid": 1360,
      "valid_rate": 0.9883720930232558,
      "valid_multibox": 1227,
      "multibox_per_all": 0.8917151162790697,
      "multibox_per_valid": 0.9022058823529412,
      "valid_positive": 1360,
      "valid_positive_multibox": 1227,
      "selected_iou": 0.47073303465948996,
      "oracle_selected_gap": 0.2973230372908926,
      "unterminated": 13,
      "tiers": {
        "None": 1360
      }
    },
    "original": {
      "total": 1184,
      "valid": 1169,
      "valid_rate": 0.987331081081081,
      "valid_multibox": 522,
      "multibox_per_all": 0.4408783783783784,
      "multibox_per_valid": 0.446535500427716,
      "valid_positive": 589,
      "valid_positive_multibox": 255,
      "selected_iou": 0.7002461597728973,
      "oracle_selected_gap": 0.061558441539091256,
      "unterminated": 10,
      "tiers": {
        "None": 589
      }
    }
  },
  "mixed_groups": 28,
  "within_group_multi_minus_single_advantage": -0.258771682980563,
  "multibox_disappeared": false,
  "diagnosis": [
    "仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。",
    "窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。",
    "存在较大选框差距；优先离线检查正确候选低分与错误候选高分，针对评分目标优化，不仅提高框数收益。"
  ]
}
```
