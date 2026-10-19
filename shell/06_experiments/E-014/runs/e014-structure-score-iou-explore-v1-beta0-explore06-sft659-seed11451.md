# e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451 · 改好了就直接运行吧，也不要过多去监控：用户授权独立fresh SFT659训练，保持beta=0，只将条件探索扣分从0.2改到0.6。低Selected IoU

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-sft659-seed11451`
- 来源版本：2026-10-14T16:34:40
- 状态：failed
- Workspace：03

## 本次任务
改好了就直接运行吧，也不要过多去监控：用户授权独立fresh SFT659训练，保持beta=0，只将条件探索扣分从0.2改到0.6。低Selected IoU<.3正样本且没有预测框间IoU<.9的一对时扣.6，有非近重复候选解除一次扣分，不要求新增框命中。新奖励/G4/seed11451/学习率/数据/预算均沿用；旧训练保持停止，当前step50评测不打断；只核验启动与实际配置，不持续日志监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户已明确授权改好直接运行且不要过多监控。复用已发布部署SHA599ed6809ba7b9fd36dde7e354605e56d306fbb5和新reward配置；CLI settings.trainer.beta=0.0/settings.trainer.reward.exploration_penalty=0.6/output.run_name独立覆盖。源配置解析比较确认与beta0/.2基线只改变exploration_penalty，review artifact=.pi/config-review/e014-explore06/effective_config.json；新scheme structure_score_selected_iou_explore_v1，threshold .3/.5/.9和score1.1/IoU1/order.12不变。fresh原SFT659，无resume；G4/seed11451/lr8e-5/3epochs/1500updates/192tokens/max_pixels262144/clip.2/save50/counterfactual0，原4000+派生4000数据契约沿用。只低SelectedIoU<.3正样本缺非近重复候选扣.6，解除一次扣分，不要求新增框命中，不改变负样本或非法总分。无源码改动/新增训练runner/发布/部署/测试；原step50eval已结束且GPU空闲。只做受管启动检查和一次实际配置核验，不持续日志监控、自动停训或自动评测。
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_structure_score_iou_explore_grpo.py settings.trainer.beta=0.0 settings.trainer.reward.exploration_penalty=0.6 output.run_name=e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451
- 代码版本：599ed6809ba7b9fd36dde7e354605e56d306fbb5
- 随机种子：11451
- 配置：configs/experiments/E-014/training/e014_structure_score_iou_explore_grpo.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451/metrics.json

## 结果
尚无结果。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
