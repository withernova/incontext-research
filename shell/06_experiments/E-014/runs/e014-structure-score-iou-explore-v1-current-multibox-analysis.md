# e014-structure-score-iou-explore-v1-current-multibox-analysis · 我想知道目前的多框目测是否带来了更好的结果呢：只分析父训练当前已有rollout，按完成更新及同prompt组比较单框与多框Selected/Oracle Io

- 父 Run：`e014-structure-score-iou-explore-v1-sft659-seed11451`
- 来源版本：2026-10-14T11:58:42
- 状态：analysis_pending
- Workspace：03

## 本次任务
我想知道目前的多框目测是否带来了更好的结果呢：只分析父训练当前已有rollout，按完成更新及同prompt组比较单框与多框Selected/Oracle IoU、置信度选择和低IoU探索；不启动checkpoint评测，不停训、不改奖励、不恢复其他Run。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：一次性只读分析，script位于独立子Run/analyze.py；从父training.log取8rank共同连续完成更新上限，仅纳入rollout zero-based step<cutoff。固定字节快照及SHA256、G4同rank/step/sample_id分组和奖励重算核验；按original正负/collage及50update窗口计算First/Selected/Oracle和同prompt单框多框均值差。不中断训练、不加载模型、不改仓库。分析不使用额外seed，沿用父采样seed11451；分析脚本无随机操作。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/analyze.py
- 代码版本：1e2caec81668dafaf015005415d219b4e5e4ca2e
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json

## 结果
首次分析按整行JSON解析，多rank完成输出拼接导致仅纳入step1；该局限已核查并在独立r2使用完全相同快照纠正。首次产物保留，不能作为截至当前全程的多框收益判断；本次完整结果见e014-structure-score-iou-explore-v1-current-multibox-analysis-r2（完成1..68、4352rollout）。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 64,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 18,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate",
    "value": 0.33962264150943394,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.mixed_prompt_groups",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_diff",
    "value": 0.42752712247849345,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.oracle_diff",
    "value": 0.4621222289553754,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.success05_diff",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_wins",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_ties",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.mixed_prompt_groups",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_diff",
    "value": 0.42752712247849345,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.oracle_diff",
    "value": 0.4621222289553754,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.success05_diff",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_wins",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_ties",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 16 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### 结论范围
仅首次受限解析产物；后续完整分析r2优先，不作为完整训练趋势证据。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis/logs/run.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
