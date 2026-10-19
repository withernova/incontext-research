# e014-structure-score-iou-explore-v1-latest-training-analysis · 现在看看截止目前的训练结果呢：只读取本父训练最新完成更新、checkpoint及rollout快照，分析奖励/置信度/定位/多框趋势；不停止训练，不执行chec

- 父 Run：`e014-structure-score-iou-explore-v1-sft659-seed11451`
- 来源版本：2026-10-14T11:58:42
- 状态：analysis_pending
- Workspace：03

## 本次任务
现在看看截止目前的训练结果呢：只读取本父训练最新完成更新、checkpoint及rollout快照，分析奖励/置信度/定位/多框趋势；不停止训练，不执行checkpoint评测，不改变奖励或Claim。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：复用已修正的变长候选日志分析方法；独立Run脚本读取父Run training.log和8rank rollouts固定字节快照+SHA256；提取拼接rank JSON，以共同连续完成更新为截断。核验G4分组、全部reward重算；按50update窗口及original正负/collage计算reward、score worst error、Selected/First/Oracle、探索扣分、多框率、zero advantage及最新checkpoint文件清单。不停止父训练、不执行模型或checkpoint评测。无新增随机seed，父采样seed11451；科学结果仅训练诊断。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-latest-training-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/analyze.py
- 代码版本：1e2caec81668dafaf015005415d219b4e5e4ca2e
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-latest-training-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-latest-training-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json

## 结果
快照共同完成1..129，共8256rollout/2064G4组，8190合法（99.20%），68多框全部出现在1..50；51..129的5056rollout无合法多框。窗口1..50/51..100/101..129：original正Selected mIoU=.682384/.731630/.708232，IoU>=.5=.772953/.814035/.792608；collage正mIoU=.564461/.695359/.719312，命中=.650998/.801079/.820250；original负平均Selected score=.522591/.163451/.087557，最坏score误差=.389540/.144185/.072919。最新checkpoint100有optimizer及非空policy/config。GPU计算仍活跃。累计奖励2.328562，探索扣分1138次；多框55正样本的First/Selected/Oracle=.320368/.323409/.701139与上次一致。定位改善主要来自单框，探索多框尚未持续。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 129,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 8256,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 68,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate",
    "value": 0.008302808302808303,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.mixed_prompt_groups",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_diff",
    "value": 0.42752712247849345,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.oracle_diff",
    "value": 0.4621222289553754,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.success05_diff",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_wins",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_ties",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.mixed_prompt_groups",
    "value": 17,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_diff",
    "value": -0.1523562912205018,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.oracle_diff",
    "value": 0.21684921845091018,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.success05_diff",
    "value": -0.1666666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_wins",
    "value": 0.30392156862745096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_ties",
    "value": 0.22549019607843138,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "collage_positive.mixed_prompt_groups",
    "value": 16,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_diff",
    "value": -0.188599004576689,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "collage_positive.oracle_diff",
    "value": 0.2015196552943811,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "collage_positive.success05_diff",
    "value": -0.20833333333333337,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_pair_wins",
    "value": 0.29166666666666663,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_pair_ties",
    "value": 0.20833333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 22 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### 结论范围
仅当前训练采样日志，窗口输入不同且policy持续变化，不能作固定测试集效果或多框因果结论；未进行checkpoint独立评测，不改Claim。最新checkpoint只核对文件存在非空，未加载验证。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-latest-training-analysis/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-latest-training-analysis/logs/run.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
