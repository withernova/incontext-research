# e014-multi-bonus02-g8-step150-eval1766 · 用户要求现在停止G8训练并开始评测，不再等400。训练已按授权停止，8rank实际完成154更新；最新完整保存checkpoint为本父Run payload/

- 父 Run：`e014-multi-bonus02-g8-sft659-seed11451`
- 来源版本：2026-10-14T08:17:48
- 状态：failed
- Workspace：03

## 本次任务
用户要求现在停止G8训练并开始评测，不再等400。训练已按授权停止，8rank实际完成154更新；最新完整保存checkpoint为本父Run payload/grpo/checkpoints/step_000150，optimizer.steps=150。独立评测该G8 step150 checkpoint，原1766样本/8GPU/multi_v2/greedy192/vision4096/evaluation.seed20260901。复用现有explicit_binding评测shell与worker，仅薄配置绑定来源和独占输出；不改奖励/训练/数据/指标、不恢复训练、不覆盖旧结果。不运行step400 Run。报告First/Selected/Oracle、候选数与评分诊断，训练诊断限完成更新1..150；151..154不用于本checkpoint评测。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：review29212c4e326a1824通过；已部署84f1f13427ef527f8bc0d6f8e4dadebd34db0c05。导航/AST/diff静态检查通过，未跑suite/build/import/smoke。父训练已停154更新，optimizer.steps=150已核验，8GPU已释放。首次部署fetch失败，远端HEAD未变/clean；再次指定同SHA部署成功，评测尚未启动/未重试。
- 命令：E014_EVAL_PROFILE=explicit_binding E014_EVAL_RUN=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766 E014_EVAL_CHECKPOINT=/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-sft659-seed11451/payload/grpo/checkpoints/step_000150 E014_EVAL_CONFIG=configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step150_eval1766.py E014_EVAL_VARIANT=multi_v2 E014_EVAL_STEP=150 E014_EVAL_PROMPT_SHA=c6f28d607e7736bde33a82169e86fe517b5c13dccd4a04a0cb295da0e47336ba bash tools/run/eval/e014/e014_step800_eval1766_8gpu.sh
- 代码版本：84f1f13427ef527f8bc0d6f8e4dadebd34db0c05
- 随机种子：11451
- 配置：configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step150_eval1766.py
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766/managed_console.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766/payload/evaluation
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-bonus02-g8-step150-eval1766/metrics.json

## 结果
前置检查失败，exit1，没有模型加载、预测或评测结果。训练已按用户要求停止154，最新可评测checkpoint150。

### 局限
父训练实际154但只评测保存step150；151..154未保存，不进入该checkpoint训练诊断；取消step400等待。训练保持暂停。

### Claim 边界
单seed、已查看测试集，探索性诊断；不作因果结论或Claim升级。

### 过程记录
output_dir误登记Run/payload/evaluation，managed_execution.py:279会mkdir output_dir，故payload预先存在，触发run_symmetric_grpo.py:130独占布局拒绝。未来经用户授权的新尝试必须用根级outputs作为canonical output_dir、根级managed_console.log；实际worker输出仍payload/evaluation。现有失败产物全保留，不自动retry/新Run/覆盖。原step400队列暂停。

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
