# e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis · 根据目前训练结果分析为什么多框逐渐消失：只用父训练保存日志1..150，检查同prompt组奖励/advantage、探索扣分触发与组内差异、raw多框非法及t

- 父 Run：`e014-structure-score-iou-explore-v1-sft659-seed11451`
- 来源版本：2026-10-14T14:15:33
- 状态：analysis_pending
- Workspace：03

## 本次任务
根据目前训练结果分析为什么多框逐渐消失：只用父训练保存日志1..150，检查同prompt组奖励/advantage、探索扣分触发与组内差异、raw多框非法及token预算、选择质量与score误差、GRPO/KL实现；不改奖励、训练、评测或Claim，不运行新模型实验。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：独立一次性只读诊断，仅已保存训练rollout1..150，排除151..154。复用完成rank拼接日志解析、snapshot SHA256、G4分组、奖励重算。新增raw answer openings/非法原因/token budget、同prompt多框advantage、结构/score/IoU/探索分项差额、整组统一探索扣分统计、在固定样本上以.2/.4/.6/1.0探索扣分重评分（不运行不同policy、不预测更改参数的真实收益）、多框回答裁为第一框的离线奖励对比。无随机seed、无模型加载，不修改代码仓库或当前eval；记录KL与EOS候选概率未单独保存的诊断缺口。当前部署SHAf394只新增评测配置，训练reward实现SHA1e2caec保持。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/analyze.py
- 代码版本：f394b5704a9a258f4863e0d525ca5ca0a2bdec3b
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json

## 结果
仅1..150共9600rollout/2400G4组，排除151..154的256条。全部82原始多框尝试（68合法、14非法）均在前8步，第9步后0 raw多框。合法多框35正adv/33负adv、mean-.024689；14非法多框均负adv(mean-1.161366)，10条未终止且耗尽192token；raw多框meanadv-.218756。17正混合prompt组：multi-single结构-.037647、加权score-.379600、selectedIoU-.152356、探索+.078431、total-.491172。55正多框裁至首框的离线对比：multi比first-only平均reward-.226630，其中score-.29149、structure-.054545、IoU+.003041、explore+.116364。1770正prompt组中498有低IoU，475没有合法多框，179四条统一扣分；296探索分项不同组中289仅单框定位差异，7涉及多框；26正组含合法多框。固定已有55正多框样本扣分重评分：.2/.4正优势均29条，.6/1.0均31条，不预测训练后分布。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 150,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "rollouts",
    "value": 9600,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_count",
    "value": 68,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_rate",
    "value": 0.0071331165425364525,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "original_positive.mixed_prompt_groups",
    "value": 1,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_diff",
    "value": 0.42752712247849345,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "original_positive.oracle_diff",
    "value": 0.4621222289553754,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "original_positive.success05_diff",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_wins",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "original_positive.selected_pair_ties",
    "value": 0.5,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "all_positive.mixed_prompt_groups",
    "value": 17,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_diff",
    "value": -0.1523562912205018,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "all_positive.oracle_diff",
    "value": 0.21684921845091018,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "all_positive.success05_diff",
    "value": -0.1666666666666667,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_wins",
    "value": 0.30392156862745096,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "all_positive.selected_pair_ties",
    "value": 0.22549019607843138,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "collage_positive.mixed_prompt_groups",
    "value": 16,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_diff",
    "value": -0.188599004576689,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "collage_positive.oracle_diff",
    "value": 0.2015196552943811,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "collage_positive.success05_diff",
    "value": -0.20833333333333337,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_pair_wins",
    "value": 0.29166666666666663,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "collage_positive.selected_pair_ties",
    "value": 0.20833333333333334,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "raw_multibox_count",
    "value": 82,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "raw_multibox_invalid_count",
    "value": 14,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "valid_multibox_last_update",
    "value": 8,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  },
  {
    "metric_id": "exploration_mixed_groups",
    "value": 296,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json"
  }
]
```

### 分析
Managed execution exited successfully with 0 declared and 26 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

### 结论范围
仅当前Run已保存日志及确定性奖励反事实重评分；不能证明某因素为唯一原因，不能把重评分当新policy消融。数学上同组统一扣分不改变标准化adv；最大score误差新增候选不减，已记录置信度错误抵消补偿。源码未发现显式框数/长度奖励惩罚，token平均归约和全回答adv、冻结SFT anchor/KL均存在；EOS继续概率及KL分项未单独记录，需后续固定prompt/checkpoint probing才能验证。未测试/新模型实验/改奖励/干预当前eval/改Claim。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/metrics.json
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis/logs/run.log

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
