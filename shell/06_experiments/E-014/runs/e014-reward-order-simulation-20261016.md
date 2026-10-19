# e014-reward-order-simulation-20261016 · 用户要求编写并执行纯合成离线奖励模拟，比较讨论中的硬档位与较平滑方案，穷举单/双候选网格、十五种行为示例和阈值反例；不读训练产物、不修改训练奖励、不训练。

- 父 Run：`e014-discovery-priority-score04-beta0-sft659-200step-seed11451`
- 来源版本：2026-10-15T23:28:56
- 状态：ready_to_run
- Workspace：03

## 本次任务
用户要求编写并执行纯合成离线奖励模拟，比较讨论中的硬档位与较平滑方案，穷举单/双候选网格、十五种行为示例和阈值反例；不读训练产物、不修改训练奖励、不训练。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：纯本地标准库CLI tools/simulate_candidate_rewards.py；基线1c47c7305c695151df81d46019143028e01752ad，新增脚本和README尚未提交。当前工具未提供code_change_review，未声称专用审阅通过。已实际执行用户要求的数值模拟、手算例子assert及导航/diff静态检查。
- 命令：<PI_STEWARD_PREPARE_RUNTIME_COMMAND>
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reward-order-simulation-20261016/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reward-order-simulation-20261016/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-reward-order-simulation-20261016/metrics.json

## 结果
尚无结果。

### 分析
离线合成模拟完成，单/双候选386262组，另含15类行为示例（M6用三框）。硬档位10/10跨档关系成立；较平滑方案仅1/10满足跨全网格严格分离，不能解释为实际样本90%排序错误。固定score=.1/.1、第一框IoU=.1，第二框IoU .4999→.5001时，较平滑reward 1.225625→.906375，下降.31925，源于二值score标签跳变。未改变训练奖励，未启动训练；合成网格不代表实际分布或训练效果。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-order-simulation-20261016/final/results.json
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-order-simulation-20261016/final/examples.csv
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-order-simulation-20261016/final/transitions.csv
/home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-reward-order-simulation-20261016/final/report.md

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
