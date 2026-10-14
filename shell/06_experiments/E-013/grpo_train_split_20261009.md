# GRPO train 子函数重构（2026-10-09）

## 完成内容

用户追加要求进一步拆分 `rl/trainer.py` 的 `train()`。已通过 Windows SSH 应用到 `SZY-3090:30827` 的授权代码仓库；本轮修改 trainer、训练入口测试、职责说明共 3 个文件。

`train()` 从 376 行缩短到 93 行，抽取 10 个有明确依赖的子函数：

| 子函数 | 职责 |
|---|---|
| `_initialize_policy` | 公共初始化 seed、模型/processor、rank 采样 seed、optimizer |
| `_plan_training_pairs` | 按 pair 分组、steps/epochs 配额与固定重排 |
| `_train_pair` | 逐条件训练编排 |
| `_collect_rollouts` | rollout、奖励、score 反事实与冻结 old-policy log-prob |
| `_replay_anchor` | 无梯度 anchor 重放、反事实参考分数及切回 policy |
| `_backward_and_log` | GRPO/偏好损失、DDP 同步边界、梯度缩放与逐样本日志 |
| `_write_config_snapshot` | 配置与显式 manifest 哈希快照 |
| `_report_step` | 更新后的汇总指标 |
| `_save_step_checkpoint` | 阶段保存和 rank 同步 |
| `_finish_training` | 全局反事实门禁、最终保存和分布式收尾 |

补上了默认奖励函数 `confidence_reward` 的缺失导入。此前的局部 helper 测试没有覆盖完整 `train()` 入口，这是本轮新增入口测试的直接原因。

## 检查结果

- 抽取语句块通过 AST 对比；显式输入 `pair_size` 替代原作用域的 `len(training_pair)`，未调整训练数学或更新顺序。
- 新增 CPU 合成完整训练测试：覆盖 steps 与 epochs 模式，调用真实默认奖励解析，验证 optimizer 确实更新、逐样本日志、anchor 在 policy 梯度前重放、阶段与最终保存。
- 拆分前后合成训练对比：逐样本日志、optimizer 状态、随机数状态和完成记录完全一致。对比基线仅补相同的奖励函数导入。
- 最终全库检查：**528 passed, 1 deselected, 4 warnings**。未执行的 1 项需要真实 processor 资产。独立快照的最终测试命令显式设置包搜索路径，使直接脚本子进程能够导入仓库包。
- 应用前后逐文件 SHA-256 核验通过；实际仓库 `git diff --check` 和旧训练 helper/主入口导入检查通过。

## 剩余风险

未执行真实模型、NF4 或多卡 GPU 训练；合成入口测试不能替代实际分布式训练验证。现有环境提示和 checkpoint/精确恢复能力边界沿用上一轮报告。

未读取历史 Run 产物、启动实验、提交或推送代码，未修改 Survey Tool 审批、Claim、Run 授权或治理状态。Solid Run ID：无。本报告仅提供工程检查证据。

补丁与文件哈希见同目录 `grpo_train_split_20261009.patch`、`grpo_train_split_20261009_hashes.json`。
