# e014-score05-multibox-check-20261016T045945Z · 用户询问当前训练是否存在多框问题；仅一次日志快照，分完整步窗口分析多框、合法率、候选增益和选择差距，不修改训练。

- 父 Run：`e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451`
- 来源版本：2026-10-16T09:43:54
- 状态：ready_to_run
- Workspace：03

## 本次任务
用户询问当前训练是否存在多框问题；仅一次日志快照，分完整步窗口分析多框、合法率、候选增益和选择差距，不修改训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 命令：<PI_STEWARD_PREPARE_RUNTIME_COMMAND>
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score05-multibox-check-20261016T045945Z/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score05-multibox-check-20261016T045945Z/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-score05-multibox-check-20261016T045945Z/metrics.json

## 结果
尚无结果。

### 分析
一次日志快照，8rank共有51个完整rollout步（原始编号0..50）。合法多框/全部：前20步43.01%、随后20步69.96%、最后11步57.67%，未消失但后段回落。最近20步2560条，合法2529，合法多框1749=68.32%，拼图89.17%、原图44.09%。1949合法正样本Selected=.540093、Oracle=.766167，gap=.226074；拼图gap=.297323。1482合法正多框中554后框改善Oracle、513后框补救首框未命中。仅28个混合单多框同输入组，多框平均advantage差-.258772，样本受条件筛选，不推断总体因果或未来坍缩。未修改训练、未新增测试、不持续监控；结果为训练采样，不替代固定验证。 完整报告 .pi/analysis/e014/e014-score05-multibox-check-20261016T045945Z/extended_report.json

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
