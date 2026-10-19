# e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis · 用户问当前0.5训练是否再次消失。仅本父Run一次固定日志快照，核验beta0/.6条件探索/.5补偿与8rank共同完成更新/G4组和实际奖励，统计合法/ra

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451`
- 来源版本：2026-10-14T23:57:30
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户问当前0.5训练是否再次消失。仅本父Run一次固定日志快照，核验beta0/.6条件探索/.5补偿与8rank共同完成更新/G4组和实际奖励，统计合法/raw多框、25步和最近20/50窗口、最后多框及原正负/collage。不中断或修改训练、不重新采样/模型评测、不持续监控。用户同时要求整理分析log，本地或服务器整理位置待确认，保护训练checkpoint和历史执行事实。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：一次本父训练固定字节config/training.log/8rank rollouts快照+SHA；8rank共同连续完成更新截断，G4组/实际.6+.5奖励重算核验，累计与25步/近20/50步/source正负分层、raw非法/最后多框统计。复用此前一次分析脚本，只改绑定与bonus核验为.5，父训练不停止/改参数；不模型评测或持续监控。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/analyze.py
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json

## 结果
本次一次固定快照8rank共同完成1..18，1152rollout/288G4组，1124合法；实际beta0/.6探索/.5额外补偿重算通过。合法多框207/1152=17.96875%（合法分母18.4164%），raw222含15非法；最后多框18且该步17/64，未见持续消失。短窗口1..6/7..12/13..18为101/31/75（26.3021%/8.0729%/19.53125%），中段降后回升。collage正178/536=33.209%、原正4/308=1.2987%、负25/308=8.1169%，多框116正adv91负adv。只有18步，不能推断后续持续性或定位改善。用户同时要求整理分析log：默认本地.pi/analysis/e014/归档10辅助目录51文件，逐文件SHA/size不变，4个canonical Run本地artifact引用更新；服务器原Run/训练checkpoint不搬动。未测试/模型评测、不改训练或持续监控。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 18,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 1152,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 207,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate_all",
    "value": 0.1796875,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "raw_multibox_count",
    "value": 222,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent20_multibox_count",
    "value": 207,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent50_multibox_count",
    "value": 207,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis/metrics.json"
  }
]
```

### 分析
# 0.5额外多框补偿：18步快照

分析 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis`。受管exit0/complete，8rank共同连续更新/G4完整组和实际奖励重算核验通过。

本次一次固定快照8rank共同完成1..18，1152rollout/288G4组，1124合法；实际beta0/.6探索/.5额外补偿重算通过。合法多框207/1152=17.96875%（合法分母18.4164%），raw222含15非法；最后多框18且该步17/64，未见持续消失。短窗口1..6/7..12/13..18为101/31/75（26.3021%/8.0729%/19.53125%），中段降后回升。collage正178/536=33.209%、原正4/308=1.2987%、负25/308=8.1169%，多框116正adv91负adv。只有18步，不能推断后续持续性或定位改善。用户同时要求整理分析log：默认本地.pi/analysis/e014/归档10辅助目录51文件，逐文件SHA/size不变，4个canonical Run本地artifact引用更新；服务器原Run/训练checkpoint不搬动。未测试/模型评测、不改训练或持续监控。

| 更新窗口 | 合法多框/全部生成 | 比例 |
|---|---:|---:|
| 1–6 | 101/384 | 26.30% |
| 7–12 | 31/384 | 8.07% |
| 13–18 | 75/384 | 19.53% |

这是单seed早期训练观察，未执行checkpoint评测或测试，Claim不变。父训练保持原配置，只在用户请求下做一次快照。

本地分析目录已归入第二层`.pi/analysis/e014/`，索引与移动前后路径/SHA见上级README.md及directory_migration_20261015.json。当前训练启动控制脚本保持原位置。


### 局限
只有18共同完成步；多框主要在collage，原正低比例。未测试或模型评测。整理限本地辅助副本和路径引用，不改变服务器执行事实。

### 结论范围
仅当前beta0/.6/.5训练一次早期18步固定快照，单seed不作后续持续性/性能/因果Claim；不中断训练或持续监控。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/analysis/e014/e014-bonus05-current/analysis.json
.pi/analysis/e014/e014-bonus05-current/integrity_audit.json
.pi/analysis/e014/e014-bonus05-current/short_windows.json
.pi/analysis/e014/e014-bonus05-current/report.md

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
