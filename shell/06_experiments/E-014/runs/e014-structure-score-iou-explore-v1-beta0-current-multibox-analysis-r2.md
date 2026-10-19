# e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2 · 继续完成用户当前问题：现在多框输出是否更多。首次只读分析因min参数类型错误没有形成结果，保留失败目录；独立修正版只读比较beta0与本会话显式引用beta.0

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-sft659-seed11451`
- 来源版本：2026-10-14T15:40:57
- 状态：analysis_pending
- Workspace：03

## 本次任务
继续完成用户当前问题：现在多框输出是否更多。首次只读分析因min参数类型错误没有形成结果，保留失败目录；独立修正版只读比较beta0与本会话显式引用beta.04训练同更新/同输入前缀，修正min(min(completed.values()),150)，不重跑训练、不改奖励或评测。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：首次只读分析min(completed.values(),150)类型错误已记录失败、原产物保留；本独立修正版为min(min(completed.values()),150)。只读beta0和显式beta.04训练日志固定字节快照，按共同连续完成前缀/每rank-step-sample_id G4组/正负source对齐，trainer_config除beta及独立路径外必须一致，reward重算。统计合法/raw多框率、每步/5步窗口、source分层、advantage与Selected/Oracle。无模型加载，不停训、不改奖励、无新随机seed；父采样seed11451。不把小样本单次seed对比当已验证因果结论。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/analyze.py
- 代码版本：f394b5704a9a258f4863e0d525ca5ca0a2bdec3b
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json

## 结果
匹配前1..15更新，beta0与beta.04各960rollout/240G4组，每rank/step/sample_id与source/正负一致，trainerconfig除beta与独立输入输出路径外相同；奖励重算通过。beta0合法多框63/960=6.5625%，raw78/960=8.125%，最后合法/raw多框均step6；step7..15全部0 raw。beta.04合法68/960=7.0833%，raw82/960=8.5417%，最后多框step8。collage正：47/424 vs53/424；original正：2/268 vs2/268；负：14/268 vs13/268。beta0多框adv正36/负27/均+.031037；对照35/33/均-.024689。两者正多框Selected/Oracle=.373129/.712301 vs .323409/.701139（49 vs55条），非固定测试集指标。前两步多框counts一致，此后两者都快速减少。

### 辅助指标
```json
[
  {
    "metric_id": "matched_updates",
    "value": 15,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta0.rollouts",
    "value": 960,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta0.valid_multi",
    "value": 63,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta0.raw_multi",
    "value": 78,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta0.multi_rate_all",
    "value": 0.065625,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta0.raw_multi_rate",
    "value": 0.08125,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta0.last_valid_multi_update",
    "value": 6,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta004.rollouts",
    "value": 960,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta004.valid_multi",
    "value": 68,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta004.raw_multi",
    "value": 82,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta004.multi_rate_all",
    "value": 0.07083333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta004.raw_multi_rate",
    "value": 0.08541666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "beta004.last_valid_multi_update",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 13 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### 结论范围
单次seed11451、相同早期完成更新与同输入组的描述性比较；目前未观察到关闭KL增加或延长多框，零KL仍快速收缩，不能把KL当作已证实唯一原因，也不能凭15步排除其长期影响。未测试/模型评测/改奖励或训练参数/停止父训练/改Claim。首次只读分析脚本TypeError的失败Run与快照保留，本r2为完成比较；无训练重跑。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2/logs/run.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
