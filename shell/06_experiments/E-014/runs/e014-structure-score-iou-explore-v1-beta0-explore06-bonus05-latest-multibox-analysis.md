# e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis · 用户问现在进展。只对0.5父训练一次最新固定快照，核验8rank共同连续完成更新和G4/实际reward，统计多框累计、25步窗/最近20和50步、原正负/co

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451`
- 来源版本：2026-10-14T23:57:30
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户问现在进展。只对0.5父训练一次最新固定快照，核验8rank共同连续完成更新和G4/实际reward，统计多框累计、25步窗/最近20和50步、原正负/collage、最后多框、正样本Selected/Oracle IoU和负样本最大score。不中断或改训练，不执行模型评测/新采样，不持续监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户本次触发一次0.5训练固定字节快照：config/training.log/8rank rollouts+SHA，按共同连续完成更新截断，G4完整组及实际.6/.5奖励重算。报告25步及最近20/50窗、多框累计/原正负/collage/raw非法/最后多框，合法正样本Selected/Oracle训练IoU、负样本max-score。只读已有轨迹，无模型评测或新采样，不停训练/改参数/持续监控。本地辅助目录按用户整理要求放第二层.pi/analysis/e014/e014-bonus05-latest/。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/analyze.py
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json

## 结果
最新固定快照8rank共同完成1..377，24128rollout/6032G4组、23911合法；实际beta0/.6/.5奖励重算及G4核验通过。合法多框20547/24128=85.1583%（合法分母85.9312%），raw20730含183非法；最新377仍有多框。近50步3176/3200=99.25%，合法3178中3176为2框、2单框；近20步1262/1280=98.59375%，1262合法全部2框、18非法，raw1280全有多框。窗口1..25/26..50/51..75=21.75%/74.875%/81.75%，近段维持两框而非消失。原正/拼图/负累计多框87.72%/94.57%/64.09%。近50步合法正样本Selected/Oracle mIoU=.695579/.697942，负样本maxscore均值.049203；多框数量不代表有效覆盖或最终性能。当前形成广泛两框输出模式（负样本也如此），需后续评测确认用途。未测试/模型评测、不改训练/参数/Claim，不持续监控。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 377,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 24128,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 20547,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate_all",
    "value": 0.8515832228116711,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "raw_multibox_count",
    "value": 20730,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent20_multibox_count",
    "value": 1262,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent50_multibox_count",
    "value": 3176,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis/metrics.json"
  }
]
```

### 分析
# 额外0.5补偿：377步最新快照

Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis`。受管分析exit0/complete；仅一次固定字节快照，不持续监控。8rank共同完成377更新，24128生成/6032完整G4组，实际beta0/.6条件探索/.5额外补偿分项与总奖励重算通过。

## 当前观察

多框没有消失。累计合法多框20547/24128（85.16%），近50步3176/3200（99.25%），近20步1262/1280（98.59%）。近20步合法1262条全部2框，另18条非法；raw1280条全部有至少2个answer开头。

| 更新窗口 | 合法多框/全部生成 | 比例 |
|---|---:|---:|
| 1–25 | 348/1600 | 21.75% |
| 26–50 | 1198/1600 | 74.88% |
| 51–75 | 1308/1600 | 81.75% |
| 76–100 | 1344/1600 | 84.00% |
| 101–125 | 1249/1600 | 78.06% |
| 126–150 | 1447/1600 | 90.44% |
| 151–175 | 1593/1600 | 99.56% |
| 176–200 | 1389/1600 | 86.81% |
| 201–225 | 1165/1600 | 72.81% |
| 226–250 | 1409/1600 | 88.06% |
| 251–275 | 1599/1600 | 99.94% |
| 276–300 | 1597/1600 | 99.81% |
| 301–325 | 1597/1600 | 99.81% |
| 326–350 | 1594/1600 | 99.62% |
| 351–375 | 1583/1600 | 98.94% |
| 376–377 | 127/128 | 99.22% |

## 分层与质量

| 输入条件 | 全期多框比例 | 合法正样本Selected mIoU | 合法正样本Oracle mIoU |
|---|---:|---:|---:|
| collage:positive | 94.57% | 0.66575 | 0.70703 |
| original:negative | 64.09% | 不适用 | 不适用 |
| original:positive | 87.72% | 0.73468 | 0.74639 |

近50步合法正样本2375条：Selected mIoU=0.69558，Oracle=0.69794；负样本最大score均值=0.04920。这是训练观察，不是checkpoint评测，也不与不同条件组成窗口作因果比较。

近期基本固定两框，原始负样本也普遍两框，尽管负样本没有额外bonus。这表明出现广泛输出模式，不能仅用多框率判断有效实例覆盖、模型自适应候选数或最终定位收益。Oracle仅针对同Reference GT的事后候选上限，不是图中所有实例的覆盖指标。

## 边界

累计23911合法、217非法；raw多框20730中183非法。最新多框377。分析只按8rank共同连续完成更新截断，未完成行不混入。脚本保存source_snapshot及SHA，原日志和训练参数不变。

未测试/模型评测/新采样，Claim不变，不自动停训或评测。产物analysis.json与integrity_audit.json；本地目录保持在用户指定整理的第二层。


### 局限
训练窗口组成不同；模型近期广泛输出两框，负样本也如此。未测试/模型评测，不持续监控或修改训练。

### 结论范围
本父训练固定377步快照，单seed训练观察；当前两框持续但不代表实例覆盖或测试性能，未评测不升级Claim。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/analysis/e014/e014-bonus05-latest/analysis.json
.pi/analysis/e014/e014-bonus05-latest/integrity_audit.json
.pi/analysis/e014/e014-bonus05-latest/report.md

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
