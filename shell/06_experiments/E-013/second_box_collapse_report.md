# E-013 第二框坍缩：只读离线诊断

日期：2026-09-29。本文是探索性结果记录，不修改 Experiment、Run、Claim 或审批状态，也不构成已验证 Claim。

## 证据范围与口径

- 用户显式允许的远端 `experiments/E-013`；主训练分支 ID：`20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep`，读取其 `grpo/rollouts-rank{0,1}.jsonl`，共 7,520 条，step 0–469。
- 与主分支有明确 `parent_run_id` 及 step 450 checkpoint 血缘的现有评测分支 ID：`20260929T055808Z--multi3-rank-cf-latest-eval`，读取 `evaluation/predictions.jsonl`，共 1,766 条。step 50 评测分支 `20260929T115407Z--multi3-rank-cf-step50-eval` 当时尚无预测文件，未使用。
- 分析只纳入目标存在、有效三框、分数与 IoU 合法、IoU 唯一最优、选择索引与分数重算一致的记录。训练 rollout 纳入 3,553 条，其中第二框唯一最优 232 条；固定评测纳入 1,539 条，其中第二框唯一最优 117 条。具体排除计数见 [聚合数据](second_box_collapse_summary.json)。分数并列按原有选择规则落到较早的框。
- 本任务没有预先给出 Solid Run ID；以上两个 ID 均为本轮用户显式允许的 E-013 对象，不外推为 Solid 结果。
- 输入 SHA-256：`rollouts-rank0.jsonl` 为 `c8cf803ff3f217db85c5f10d483b944e6c9c15d7e99a9cbed66c5042ae49cbf0`，`rollouts-rank1.jsonl` 为 `f2ff894b9fca07ed02536f21d20f719730971f88f55032aa0571dce6296b0fc5`，`predictions.jsonl` 为 `2e2e37705fa02c5a6a33ec2f0792271e6e128269f9c8cb2187608759466444d9`。

## 1. 第二框选择概率随 step 变化

[训练趋势图](second_box_collapse_diagnostics/training_curve.svg) 同时画每 step 原始比例与相邻 25 step 合并比例。合并后，step 0–124 为 **16/86 = 18.6%**，125–299 为 **3/82 = 3.7%**，300–469 为 **6/64 = 9.4%**。后段有回升，且很多单 step 分母很小，因此这些训练 rollout **不足以确定精确坍缩起点**。逐 step 曲线是不断变化的训练样本及生成候选框上的描述，不是固定验证集时间曲线。

现有 step 450 固定评测中，第二框唯一最优时选中第二框 **2/117 = 1.7%**，Wilson 95% 区间约 **0.5%–6.0%**；另有 **115/117** 选中第一框。此处只有一个已完成 checkpoint，无法用它验证用户所说的“12% 到 2%”的同集变化。没有为本分析启动新的评测。

## 2. 分数差与 IoU 差

[分数差与 IoU 分桶图](second_box_collapse_diagnostics/score_margin_and_iou_gap.svg) 使用 `Δs=s₂−s₁` 和 `ΔIoU=IoU₂−IoU₁`。训练中第二框唯一最优的 232 条里，`s₂>s₁` 为 **31 条**，`s₁>s₂` 为 **96 条**，分数相等为 **105 条**。即使 `ΔIoU≥0.4`，正确的两框排序也只有 **21/135 = 15.6%**，没有看到优势越明显、排序越可靠的趋势。

step 450 固定评测的 117 条第二框唯一最优样本中，`Δs` 均值为 **−0.224**、中位数为 **0**；**71/117** 出现第一、第二框分数相等并触发靠前框的选择规则。分数并列和负的分数差都与强烈的首框偏向一致，但这仍是行为描述。

## 3. 训练 reward 与 advantage

[reward 与 advantage 图](second_box_collapse_diagnostics/reward_advantage.svg) 比较训练中第二框唯一最优且分数不相等的 rollout：

| 条件 | 条数 | 平均总 reward | 平均 advantage | 平均 IoU 项 | 平均 ranking_loss |
| --- | ---: | ---: | ---: | ---: | ---: |
| `s₂>s₁` | 31 | 0.472 | 0.388 | 0.620 | 0.043 |
| `s₁>s₂` | 96 | −0.294 | −0.673 | 0.170 | 0.243 |

同一 step、同一 `sample_id` 内同时含两种排序的只有 **8/152 组**。这 8 组的“正确排序减错误排序”平均总 reward 差为 **+0.605**、advantage 差为 **+1.114**；按组重采样的探索性 95% 区间分别为 **[+0.209,+0.986]** 和 **[+0.140,+1.907]**。`brier`、重复框惩罚等各项均值及可用记录数在聚合数据中；`coverage` 在该条件子集没有可比较数值。

## 判读与限制

现有 rollout **有正向的总 reward 和 advantage 关联**，所以“正确排序完全没有学习信号”的简单解释不符合这些记录。与此同时，正确排序样本的候选框 IoU 也明显更高；只有 8 个可作同题组内比较的组，因此无法把总 reward 的差别归因于排序本身，也不能证明正向信号有效到达 score token 的更新。当前更稳妥的下一步是针对已记录的分数并列、首框选择及 score token 梯度做聚焦检查，再决定是否修改 reward 或优化设置。

固定评测只有 step 450；step 50 的已有评测尚未产出预测文件。训练曲线样本与候选框随 step 变化，不能代替固定集 checkpoint 曲线。本报告不主张精确坍缩起点，也不主张 KL、entropy 或 group diversity 已被排除。

复算脚本：[聚合](analyze_second_box_collapse.py)、[绘图](plot_second_box_collapse.py)。运行时仅对远端已授权文件做只读扫描，聚合 JSON 与 SVG 保存在本地 E-013 目录。
