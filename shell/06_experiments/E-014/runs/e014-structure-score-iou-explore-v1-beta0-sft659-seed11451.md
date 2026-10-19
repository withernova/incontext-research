# e014-structure-score-iou-explore-v1-beta0-sft659-seed11451 · 你可以试着关闭KL散度吗，将settings.trainer.beta=0.0：按用户要求执行独立fresh SFT659训练变体，只改beta .04→0，沿

- 父 Run：`e014-structure-score-iou-explore-v1-sft659-seed11451`
- 来源版本：2026-10-14T14:15:33
- 状态：failed
- Workspace：03

## 本次任务
你可以试着关闭KL散度吗，将settings.trainer.beta=0.0：按用户要求执行独立fresh SFT659训练变体，只改beta .04→0，沿用新structure_score_selected_iou_explore_v1奖励、多框prompt、G4、数据/seed/优化器/生成预算。不续训已收缩step150、不停当前评测、不自动恢复父训练；检验KL是否影响多框持续性，不能预先当作已验证原因。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：用户明确要求settings.trainer.beta=0.0；独立fresh原SFT659 policy+固定anchor，不从已收缩step150续训。复用已发布部署SHAf394b5704a9a258f4863e0d525ca5ca0a2bdec3b和新reward配置，只用CLI覆盖settings.trainer.beta=0.0/output.run_name，未改源码/奖励/旧Run。其余继承G4/multi_v2/seed11451/lr8e-5/3epochs/1500updates/192tokens/262144max_pixels/clip.2/save50/counterfactual0及7项新reward，原4000+1000对派生4000共8000条；实际快照仍须核验。beta0移除KL损失权重，现有anchor加载/重放保留；不增加score CE或偏好损失。先比较早期1..150的合法与raw多框/Selected-IoU/score错误/advantage；不预先归因KL。前次评测已结束、GPU空闲，新输出独立。未测试，不自动停止/评测新训练，不继承父停止或恢复行为。
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_structure_score_iou_explore_grpo.py settings.trainer.beta=0.0 output.run_name=e014-structure-score-iou-explore-v1-beta0-sft659-seed11451
- 代码版本：f394b5704a9a258f4863e0d525ca5ca0a2bdec3b
- 随机种子：11451
- 配置：configs/experiments/E-014/training/e014_structure_score_iou_explore_grpo.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451/metrics.json

## 结果
用户要求停止并评测step50；managed authorization/nonretryable记录主动停止后SIGTERM唯一output.run_name绑定beta0协调器，自有worker全退出，8rank最后52，8GPU各2MiB。保存step50 policy/config/optimizer非空，policy SHA256=d917925092923f0841ecc4cba74b7c8508bb80c95a4f17b3551a333e4fe0e18a，读取期间stat稳定；源snapshot beta0/new reward/G4/multi_v2已核验。51..52未保存，不用于step50评测；不是1500完成或算法崩溃，父训练保持停止。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
