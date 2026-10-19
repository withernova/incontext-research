# e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis · 用户问现在结果、多框是否又消失。仅当前beta0/.6探索/.1补偿训练一次固定快照，核验8rank共同连续完成更新及G4组、实际配置和奖励重算；报告合法/ra

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451`
- 来源版本：2026-10-14T19:38:49
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户问现在结果、多框是否又消失。仅当前beta0/.6探索/.1补偿训练一次固定快照，核验8rank共同连续完成更新及G4组、实际配置和奖励重算；报告合法/raw多框累计、最近20/50步、最后多框位置及source正负分层。不停止或改动训练，不执行模型评测、不持续监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户当前请求触发的一次只读现有日志分析；8rank共同连续完成更新截断，保留固定字节source_snapshot及SHA、G4组校验、实际.6/.1分项和总奖励重算，累计/25步/最近20及50窗/source正负/raw非法统计。原单次分析脚本复用，仅绑定当前Run和.1奖励项，不修改代码仓库/父训练，不模型推理或持续监控。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/analyze.py
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json

## 结果
最新固定快照8rank共同完成1..75，4800rollout/1200G4组、4728合法；beta0/.6/.1实际配置和奖励重算通过，排除pending0。合法多框467/4800=9.7292%，raw509含42非法。1..25/26..50/51..75多框332/133/2，率20.75%/8.3125%/.125%。近20步2/1280=.15625%，近50步135/3200=4.21875%；最近多框73。51..75仅2条均合法collage正样本、低IoU非近重复、adv均负。原正/负最后多框35/34。前期增加之后多框几乎消失，但不是严格零；累计比例不能代表当前输出。不改参数或训练、未测试/模型评测、不持续监控、无Claim升级。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 75,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 4800,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 467,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate_all",
    "value": 0.09729166666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "raw_multibox_count",
    "value": 509,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent20_multibox_count",
    "value": 2,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent50_multibox_count",
    "value": 135,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/metrics.json"
  }
]
```

### 分析
# 新增0.1补偿：75步最新快照

最新固定快照8rank共同完成1..75，4800rollout/1200G4组、4728合法；beta0/.6/.1实际配置和奖励重算通过，排除pending0。合法多框467/4800=9.7292%，raw509含42非法。1..25/26..50/51..75多框332/133/2，率20.75%/8.3125%/.125%。近20步2/1280=.15625%，近50步135/3200=4.21875%；最近多框73。51..75仅2条均合法collage正样本、低IoU非近重复、adv均负。原正/负最后多框35/34。前期增加之后多框几乎消失，但不是严格零；累计比例不能代表当前输出。不改参数或训练、未测试/模型评测、不持续监控、无Claim升级。

最近非零多框更新：[{"update": 73, "valid_multi": 2, "raw_multi": 2}]

分析Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis`。单seed训练日志观察，不是最终性能或因果结论。详见analysis.json与integrity_audit.json；完整只读source_snapshot及SHA在独立Run。


### 局限
未测试、未执行checkpoint评测；累计比例主要反映早期输出。

### 结论范围
仅当前训练固定日志快照，单seed；近期多框几乎消失但不为严格零，不作性能/因果Claim；不改动训练或持续监控。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/analysis/e014/e014-bonus01-latest/analysis.json
.pi/analysis/e014/e014-bonus01-latest/integrity_audit.json
.pi/analysis/e014/e014-bonus01-latest/report.md

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
