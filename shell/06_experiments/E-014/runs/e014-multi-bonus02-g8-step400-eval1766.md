# e014-multi-bonus02-g8-step400-eval1766 · 用户追加要求新G=8训练约400step时自动评测400step。此独立评测仅在父训练保存payload/grpo/checkpoints/step_00040

- 父 Run：`e014-multi-bonus02-g8-sft659-seed11451`
- 来源版本：2026-10-14T00:45:31.610736
- 状态：ready_to_run
- Workspace：03

## 本次任务
用户追加要求新G=8训练约400step时自动评测400step。此独立评测仅在父训练保存payload/grpo/checkpoints/step_000400并暂停释放GPU后启动。只读核验optimizer.steps=400、训练group_size=8、multi_v2、multi_bonus_weight=0.2、prompt和checkpoint来源SHA。沿用本轮1766测试清单、8GPU、greedy192/vision4096，评测seed20260901；只派生image_path至只读alias，不改GT/身份/split。输出本Run独占payload，日志根managed_console.log。报告raw候选数、First/Selected/Oracle mIoU及gap、选非首框率、多框条件下同分/排序/顺序/重复、IoU阈值命中；Oracle仅事后诊断，不能替代真实score选择。训练评分诊断只读父Run已完成更新1..400日志，按同rank/update/sample_id分组及original正/负和collage分层，不增加模型推理或改变奖励。本请求授权Steward在上述前置条件通过后单次受管自动评测，不重跑、不恢复父训练、不自动提升Claim。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：必须等待step400存在、optimizer.steps400、来源snapshot.group_size8/bonus.2/multi_v2正确、父训练暂停且8GPU空闲。独占payload，日志managed_console.log。配置与入口已部署，未提前评测；未测试。
- 命令：E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step400-eval1766 E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000400 E014_EVAL_CONFIG=configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step400_eval1766.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=400 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh
- 代码版本：f780dff120669af666007d2ab04292873e654e88
- 随机种子：11451
- 配置：configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step400_eval1766.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step400-eval1766/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step400-eval1766/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step400-eval1766/metrics.json

## 结果
尚无结果。

### 局限
单seed、已看测试集；G8与G4同更新数非等生成预算；不自动validated Claim或恢复训练。

### Claim 边界
主诊断高且multi率下降支持Exploration瓶颈假设，但不能单独确定主要原因或排除Reward Design。该Run不自动validated Claim，不输出因果结论；工程complete不等于收益。

### 过程记录
2026-10-14用户取消等待step400，训练已主动停止154，最新完整checkpoint150。此step400评测未运行，原自动队列已暂停，不执行本命令。改为独立step150评测，但该新Run前置布局检查失败；待用户决定重试。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
