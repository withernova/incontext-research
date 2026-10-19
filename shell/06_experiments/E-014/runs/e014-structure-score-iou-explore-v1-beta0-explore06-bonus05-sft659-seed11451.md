# e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451 · 用户要求试着开启0.5额外多框奖励。独立fresh原SFT659，beta0和低SelectedIoU条件探索.6不变，仅合法正样本distinct一次补偿由.

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451`
- 来源版本：2026-10-14T23:54:19
- 状态：failed
- Workspace：03

## 本次任务
用户要求试着开启0.5额外多框奖励。独立fresh原SFT659，beta0和低SelectedIoU条件探索.6不变，仅合法正样本distinct一次补偿由.1改.5，与SelectedIoU无关、不要求新增命中或最低score、不按框数累加。保持G4/seed11451/数据/prompt/优化器/预算及新reward其他项。停止上一轮.1释放GPU、保留所有产物，不续训或覆盖。不持续监控，只受管启动与一次实际配置健康核验，不自动评测或停训。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户要求试着开启0.5额外多框奖励。独立fresh原SFT659，beta0和低SelectedIoU条件探索.6不变，仅合法正样本distinct一次补偿由.1改.5，与SelectedIoU无关、不要求新增命中或最低score、不按框数累加。保持G4/seed11451/数据/prompt/优化器/预算及新reward其他项。停止上一轮.1释放GPU、保留所有产物，不续训或覆盖。不持续监控，只受管启动与一次实际配置健康核验，不自动评测或停训。 复用已发布部署SHA7bb09c762b4e6030fe870b34f9c1a119d7c81425和现有薄配置，CLI只覆盖settings.trainer.reward.multibox_bonus_weight=0.5及独立run_name，不改代码或历史默认。源配置解析比较确认只有bonus/output差异，配置核对产物.pi/config-review/e014-positive-multibox-bonus05/effective_config.json；沿用reward_impl code_review041d971522cb2212（本次无新源码diff）。原4000+AB/BA/Ref派生4000、G4、seed11451、lr8e-5、3epochs1500updates、save50、192tokens、clip.2、纯GRPO/CF0，原SFT659无resume。负样本/单框/全近重复不加.5，非法总分仍-1，日志独立bonus分项。无测试/模型评测、无新部署或持续监控。
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_structure_score_iou_explore_multibox_bonus_grpo.py settings.trainer.reward.multibox_bonus_weight=0.5 output.run_name=e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 配置：configs/experiments/E-014/training/e014_structure_score_iou_explore_multibox_bonus_grpo.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451/metrics.json

## 结果
用户要求暂停并评测step350；8rank最后完成380，唯一协调器SIGTERM、自有workers退出，8GPU idle，所有产物保留。当前保持暂停，不是1500完成，不自动恢复。step350 policy SHA2399a6db32649adc219f4e85f859dd052cbc634fe85571e5aee087ccdb235a84，beta0/.6/.5/G4来源核验。

### 局限
未测试/模型评测；本次只有参数覆盖，无源码改动或新代码发布部署。0.5是否维持有效多框仍待训练，启动核验不是收益验证。

### 结论范围
单seed奖励系数变体，离线扫描仅提供候选依据，不证明新训练效果，Claim不变。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/config-review/e014-positive-multibox-bonus05/effective_config.json
.pi/config-review/e014-positive-multibox-bonus05/actual_config_audit.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
