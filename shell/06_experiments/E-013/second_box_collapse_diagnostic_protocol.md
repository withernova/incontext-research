# E-013 第二框坍缩诊断协议

本文件只定义分析方法，不记录 Claim。用户已明确允许读取远端 `experiments/E-013` 下的现有实验，重点为 `20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep`。本次结果见 `second_box_collapse_report.md`。

## 共同口径

- 只纳入三候选框、目标存在、三个 score 与 IoU 均有限且在合法范围、输出有效的记录；逐项报告排除数量。
- 候选框按原始顺序编号 1、2、3。`k*=2` 指第二框 IoU 严格大于第一框和第三框；IoU 并列最优单列报告，不算入主分析。
- `\hat k` 按已登记的推理选择规则从 score 得出；分数并列、报告的 `selected_index` 与重算不一致、未正常结束的记录单列审计。
- 评测曲线使用同一批样本及相同提示、解码和候选框顺序；重复 `sample_id` 按样本聚类，不把 rollout 条数当独立样本量。

## 1. 第二框选择概率随 step 变化

对每个可用 checkpoint，计算 `P(\hat k=2 | k*=2)`，同时报告分子、分母及有效样本数。画逐 step 曲线和区间；以第一个持续下降且后续 checkpoint 未恢复的区间描述坍缩起点，不只凭两个端点断言起点。若各 step 的评测样本不同，先取共同样本交集，原始各自样本结果仅作附录。

## 2. 第二框分数差与 IoU 差

在 `k*=2` 子集定义 `\Delta s=s_2-s_1`、`\Delta IoU=IoU_2-IoU_1`。每个可用 step 画 `\Delta s` 分布与中位数，并按预先固定的 `\Delta IoU` 桶报告 `P(s_2>s_1)`、相等率和每桶数量；另报告 `P(\hat k=2)`。`s_2>s_1` 只是两框排序正确，第三框可能仍有最高分，不能等同选中第二框。

## 3. 训练 rollout 的学习信号

限于训练中 `k*=2` 的有效三框 rollout，比较 `s_2>s_1` 与 `s_1>s_2` 两组的总 reward、每个实际记录的 reward component、以及训练使用的 group-normalized advantage。分数相等单列。优先在同一 prompt/group 中同时存在两种排序时计算组内差，再汇总各组差值、组数和不确定区间；同时报告两组原始均值，防止题目难度混淆。若只有聚合 reward 而无逐 rollout component 或 advantage，就明确标记相应比较不可识别，不能从聚合量反推。

## 判读边界

- 正确排序 rollout 没有稳定的正向 reward/advantage 差值：优先审查 reward 及组内归一化是否提供可用信号。
- 正确排序有稳定的正向信号，而固定评测集的第二框选择率仍随 step 下降：再检查 KL、entropy、group diversity 和对应 token 的优化贡献。
- 这些是诊断分支，不是因果结论；rollout 的排序是模型行为，条件均值本身不能证明 reward 修改或优化过程的因果作用。
