# 旧五头（E-009 R-003）与新五头（E-012 R-006）选头算法对照

日期：2026-09-15。只读复核既有实现与归档产物；未启动实验、未修改治理状态。

## 0. 两套 head 集合的出处

| | 旧五头（student_heads） | 新五头（R-006 E_null_calibrated） |
|---|---|---|
| heads | L21H10, L17H04, L17H07, L24H16, L18H15 | L24H13, L23H30, L26H20, L21H11, L23H13 |
| 出处 | `configs/sft/qwen3vl_8b_reference_query_alignment.py` 的 `runtime.runner.auxiliary_loss.student_heads`（历史字节 sha256 `0be113ae…`） | `experiments/E-012/R-006-redetermine-reference-heads/attempt-001/frozen_heads.json` 的 `E_null_calibrated`（sha256 `0a87d700…`） |
| 配对 teacher 头 | L20H20, L20H15, L14H23（同配置 `teacher_heads`） | L17H24, L17H27, L21H17（R-005 `E_null_calibrated` top-3） |
| 生成算法 | E-009 R-007 头稳定性筛查（`r003-t003/v1`） | E-012 R-006 dual-role 筛查（`e012.reference-target-screening/v2`） |
| 实现 | `iploc_szy/head_screening/finders.py::_r003_select`；`metrics.py::{component_token_entropy, chord_threshold, support50_fiou}` | `iploc_szy/head_screening/reference_target_screening.py::aggregate_reference_screening`；`reference_target_collector.py` |

旧 `student_heads` 与 R-007 稳定性筛查中 **step1646** 的 query top-5 完全一致（`L21H10, L17H04, L24H16, L17H07, L18H15`）；step1729 的 query top-5 只差一个头（含 `L20H15` 而缺 `L17H07`）。配对的 teacher top-3 在 step1646 与 step1729 相同。归档里没有写明最终取哪个 checkpoint，因此"来自 step1646"是由集合完全相同推断的，不是文档直述。

## 1. 旧算法：R-003（query 角色，不用 GT）

输入：每个样本在 teacher-forced bbox 预测行 `p−1` 上、对 **query 图像 token** 的注意力图 `q_to_q`，重排成 `[layer, head, H, W]` 网格；96 条样本。

1. **质量**：`sum(l,h,n) = Σ_grid q_to_q`，样本均值 `mean_sums`。
   门槛 `threshold = chord_threshold(mean_sums)`：把 `mean_sums` 升序排列画成曲线，取"到首尾连线距离最大"的拐点值（max-distance-to-chord elbow），即只保留注意力质量明显更大的一批 head。
2. **资格**：`mean_sums ≥ threshold` 且 `layer ∉ {0,1}`（排除前两层）。
3. **集中度**：对每个 head 的网格，先做二值化 `mask = map > 1.0 × mean(map)`，用 8 连通域标记，得到各连通块 token 数 `sizes`，`entropy = −Σ p log p`（`p = sizes/Σsizes`）。熵越低＝注意力越集中在少数连通块。
4. **逐样本投票**：在每个样本内，把资格 head 按熵**升序**排序，取前 `per_sample=10` 个，各自 `selection_frequency += 1`（并列按 head 索引）。
5. **排名与冻结**：按 `selection_frequency` 降序（并列按索引）排序，取前 3 / 前 5。query 角色的固定 5 头即由此产生。

要点：**全程只用注意力图本身的几何统计（质量 + 连通块熵），不含损失、不含梯度；query 角色完全不使用 GT；阈值是手工/启发式的（质量用 elbow，熵无阈值）。**

## 2. 旧算法：T-003（reference 角色，用 GT）

输入：对 **reference 图像 token** 的注意力图 `q_to_r` + 网格化的 GT 占有率 `reference_target`。

1. `normalized_entropy = component_token_entropy(map, 1.0) / log(H×W)`（同上熵，再按网格 token 数归一化）。
2. `support50_fiou = IoU(retained_mass_support(map, 0.5), GT_occupancy)`：把该 head 注意力按质量从大到小保留到 50% 的那块支撑区域，与 GT 分数占有率做 IoU。
3. `reward = −1.0 × normalized_entropy + 2.0 × max(0, support50_fiou − 0.1)`（**熵权重 1、IoU 权重 2、IoU 阈值 0.1 都是人工设定**）。
4. 每个样本按 reward 降序统计 `top1_frequency` / `top10_frequency`，并累加 mean reward / IoU / 熵。
5. 排名 = `top1_frequency` 降序 → `top10_frequency` 降序 → mean reward 降序；取前 3 冻结（要求至少 5 个不同的 per-sample top-1 head，否则报错）。
   step1646/step1729 的 reference top-3 = `L20H20, L20H15, L14H23`，即旧配置的 `teacher_heads`。

要点：**只用"注意力支撑区域与 GT 的重合 + 集中度"，仍然没有用到 loss 或梯度。**

## 3. 新算法：E-012 R-006 dual-role 筛查（target_role=query）

输入：E-009 step247 checkpoint；`test_combined_lasot600_gotval_taoval_1shot_focus.json` 的 590 条，按 component/图像隔离切成 **discovery 354 / calibration 118 / confirmation 118**；全部 36×32=1152 heads；teacher-forced bbox **坐标 token** 的预测行 `p−1`。

