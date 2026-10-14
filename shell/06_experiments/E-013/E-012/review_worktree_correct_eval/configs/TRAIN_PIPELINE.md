# FOCUS 早期 GT-mask 训练配置

主配置：`configs/sft/qwen3vl_8b_focus_gt_mask_pipeline.py`。
继承现有 FOCUS 1-shot NF4 四卡配置，保持原 prompt、SFT 交叉熵、优化器和有效 batch 64。
使用已有有效的 train-only manifest；原始模型从 `model.model_path` 加载。

| 已完成的 optimizer updates | 下一次更新的行为 | Head 更新 |
| --- | --- | --- |
| 0–82 | 仅 SFT CE | 无 |
| 83–493 | GT-mask 权重在 83 次更新内从 0 渐增至 0.02 | 当前模型 Query Top-3，每 83 步重筛 |
| 494–1481 | 权重在 83 次更新内从 0.02 渐增至 0.05 | 当前模型 Query Top-5，每 83 步重筛 |
| 1482 起 | 权重在 83 次更新内从 0.05 渐增至 0.1 | 进入阶段时重筛 Top-5，此后固定 |

这些时点和权重是待比较的初始设置，不是经实验验证的最优值。
例如 `start_step=83` 表示完成 83 次 optimizer 更新后筛选，GT-mask 首次作用于第 84 次更新。
同一 optimizer update 的所有 gradient accumulation microbatch 共用同一阶段/权重/heads。
重筛使用训练集中的固定 seeded 96 条样本；不使用此前验证集结果或未来 checkpoint 的 heads。
固定阶段只表示配置要求停止重筛，不意味着程序判定科学上已经收敛。

GT-mask 保持原有目标：Query heads 的 bbox p-1 rows 到 reference 图像的 attention，
对齐 reference GT box 的 token occupancy。总损失是
`CE + coefficient * (KL(target || student) + SmoothL1(span_mass) + SmoothL1(object_mass))`。
GT target 从当前 batch 几何直接计算，不再依赖离线 teacher 文件，亦不需要 Reference Top-3。
这不是遮挡输入像素，也不是给 Query 图 GT 框单独新增 bbox regression loss。

启动（会新建代码仓库的训练输出，不修改 Survey Tool 授权）：

```bash
bash tools/run/train/train_focus_gt_mask_pipeline.sh
```

可通过同一主配置直接覆盖阶段参数：

```bash
bash tools/run/train/train_focus_gt_mask_pipeline.sh \
  named_run.run_name=focus-gt-mask-earlier \
  runner.pipeline.stages.early.start_step=41 \
  runner.pipeline.stages.early.auxiliary_loss.coefficient=0.01 \
  runner.pipeline.stages.early.head_selection.refresh_steps=41
```

做相同训练参数的 CE-only 对照：`runner.pipeline=None`。
`pipeline.stages` 为有序映射，第一阶段必须从 0 开始；所有 start_step 严格递增。
每个阶段可配置 `auxiliary_loss=None`、可注册的辅助损失、`head_selection`、
`ramp_steps` 和 `ramp_from_coefficient`。需要固定指定 heads 时，省略 `head_selection`，
直接填写该阶段 `auxiliary_loss.student_heads`。

追溯：`logs/config_snapshots/train-*/` 保存主配置、所有继承配置、resolved JSON 和 prompt 示例；
`logs/pipeline_events.jsonl` 记录阶段、实际 heads 及筛选来源；
`pipeline/<stage>/step_<completed>/selection.json` 保存重筛结果；
`logs/train_steps.jsonl` 记录每步实际权重与阶段索引。
checkpoint 的 `trainer_state.pt` 保存阶段、heads 和上次重筛步数；resume 恢复该状态，
拒绝使用不一致的 pipeline 配置。新分支 `initialize_from` 只加载 adapter，并从第 0 步重新计时。
原 pipeline 未使用的历史 checkpoint 无阶段状态，不能伪装成该 pipeline 的精确 resume。

完整运行会包含多次 attention screening，耗时与显存须经四卡 smoke 验证。
