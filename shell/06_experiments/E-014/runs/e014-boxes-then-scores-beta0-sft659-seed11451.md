# e014-boxes-then-scores-beta0-sft659-seed11451 · 用户明确授权修改完成后训练且关闭KL；在新协议step0评测完成后，从原单框SFT659全新启动统一GRPO。boxes_then_scores_v1；beta

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451`
- 来源版本：2026-10-15T08:34:56
- 状态：failed
- Workspace：03

## 本次任务
用户明确授权修改完成后训练且关闭KL；在新协议step0评测完成后，从原单框SFT659全新启动统一GRPO。boxes_then_scores_v1；beta=0；exploration_penalty=0；multibox_bonus_weight=0；只保留结构/score/Selected IoU三主奖励。保留现有3epochs/1500updates、G4、seed11451、save50和数据构造，不恢复旧checkpoint，不持续监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：新协议boxes_then_scores_v1：先所有bbox再按序score；解析/奖励/评测显式路由；原始序列重放不变；review3086e33f5f827fb4通过，静态检查通过，未测试。全新SFT659；beta0、exploration_penalty0、multibox_bonus_weight0；score1.1/IoU1/order.12；G4/seed11451/3epochs1500updates/save50/lr8e-5/192tokens；原4000+对称4000；不resume。只做启动核验，无持续训练监控。
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_boxes_then_scores_grpo.py
- 代码版本：41698665d15742276bf22d1376e8d53a367c07db
- 随机种子：11451
- 配置：configs/experiments/E-014/training/e014_boxes_then_scores_grpo.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-sft659-seed11451/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-sft659-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-boxes-then-scores-beta0-sft659-seed11451/metrics.json

## 结果
尚无结果。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
