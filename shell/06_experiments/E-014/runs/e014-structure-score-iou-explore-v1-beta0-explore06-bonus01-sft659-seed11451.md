# e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451 · 用户要求完成修改审阅后运行，并授权停止上一轮。独立fresh原SFT659训练：保持新奖励、beta0、低SelectedIoU探索扣分.6、G4/seed11

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451`
- 来源版本：2026-10-14T19:32:46
- 状态：failed
- Workspace：03

## 本次任务
用户要求完成修改审阅后运行，并授权停止上一轮。独立fresh原SFT659训练：保持新奖励、beta0、低SelectedIoU探索扣分.6、G4/seed11451及数据预算，仅新增合法正样本非近重复多框固定补偿.1，与SelectedIoU无关，不按数量累加，不恢复Coverage/Ranking等旧项。不续训上一轮、不覆盖产物；只核验一次启动健康和实际配置，不持续监控。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户已授权停止上一轮并完成修改审阅后运行。旧训练唯一协调器已SIGTERM，自有workers退出、8GPU无compute进程，保留产物。新奖励函数可选multibox_bonus_weight默认0；合法正样本且存在框间IoU<.9的一对时加一次.1，与SelectedIoU无关、不要求新增框命中或score门槛、不按框数累加；负样本/全近重复/单框0，非法总分仍-1、分项null。低SelectedIoU<.3正样本无非重复候选仍扣.6，独立日志multibox_bonus_eligible/multibox_bonus_reward。仅新增薄配置beta0/.6/.1，newreward原参数/路由/prompt/G4/seed11451/freshSFT659/lr8e-5/3epochs1500/save50/192tokens/CF0沿用，不恢复Coverage/Ranking/旧multi_bonus。旧variable_reward和coverage AST未变。5任务文件review041d971522cb2212 passed/current，测试缺失warning保留；AST/config差异/source-navigation/diff静态核对通过，未测试/build/import-smoke。使用已发布部署精确SHA7bb09c762b4e6030fe870b34f9c1a119d7c81425，独立目录、不覆盖/续训父Run。启动后仅一次健康/实际配置核验，不持续监控、自动停训或评测。
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_structure_score_iou_explore_multibox_bonus_grpo.py output.run_name=e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 配置：configs/experiments/E-014/training/e014_structure_score_iou_explore_multibox_bonus_grpo.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451/metrics.json

## 结果
用户切换0.5独立奖励变体，当前0.1训练按范围主动停止；8rank真实最后完成288，唯一协调器SIGTERM、自有workers退出，8GPU无compute进程；全部checkpoint/日志/数据保留，不是1500更新完成，不自动恢复。

### 局限
未测试；仅源代码审阅及AST/配置/导航静态核对、实际受管启动和配置核验。0.1补偿是否能维持有效多框仍待训练与评测，Claim不变。

### 结论范围
单seed独立新训练变体；当前无性能结论，多框比例不等于成功，Claim不变。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