对每个样本 `n`、head `(l,h)`（`L_coord` = 四个坐标字段 token 的平均 CE）：

1. **一阶视觉贡献**（对 query 视觉 key 边求和，先取绝对值）：
   `C(n,l,h) = Σ_{p∈P̄_n} Σ_{j∈query keys} | A[p−1,j] · ∂L_coord/∂A[p−1,j] |`；汇总为样本等权均值 `RoleVisualAbsContrib`。
   同一套代码还会算出链式等价量并做 FP32 一致性门禁。
2. **目标偏好** `T_A`（注意力）与 `T_D`（贡献）：把该角色（本例为 query 图像）视觉 token 上的权重向量先归一化成 `distribution = values / Σvalues`，与 GT 分数占有率 `g`（每个 token 被 GT 覆盖的比例）做内积得目标质量 `m = Σ_j distribution_j · g_j`，再
   `T_raw = (m − mean(g)) / (max(g) − mean(g))`，`T = clip(T_raw, 0, 1)`；
   当权重全零或 `max(g) == mean(g)`（GT 在网格上无空间区分度）时记为 invalid，不补 epsilon。
3. **Calibration（118 条，看模型输出前冻结）**：三种空间 null（`same_size_shifted`、`radial_matched`、`fixed_center`）生成 pooled null 分布；
   `τ_C = quantile(C_calibration, 0.90)`，`τ_A = quantile(null T_A, 0.95)`，`τ_D = quantile(null T_D, 0.95)`。
4. **资格频率**：在 discovery 的 354 条里，要求
   `valid(n,l,h) & C ≥ τ_C & T_A ≥ τ_A & T_D ≥ τ_D`
   的样本比例 `≥ qualification_frequency_min = 0.5`，才进入候选池。
5. **排名分数**：`score(l,h) = mean_n[ (C(n,l,h)/max_h C(n,h)) · sqrt(T_A(n,l,h)·T_D(n,l,h)) ]`，降序取 `top_k = 5`；**允许少于 5，甚至零候选**。
6. **Confirmation（118 条）**：只对冻结集合做按 component 聚类的 bootstrap（seed 20260914，1000 次）报区间，不重新排序、不改变入选门槛。

R-006 实际冻结：L24H13(0.3160)、L23H30(0.1816)、L26H20(0.1621)、L21H11(0.1533)、L23H13(0.1367)；Discovery 达标率 89.8%/95.5%/89.0%/96.3%/94.4%。

要点：**用 loss 对注意力边的一阶敏感度（绝对贡献）+ GT 目标偏好；阈值全部由 null 校准给出；有独立 split 与达标频率约束；还能给出"零候选"。**

## 4. 关键差异一览

| 维度 | 旧（R-003 / T-003） | 新（R-006） |
|---|---|---|
| 信号 | 注意力图几何：图像注意力质量 + 8 连通块熵 | 损失梯度 `|A·∂L/∂A|` + GT 占有率加权的目标偏好 |
| 是否用 loss | 否 | 是（teacher-forced bbox 坐标 CE） |
| 是否用 GT | query 角色不用；reference 角色用支撑区 IoU | 两个 T 指标都用 fractional occupancy |
| 阈值来源 | elbow（质量）、人工设 1/2/0.1（reward） | null 分位：τ_C 90%、τ_A/τ_D 95% |
| 排名方式 | 每样本按熵取 top-10 → 计数频率 → 取前 5 | 每样本归一化 C × sqrt(T_A·T_D) 的样本均值 → 取前 5 |
| 稳健性约束 | 无频率门槛，只有"≥5 个 unique top-1" | 必须在 ≥50% discovery 样本同时过三阈值 |
| 数据 | 96 条训练内样本，单 split | 590 条，discovery/calibration/confirmation 三分且 component 隔离 |
| 冻结方式 | 训练前一次冻结（`periodic_head_screening=False`），不随训练更新 | 单次冻结，confirmation 仅验证 |
| 允许零候选 | 否 | 是（0~5） |
| 层排除 | 排除 L0、L1 | 无 |

## 5. 与消融结果的对应

- 旧五头在 E-009 step741 上联合置零：mIoU 0.6695 → 0.5051（配对 ΔIoU −0.1644，−24.6%），TAO −29.5 pp。
- 新五头在同一 checkpoint 上：0.6678 → 0.6268（−0.0409，−6.1%），与同层随机 5 头不可区分。
- 因此"选头算法是否指向承重 head"这件事本身就是两套算法差异的直接体现：旧算法（注意力质量 + 集中度）选中的是注意力大量压在图上的早中层 head，联合移除即崩；新算法（梯度敏感度 + 目标偏好 + null 校正）选中的是 21–26 层 head，联合移除代价很小。

## 6. 边界

- 旧 head 集合的最终冻结 checkpoint 未在归档中明确写出，本文的"step1646"是集合完全一致推断出的，非文档直述。
- 两套算法使用不同模型与数据（旧：E-009 step1646/1729、96 条训练内样本；新：E-009 step247、590 条 test_combined），选头分数之间不可直接比较数值大小。
- 两套都只是"候选 head 的发现"，都不是因果必要性证明；因果结论只能来自对应模型上的干预实验。
