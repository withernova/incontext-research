# e014-structure-score-iou-explore-v1-current-multibox-analysis-r2 · 继续完成用户当前多框是否带来更好结果的分析：首次分析逐行JSON解析漏掉拼接rank完成日志；以已保存的同一固定快照重新解析，8rank完整1..68已核验。保

- 父 Run：`e014-structure-score-iou-explore-v1-sft659-seed11451`
- 来源版本：2026-10-14T11:58:42
- 状态：analysis_pending
- Workspace：03

## 本次任务
继续完成用户当前多框是否带来更好结果的分析：首次分析逐行JSON解析漏掉拼接rank完成日志；以已保存的同一固定快照重新解析，8rank完整1..68已核验。保留首次分析产物，只修正日志解析，不重新采样、不停训、不改奖励或指标。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：复用首次分析的source_snapshot固定字节及hash；仅修正training.log中拼接的rank JSON解析。8rank完整1..68为共同完成更新，zero-based rollout 0..67。其余统计和完整性核验不变，首次分析结果保留且标明仅step1受限解析。一次性脚本在独立r2 Run，不改仓库，不测试，不调用模型。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/analyze.py
- 代码版本：1e2caec81668dafaf015005415d219b4e5e4ca2e
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json

## 结果
固定快照完成1..68，4352 rollout/1088 G4组，4296合法、68多框，其中55正样本多框：First/Selected/Oracle mIoU=.320368/.323409/.701139；IoU>=.5为20/21/44。后框更好30例，实际较首框改善7/恶化7；Oracle可救首框24例，Selected救6/损失5。17同prompt正混合组，组均Selected差-.152356、Oracle差+.216849；16拼图组Selected差-.188599。51..68共1152rollout没有合法多框。覆盖潜力尚未转化为最终定位收益，训练诊断非heldout/因果证据。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 68,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 4352,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 68,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate",
    "value": 0.015828677839851025,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "original_positive.mixed_prompt_groups",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_diff",
    "value": 0.42752712247849345,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "original_positive.oracle_diff",
    "value": 0.4621222289553754,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "original_positive.success05_diff",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_wins",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_ties",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "all_positive.mixed_prompt_groups",
    "value": 17,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_diff",
    "value": -0.1523562912205018,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "all_positive.oracle_diff",
    "value": 0.21684921845091018,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "all_positive.success05_diff",
    "value": -0.1666666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_wins",
    "value": 0.30392156862745096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_ties",
    "value": 0.22549019607843138,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "collage_positive.mixed_prompt_groups",
    "value": 16,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_diff",
    "value": -0.188599004576689,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "collage_positive.oracle_diff",
    "value": 0.2015196552943811,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "collage_positive.success05_diff",
    "value": -0.20833333333333337,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_pair_wins",
    "value": 0.29166666666666663,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_pair_ties",
    "value": 0.20833333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 22 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### 结论范围
仅该新奖励训练的固定采样快照；小样本、模型自行决定候选数量、训练中policy变化；不能证明多框因果收益或整体模型评测提升；Oracle是诊断，不能代替最终选框。首次analysis仅逐行解析step1局限已纠正，原产物保留，以r2为本次完整分析。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2/logs/run.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
