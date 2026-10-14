# e014-multi-bonus02-g8-sft659-seed11451 · 用户选方案1并要求重新训练及约400步自动评测：新独立训练从原SFT659 fresh policy+固定anchor，纯GRPO；仅settings.trai

- 父 Run：`e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2`
- 来源版本：2026-10-13T23:34:27.083208
- 状态：failed
- Workspace：03

## 本次任务
用户选方案1并要求重新训练及约400步自动评测：新独立训练从原SFT659 fresh policy+固定anchor，纯GRPO；仅settings.trainer.group_size从4改8，沿用multi_v2、min覆盖/cap5及0.2多框补偿，奖励/数据/优化器/seed11451/8GPU不变。不加载step150、不恢复父Run、不覆盖任何旧产物。复用configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_multi_bonus_grpo.py及tools/run.sh，output.run_name为新RunID。保持3epoch/1500更新配置，但在本Run保存step_000400后由Steward自动核验、暂停并释放GPU，然后使用独立子Run评测该checkpoint；评测后不自动恢复训练，不把暂停视为1500完成。每更新全局128rollouts；至400约51200rollouts，不是等生成量对照。评分诊断复用既有rollouts reward.scores/candidate_ious/ranking_pairs/ranking_loss/calibration_penalty/distractor_penalty及advantage，在同rank/update/sample_id采样组内统计，多框与original正负/collage分层；不引入score CE或偏好损失。此次明确授权新训练受管执行及必要指定已发布SHA部署，不启动父Run排队命令。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：seed11451；每50步存档/组统计。评分诊断读取既有reward.scores/candidate_ious/ranking_pairs/ranking_loss/calibration_penalty/distractor_penalty和advantage；同rank/update/sample_id分组、每50完成更新及original正负/collage分层。无score CE/偏好损失。Steward约400暂停、核验8GPU释放后自动评测。未测试。
- 命令：bash tools/run.sh configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_multi_bonus_grpo.py settings.trainer.group_size=8 output.run_name=e014-multi-bonus02-g8-sft659-seed11451
- 代码版本：f780dff120669af666007d2ab04292873e654e88
- 随机种子：11451
- 配置：configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_multi_bonus_grpo.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/metrics.json

## 结果
用户主动停训：8rank最终154；最新checkpoint150。step150独立评测r2已exit0/managed complete，Selected mIoU=.7024264856（1766样本）。训练1..150日志19200rollouts/2400G8组核验完整；multi总率34.22→46.80→44.22%，collage54.82→87.13→89.89%，原始正负输入下降。

### 分析
复用原日志逐组核对2400group及24已完成窗口；只取rollout.step0..149，排除151..154共512条。全程mixed462组/4818对；主指标组等权严格胜率q=.473704，ties=.089341，pooled=.475509，mean multi-single差+.052170；original正/负/collage分层q=.274555/.136618/.689450。multi正adv4694/8015。全分母及窗口/score奖励诊断见shell/06_experiments/E-014/visualizations/g8-step150-20261014/report.md和training_audit.json。不同条件差异明显，不支持统一整体探索坍缩说法；不作因果或Claim升级。训练仍暂停，不声称1500完成或自动恢复。

### Claim 边界
主诊断高且multi率下降支持Exploration瓶颈假设，但不能单独确定主要原因或排除Reward Design。该Run不自动validated Claim，不输出因果结论；工程complete不等于收益。

### 过程记录
2026-10-14 08:18用户要求立即停止转评测，取消等待400。先managed fail authorization/retryable=false，再SIGTERM唯一coordinator及9个已验证worker进程。8rank最终完成154；最新保存step150。所有目标PID消失，nvidia-smi compute-apps为空，8卡各2MiB/0%。退出码254为用户停止，不是1500预算完成。step150 optimizer.steps=150；policy/config/optimizer非symlink、非空且读期间stat稳定；权重SHA256=2b1b5343ce77087401fb3bdf2be1dccce5cead814d94f0b006f350c4ab214936。151..154未保存不用于step150评测。全部产物保留，不自动恢复。新评测e014-multi-bonus02-g8-step150-eval1766；原step400队列已暂停。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
