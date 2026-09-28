# 拼图正式三轮训练

用户于当前对话明确要求立即启动正式 3 epoch 训练。已启动独立分支，未恢复此前暂停的旧训练；未修改 Survey Tool 审批、Claim 或 Run 授权状态。

- 分支 ID：`20260926T153209Z--multi3-collage-coverage-grpo-lr8e5-3ep`
- 代码提交：`86d3005`
- 配置：`configs/grpo/e013_multi3_collage_coverage_branch.py`
- 初始化：原置信度 SFT 的 `samples_00042136_step_000659`，不是短试验的 step100。
- 四卡，学习率 `8e-5`，3 epoch，每个输入生成 4 个候选回答。
- 每轮：2000 组原始正负对 + 2000 组拼图 A/B 对，共 8000 条输入。每步四卡合计处理 4 组，因此每轮 1000 step，全程 3000 step。
- Prompt：`focus_multi3_instances_spatial_v2`，候选按 Query 中框中心从左到右输出。
- 奖励：沿用短试验的按最高置信度选框 IoU、全候选置信度校准、候选排序、重复框惩罚，以及拼图左右覆盖与错误实例高置信度惩罚。

## 远程产物

训练目录：`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260926T153209Z--multi3-collage-coverage-grpo-lr8e5-3ep`

日志：上述目录中的 `logs/grpo.log`。

运行时配置：上述目录中的 `grpo/config_snapshot.json`，已核验 `epochs=3`、`learning_rate=8e-5`、`steps` 未设置。

Checkpoint：上述目录中的 `grpo/checkpoints/step_XXXXXX/adapter/policy`。

按 100-step 短试验约 99 秒/step 的速度粗估，完整训练约需 3–4 天；这不是完成时间保证。

启动核验：四卡均已完成第 1 次更新，梯度范数均为 0.3242，未见启动错误；每卡已写出 8 条 rollout 记录。Checkpoint 保存间隔已核验为 50 step。

## 2026-09-28 中途评测

用户明确选择终止当前训练，以便立即评测。终止前日志已到 step1405；最近完整 checkpoint 为 step1400。四卡已释放，原定 3000 step 未完成，不能把这次分支写作三轮完成或精确续跑。

已从 step1400 创建只读适配器入口 `eval-checkpoints/step1400`，并启动全量 1766 样本评测分支 `20260928T061742Z--collage-full3ep-step1400-spatial-eval`。结果目录同上述训练目录的 `branches/` 同级；完成后产物包括 `evaluation/metrics.json`、`ap_report.json`、`confidence_error_gap.json`。
