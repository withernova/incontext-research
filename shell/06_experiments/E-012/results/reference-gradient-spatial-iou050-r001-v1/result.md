# E-012：reference 选头加入 IoU ≥ 0.5 的结果

产物 ID：`reference-gradient-spatial-iou050-r001-v1`。用户在启动前要求 IoU ≥ 0.5；计算与核验均已完成。

## 主要结果

- 同一 step1973 checkpoint、690条原 reference 样本和原逐样本梯度 Top-50；新规则最多选10个，允许零入选。
- 累计入选 1421 次；378/690 条零入选（54.8%），53条选满10个。
- 入选项的最大注意力质量连通域 IoU：均值 0.577861、最低 0.500032。
- 旧规则入选项在同一最大质量分量指标下均值 0.343161；两种均值来自不同筛选总体，不能解释为独立性能提升。
- 与原 reference Top-10 重合4个：L17H04, L17H07, L17H24, L17H27；Jaccard=0.25。

| 排名 | Head | 入选次数 / 690 | 频率 |
|---:|---|---:|---:|
| 1 | L17H07 | 122 | 17.68% |
| 2 | L21H17 | 120 | 17.39% |
| 3 | L17H06 | 81 | 11.74% |
| 4 | L17H24 | 80 | 11.59% |
| 5 | L18H12 | 80 | 11.59% |
| 6 | L17H04 | 79 | 11.45% |
| 7 | L18H14 | 77 | 11.16% |
| 8 | L21H31 | 76 | 11.01% |
| 9 | L17H25 | 66 | 9.57% |
| 10 | L17H27 | 64 | 9.28% |

## 分数据集覆盖

| 数据集 | 样本数 | 零入选 | 选满10个 |
|---|---:|---:|---:|
| LaSOT | 300 | 144 | 35 |
| GOT10k | 90 | 42 | 6 |
| TAO | 300 | 192 | 12 |

## 检查与解释边界

- 本地和服务器的9项聚焦测试均通过；首样本捕获前后bbox logits一致；全部690条使用旧规则重算的入选集合与原run逐条相同。
- 全部入选项 IoU≥0.5，梯度候选与原记录逐项一致，频率矩阵、样本分母和计数一致。本地8个摘要/记录/频率图文件的SHA-256与服务器一致。
- 155/690条样本在当前token网格上，即使选择最优任意二值token掩码，分数IoU也达不到0.5；这只是忽略连通性和attention约束的理论上界。它们必然零入选，应归因于当前网格/门槛的几何限制，不能自动归因于head错位。
- 固定GOT10k样本600的旧head L20H18有约91.9%的reference attention质量落在GT内，但主要连通域IoU为0.281，因此被新门槛排除。门槛更偏向覆盖整框，会丢弃一些关注目标局部的head。
- 约束保证的是每次计入frequency的样本达标；并不保证最终固定Top-10在所有图上都达标。总体第一名也仅在122/690条样本入选。
- 本轮同时改变了分量规则、IoU门槛、排序和不补满策略，结论限于这套规则的整体变化。使用同一发现集，未作独立留出或因果消融。
- 原始bbox梯度方向未通过有限差分校验的限制仍在，本轮只复用绝对贡献候选，不作增强或抑制方向解释。

## 文件

- [完整比较与核验](comparison.json)、[原始摘要](summary.json)、[逐样本记录](records.json)、[参数与来源](resolved_plan.json)。
- [总体frequency图](frequency_all.png)、[LaSOT](frequency_LaSOT.png)、[GOT10k](frequency_GOT10k.png)、[TAO](frequency_TAO.png)。
- [LaSOT固定样本0](visualizations/sample_000000_LaSOT_old_vs_iou050.png)、[GOT10k固定样本600](visualizations/sample_000600_GOT10k_old_vs_iou050.png)、[TAO固定样本780](visualizations/sample_000780_TAO_old_vs_iou050.png)。另保存每个数据集第二条固定样本。
- 服务器产物：`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/reference-gradient-spatial-iou050-r001-v1`。全部690条候选attention缓存保存在其 `attention_maps/` 下。
- 原 reference 来源 ID：`reference-gradient-gated-spatial-frequency-r001-v1`；本轮没有使用新的 Solid 结果，也没有更新审批、Claim 或执行授权状态。
