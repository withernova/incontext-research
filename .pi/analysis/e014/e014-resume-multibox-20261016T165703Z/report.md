# E-014 一次性检查

仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。

窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。

```json
{
  "run_id": "e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150",
  "observed_utc": "2026-10-16T16:58:54.661387+00:00",
  "complete_step_count": 76,
  "window_steps": [
    256,
    257,
    258,
    259,
    260,
    261,
    262,
    263,
    264,
    265,
    266,
    267,
    268,
    269,
    270,
    271,
    272,
    273,
    274,
    275
  ],
  "overall": {
    "total": 2560,
    "valid": 2538,
    "valid_rate": 0.99140625,
    "valid_multibox": 1539,
    "multibox_per_all": 0.601171875,
    "multibox_per_valid": 0.6063829787234043,
    "valid_positive": 2002,
    "valid_positive_multibox": 1490,
    "selected_iou": 0.7345466543147852,
    "oracle_selected_gap": 0.04278380628339342,
    "unterminated": 17,
    "tiers": {
      "None": 2002
    }
  },
  "by_source": {
    "collage": {
      "total": 1488,
      "valid": 1467,
      "valid_rate": 0.9858870967741935,
      "valid_multibox": 1446,
      "multibox_per_all": 0.9717741935483871,
      "multibox_per_valid": 0.9856850715746421,
      "valid_positive": 1467,
      "valid_positive_multibox": 1446,
      "selected_iou": 0.7447407770078757,
      "oracle_selected_gap": 0.05162933165613545,
      "unterminated": 17,
      "tiers": {
        "None": 1467
      }
    },
    "original": {
      "total": 1072,
      "valid": 1071,
      "valid_rate": 0.9990671641791045,
      "valid_multibox": 93,
      "multibox_per_all": 0.08675373134328358,
      "multibox_per_valid": 0.08683473389355742,
      "valid_positive": 535,
      "valid_positive_multibox": 44,
      "selected_iou": 0.7065937982572831,
      "oracle_selected_gap": 0.01852887970056619,
      "unterminated": 0,
      "tiers": {
        "None": 535
      }
    }
  },
  "mixed_groups": 9,
  "within_group_multi_minus_single_advantage": 0.28073770559575184,
  "multibox_disappeared": false,
  "diagnosis": [
    "仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。",
    "窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。"
  ]
}
```
