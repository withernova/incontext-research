# E-014 一次性检查

仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。

窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。

```json
{
  "run_id": "e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451",
  "observed_utc": "2026-10-16T10:40:10.853440+00:00",
  "complete_step_count": 162,
  "window_steps": [
    142,
    143,
    144,
    145,
    146,
    147,
    148,
    149,
    150,
    151,
    152,
    153,
    154,
    155,
    156,
    157,
    158,
    159,
    160,
    161
  ],
  "overall": {
    "total": 2560,
    "valid": 2547,
    "valid_rate": 0.994921875,
    "valid_multibox": 1504,
    "multibox_per_all": 0.5875,
    "multibox_per_valid": 0.5904986258343149,
    "valid_positive": 1893,
    "valid_positive_multibox": 1379,
    "selected_iou": 0.7097221002194378,
    "oracle_selected_gap": 0.0593554613069679,
    "unterminated": 8,
    "tiers": {
      "None": 1893
    }
  },
  "by_source": {
    "collage": {
      "total": 1248,
      "valid": 1237,
      "valid_rate": 0.9911858974358975,
      "valid_multibox": 1234,
      "multibox_per_all": 0.9887820512820513,
      "multibox_per_valid": 0.9975747776879548,
      "valid_positive": 1237,
      "valid_positive_multibox": 1234,
      "selected_iou": 0.6979535499832303,
      "oracle_selected_gap": 0.07759702151297464,
      "unterminated": 8,
      "tiers": {
        "None": 1237
      }
    },
    "original": {
      "total": 1312,
      "valid": 1310,
      "valid_rate": 0.9984756097560976,
      "valid_multibox": 270,
      "multibox_per_all": 0.20579268292682926,
      "multibox_per_valid": 0.20610687022900764,
      "valid_positive": 656,
      "valid_positive_multibox": 145,
      "selected_iou": 0.7319137109544817,
      "oracle_selected_gap": 0.024957885125824104,
      "unterminated": 0,
      "tiers": {
        "None": 656
      }
    }
  },
  "mixed_groups": 17,
  "within_group_multi_minus_single_advantage": -0.21253435119819578,
  "multibox_disappeared": false,
  "diagnosis": [
    "仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。",
    "窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。"
  ]
}
```
