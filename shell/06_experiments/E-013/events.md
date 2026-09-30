# E-013 事件日志

> 本文件只保留单行摘要；完整 details 保存在工具内部的 experiment-events.jsonl 中。
> 需要展开某条事件时运行：`python3 /home/zhengyuesong/Tools/survey-tool/surveyctl.py --project <proj> experiment event-detail <E-ID> <EVENT-ID>`。

- 2026-09-29T01:12:08 · run_organization · 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep: microtask · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-bb12a19178fd
- 2026-09-29T01:12:08 · run_created · Agent 创建 canonical Run 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · 三框分数反事实训练 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-a7ce37709459
- 2026-09-29T01:15:11 · run_update · 已核对SZY-3090仅有两张3090，将本Run启动配置和GRPO进程数校验改为双卡；配置解析及输入检查通过。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-826e49722b9f
- 2026-09-29T01:15:22 · run_update · 双卡配置已提交并同步；因执行门尚未开启，尚未启动训练。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-f08ebabd5918
- 2026-09-29T01:17:07 · execution_dispatch_enqueue · 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep outbox=queued · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-dd04e445f487
- 2026-09-29T01:17:07 · run_direct_steward · 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep: current snapshot sent directly to Steward · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-462b6996c177
- 2026-09-29T01:24:00 · discovery · SZY-3090 项目目录内已安装并验证 tmux；受控执行器已接入项目内路径和本机既有 SSH 配置。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-2ea9f67a63f1
- 2026-09-29T01:28:02 · run_execution_human_failed · 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep: human marked current execution attempt failed · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-b859c1f73789
- 2026-09-29T01:28:05 · execution_dispatch_enqueue · 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep outbox=queued · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-51d9d5c3b257
- 2026-09-29T01:28:05 · run_execution_restarted · 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep: failed attempt preserved; new authorization created · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-dd937a55e1ab
- 2026-09-29T01:31:10 · progress · 用户明确授权直接运行后，已在SZY-3090启动登记的双卡训练命令；模型权重加载完成，等待首个训练步骤。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-19676ab5b97f
- 2026-09-29T01:32:58 · progress · SZY-3090 双卡训练已完成首个优化步骤；两张卡各记录 step 1，rollout 文件已写入。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-ac83e677b23f
- 2026-09-29T13:53:02 · discovery · 当前训练最新完整 checkpoint 已超过 step 450；Run 内尚无独立验证结果。已准备双卡验证配置，尚未读取验证清单或启动推理。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-7c5391894c65
- 2026-09-29T13:53:15 · correction · 更正上一条事件：当前训练步数已超过 450，但最新完整保存的 checkpoint 仍是 step_000450。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-3521fd0cf457
- 2026-09-29T14:02:16 · run_organization · 20260929T055808Z--multi3-rank-cf-latest-eval: microtask · run=20260929T055808Z--multi3-rank-cf-latest-eval · detail=evt-2b9bb86881b9
- 2026-09-29T14:02:16 · run_created · Agent 创建 canonical Run 20260929T055808Z--multi3-rank-cf-latest-eval · 反事实三框模型验证 · run=20260929T055808Z--multi3-rank-cf-latest-eval · detail=evt-fde607416f92
- 2026-09-29T14:02:36 · progress · 已在 SZY-3090 启动验证等待任务；当前等待父训练结束和双卡空闲，随后自动选最新完整 checkpoint 做全量验证。 · run=20260929T055808Z--multi3-rank-cf-latest-eval · detail=evt-30445a47ffb8
- 2026-09-29T14:11:43 · run_update · 用户要求停止训练并直接推理；已使用完整 step_000450 权重的兼容引用启动双卡全量验证，两个进程均已完成前10条预测。 · run=20260929T055808Z--multi3-rank-cf-latest-eval · detail=evt-cef94a8082a0
- 2026-09-29T14:11:56 · progress · 按用户要求停止双卡 GRPO 训练；停止时日志到 step 470，最新完整 checkpoint 为 step_000450。 · run=20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · detail=evt-6ddbb4bd1b48
- 2026-09-29T14:11:56 · progress · 全量验证已从 step_000450 开始推理；两个 GPU 进程均已完成前 10 条预测。 · run=20260929T055808Z--multi3-rank-cf-latest-eval · detail=evt-d25b42fd80af
- 2026-09-29T17:10:48 · run_update · 全量验证已完成并核对结果；仅更新该Run的结果记录，不改Claim或审批状态。 · run=20260929T055808Z--multi3-rank-cf-latest-eval · detail=evt-392dfe07f0e8
