# e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis · 那根据目前的已训练的，多框比例怎么样：一次性只读当前beta0/探索.6父训练已完成更新，核验8rank共同连续完成日志、G4组和真实配置，统计合法/raw多框

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451`
- 来源版本：2026-10-14T17:05:35
- 状态：analysis_pending
- Workspace：03

## 本次任务
那根据目前的已训练的，多框比例怎么样：一次性只读当前beta0/探索.6父训练已完成更新，核验8rank共同连续完成日志、G4组和真实配置，统计合法/raw多框、最近窗口、original正负/collage及低IoU探索。不中断训练、不修改奖励、不进行模型评测或持续监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户本次请求一次性统计当前多框比例。仅0.6父训练：trainer_config、拼接rank完成日志及8rank rollouts固定字节快照+SHA；以8rank共同连续完成更新截断、G4组及reward按实际.6重算校验；统计全部/合法分母、raw多框、source正负分层、25步及最近20/50步窗口、最后多框更新与低IoU非重复探索比例。不读其他Run结果，不改训练，不模型评测、无持续监控。无新增seed，父采样11451。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/analyze.py
- 代码版本：599ed6809ba7b9fd36dde7e354605e56d306fbb5
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json

## 结果
一次性快照8rank共同完成1..122，7808rollout/1952G4组，7740合法；beta0/.6配置及按实际.6奖励重算、完整组核验通过。合法多框72/7808=.9221%（合法分母72/7740=.9302%）；raw85/7808=1.0886%，其中13非法。全部合法和raw多框都在前6步，第7..122无多框。最近20步1280条及最近50步3200条均0合法/raw多框。分层：collage正52/3696=1.4069%，original正4/2056=.1946%，负16/2056=.7782%。低IoU正975条只有31条非重复探索。多框adv34正/38负。0.6设置仍未维持多框，不作为参数因果或最终模型性能结论。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 122,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 7808,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 72,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate_all",
    "value": 0.009221311475409836,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "raw_multibox_count",
    "value": 85,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent20_multibox_count",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "recent50_multibox_count",
    "value": 0,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 7 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### 结论范围
仅当前KL0、探索.6训练已完成更新的固定日志快照；单seed训练诊断，未执行模型评测、不改Claim。不中断训练、不修改参数、不增加持续日志监控；只在本次用户请求下读取并登记统计。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis/logs/run.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
