# e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis · 现在我想知道会不会多框输出的情景会更多了呢：只分析KL=0父训练已完成更新的现有日志，按相同早期更新窗口统计合法/raw多框、正负与拼图分层、advantage

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-sft659-seed11451`
- 来源版本：2026-10-14T15:40:57
- 状态：failed
- Workspace：03

## 本次任务
现在我想知道会不会多框输出的情景会更多了呢：只分析KL=0父训练已完成更新的现有日志，按相同早期更新窗口统计合法/raw多框、正负与拼图分层、advantage和Selected/Oracle定位；与会话中显式引用的beta=.04父训练 e014-structure-score-iou-explore-v1-sft659-seed11451 的同更新前缀进行描述性对比。不停训、不改变奖励、不执行checkpoint评测或Claim。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：独立一次性CPU日志分析。截取beta0父与本会话显式引用beta.04父各8rank日志固定字节及SHA；以共同连续完成更新范围（最大150）对齐，验证每个(rank,step,sample_id) G4组和正负/数据source一致，排除未完成更新。核验两trainer config除beta及独立输入输出路径外无其他差异，reward重算通过后报告合法/raw多框率、逐update和5update窗口、original正负/collage、advantage和Selected/Oracle IoU。只描述同seed初步对比，不作已验证因果结论；不改训练、不评测模型、不新增随机seed。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis/analyze.py
- 代码版本：f394b5704a9a258f4863e0d525ca5ca0a2bdec3b
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis/metrics.json

## 结果
尚无结果。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
