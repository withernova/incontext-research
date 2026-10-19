# e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis · 用户问现在结果、多框是否改善。只读当前beta0/探索.6/补偿.1训练固定日志快照，核验8rank共同完成更新、G4和实际奖励，统计合法/raw多框及最近20

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451`
- 来源版本：2026-10-14T19:38:49
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户问现在结果、多框是否改善。只读当前beta0/探索.6/补偿.1训练固定日志快照，核验8rank共同完成更新、G4和实际奖励，统计合法/raw多框及最近20/50步、original正负/collage、Selected/First/Oracle定位与选框收益。显式对照本会话上一轮.6无.1的既有122步分析Run e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis 的固定source_snapshot，比较共同更新前缀和输入组。不停训练、不改参数、不重新采样/评测、不持续监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户请求当前多框是否改善；一次固定字节快照当前训练config/training.log/8rank rollout并保留SHA，截断8rank共同连续完成更新，完整G4组校验，重算含.1奖励。显式上一轮.6无.1对照使用既有122步分析Run不可变source_snapshot；仅共同完成前缀，核对实际配置仅补偿/独立路径差异、group keys/输入条件。报告合法/raw多框、近20/50和25步窗、source正负、First/Selected/Oracle及命中/选框救援，多框同组reward胜率。不加载模型、不重新采样/评测，不停训练或持续监控，无新增seed。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/analyze.py
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json

## 结果
一次快照8rank共同完成1..53，3392rollout/848G4组；实际beta0/.6/.1奖励重算及配置唯一差异/共同输入组校验通过。共同1..53：合法多框465/3392=13.7087%，上轮无.1为72/3392=2.1226%；raw507/3392=14.9469%，42非法。新分支窗口1..25=20.75%、26..50=8.3125%、51..53=0；最后多框39，40..53连续14步无raw或合法多框。近20步25/1280=1.9531%。collage多框388/1672=23.2057%，原正32/860=3.7209%，负45/860=5.2326%。420正多框First/Selected/Oracle=.4771867/.4345173/.7385533，选框41改善60损失；IoU.5候选可救133，实际救37/损56。新增补偿实际支付420次，其中232SelectedIoU>=.3。多框251正adv214负adv，99mixed组等权胜率.464646、mean差-.029722。前期多框增加但未持续，不构成最终模型性能改善或因果Claim。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 53,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 3392,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "groups",
    "value": 848,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 465,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate_all",
    "value": 0.13708726415094338,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent20_multibox_count",
    "value": 25,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent50_multibox_count",
    "value": 408,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "matched_updates",
    "value": 53,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis/metrics.json"
  }
]
```

### 分析
# E-014 新增0.1补偿：当前一次快照

分析 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis`。截至8rank共同完成53更新，3392 rollouts/848完整G4组。正式分析exit0，完整性、实际奖励重算、实际配置比较和同输入组核验通过；未执行模型评测或测试。

前期多框明显增加，但未持续。最后多框在39步，40–53连续14步没有合法/raw多框。

| 同前53步 | 无额外0.1 | 新增0.1 |
|---|---:|---:|
| 合法多框/全部生成 | 72/3392（2.12%） | 465/3392（13.71%） |
| 拼图正样本 | 52/1672（3.11%） | 388/1672（23.21%） |
| 原始正样本 | 4/860（0.47%） | 32/860（3.72%） |
| 原始负样本 | 16/860（1.86%） | 45/860（5.23%） |

新分支1–25/26–50/51–53窗口多框率20.75%/8.31%/0%。最近20步25/1280（1.95%）。raw多框507条，其中42非法，不能当合法多框。

420条合法正多框First/Selected/Oracle mIoU为0.47719/0.43452/0.73855。后续候选比首框更好151例，但实际选框相对首框41改善、60损失。IoU≥0.5：Oracle可救援133条；实际救援37条、损失56条。Oracle仅GT事后诊断，不能视为实际性能。

补偿实际生效420次，其中232条SelectedIoU≥0.3，确认补偿不局限低IoU。合法多框251正adv、214负adv；99同Query mixed组的组等权严格胜率46.46%，组等权mean(multi)-mean(single)=-0.02972。没有据此定位单一消失机理。

比较使用显式上一轮分析Run的不可变122步source_snapshot，只取共同前53步；实际配置除独立路径和新增multibox_bonus_weight=.1一致，输入group keys/条件匹配。两轮生成输出已随策略分化，单seed训练观察不能作稳定因果或测试集性能结论。父训练不停止、无持续监控，无Claim升级。

本地详细统计：analysis.json；SHA与完整性：integrity_audit.json；远端完整source_snapshot在本独立Run目录。


### 局限
前期多框增加但40..53已连续14步无多框；score选择损失多于收益。未测试/模型评测，不持续监控或自动停训。

### 结论范围
一次现有训练快照，显式上一轮同更新前缀描述性比较；单seed训练数据，不是checkpoint模型评测或参数因果结果，Claim不变。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/analysis/e014/e014-bonus01-multibox/analysis.json
.pi/analysis/e014/e014-bonus01-multibox/integrity_audit.json
.pi/analysis/e014/e014-bonus01-multibox/report.md

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
