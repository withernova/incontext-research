# E-005 · Attention-derived localization-head discovery and grounding audit

- status: implementing
- kind: attention_mechanism_analysis
- source_ref: localizationheads2025
- claim_refs: 
- priority: medium
- created: 2026-07-24T13:42:03
- updated: 2026-07-24T13:52:20

## 实验目标
首先审计 LocalizationHeads 当前公开仓库的 repo-original 方法在冻结 Qwen3-VL/IPLoc-ID 上是否真的找到**对 GT 有空间选择性**的注意力头；只有通过这一 head-quality gate，才使用这些头分析图像 tokens 与 prompt 其他区域之间的注意力分配、正负样本差异，并与 E-004 候选层比较。

## 假设
1. repo-original 方法若能迁移到本任务，其冻结 heads 对 GT 的 attention density 应高于面积均匀基线，也应优于同 prompt 的未选择 heads。
2. 只有定位选择性通过后，相关 heads 上的 image-token/prompt attention budget 才具有可解释性。
3. 即使 attention head 通过定位门禁，attention 仍不是因果贡献；因果结论属于 E-004 CMA/MF。

## 成功标准
- 冻结 heads 的 median GT enrichment > 1；
- 冻结 heads 在全部 36×32 heads 中的 median GT-enrichment percentile ≥ 0.75；
- 冻结 heads 的 GT pointing rate 高于同 prompt all-head control；
- 固定索引、非结果挑选的 heatmaps 经人工审核确实在 GT 附近形成高注意力区域；
- 通过后才启动 multi-query attention-budget audit。

## 失败/证伪标准
- 上述 GT concentration 三项门禁任一失败；或可视化显示高注意力系统性偏离 GT；
- 失败时不得使用这些 heads 推断“模型如何利用图像 token”，应先修正 query 位置或 selection 方法，并把新变体独立命名。

## 实验安排
1. 工程与真实 eager-attention 门禁；
2. repo-original discovery 冻结候选 heads；
3. **直接 GT concentration + all-head matched control + 固定样本 heatmap 审核**；
4. 仅当第 3 步通过，才进行 image-token vs prompt-region attention-budget、positive/negative selectivity；
5. 可视化按“一次推理一张图”组织：同一 inference 的 `reference | query` 左右并列，相同 head 按行对齐；若该 inference 实际包含 negative，则用 `reference | positive query | negative query` 三列。不得为了展示从其他样本补入 negative。顶部展示 clean images + GT，随后展示各冻结 head 与 combined map；turbo 蓝低红高、GT 绿色，panel 内 min-max 仅供空间解释。
5. attention 候选与 E-004 CMA/MF 只做重叠诊断，不混称因果。

## 变量与对照
（待补充）

## 最小测试
（待补充）

## Baseline
（待补充）

## 处理组与消融
（待补充）

## 指标与混淆变量
（待补充）

（待补充）

## 风险与开放问题
（待补充）

（待补充）

## 资源预算
（待补充）

## 自由笔记（Obsidian）
这里可补充研究设计推演；工作台更新结构化方案时不会覆盖本节。

## 已确认的实现口径（2026-07-24）

- 主协议采用官方公开仓库 `seilk/LocalizationHeads@9ffe219d20ec376eb4dd14d42c54bb3299ffdb4a` 的 **repo-original behavior**。
- 上游快照 `codespace/LocalizationHeads/` 保持零修改；源码完整性清单为 `codespace/LocalizationHeads_upstream_sha256.txt`。
- 不把论文公式与当前代码之间的差异静默修正为另一套实现。主设置保留：
  - `top_k=5`；
  - chord threshold；
  - `ReLU(A - 2*mean(A))`；
  - component attention-mass spatial entropy；
  - bottom-row focus filter；
  - 排除layer 0/1；
  - Gaussian `sigma=1.0`；
  - 当前公开代码的mask/bbox逻辑。
- Qwen3-VL仅做必要适配：双图visual-token spans、动态merged `H×W` grid、最后输入token到指定图像span的`[L,H,1,V]`attention导出。
- raw attention只构成attention-derived localization诊断，不构成CMA、因果中介或必要性证据。

## 分阶段安排

1. **R-000 工程门禁**：square-grid结果与官方`analyze.py`完全一致；矩形grid、双图span、collector contract和错误输入hard-failure测试。
2. **R-001 基础设施恢复**：若服务器重启导致Qwen snapshot缺失，恢复到server-local HF cache并做完整性检查。
3. **R-002 单样本真实attention smoke**：加载Qwen3-VL/IPLoc-ID，验证eager attention是否可在24GB显存下返回；审计reference/query span、grid、shape与finite值。
4. **R-003 小规模collection pilot**：仅在R-002通过后运行，检查跨样本head selection frequency与attention图可解释性。
5. **正式discovery/evaluation split**：规模和trial数在pilot后固定；不得用pilot同一批数据选择并验证heads。
6. **R-010 head-quality gate（已执行）**：冻结 R-005 top-5，在 40 个 positive queries 上直接测 GT soft mass/enrichment、pointing、all-head percentile，并输出前 10 个固定索引的 heatmaps。结果 3/3 quality gates 失败：median enrichment=0.107、median all-head percentile=0.092、pointing=0/200。因此当前 `last-input-token + repo-original selection` 不得进入主 attention-budget 解释阶段。
7. **下一修正阶段**：在不触碰正式结论边界的前提下，分别审计 candidate/decision/teacher-forced output query positions，或 query-image→reference-image cross-attention；每个变体单独命名并先重复 GT-quality gate。不得通过在同一评估集上搜索 query/head 后再称 held-out 验证。
8. **R-018 原始顺序 cross-image reference retrieval（已完成）**：使用 `query-object visual rows → reference visual keys` 发现并审核 reference-region retrieval candidates。有效候选冻结为 `L17H00,L07H22,L02H05,L09H18`；`L11H03` 为频率伪阳性。该结果仅支持 object-row-conditioned reference-region retrieval signature，不支持 identity selectivity 或因果使用。
9. **R-019b Yes/No decision-token audit（已完成）**：使用 gold decision token `p` 的 `p-1` row，分别对 reference/query visual spans 重选 heads。双侧 Top-5 高度重合但 object GT 空间门禁全部失败，约 80% selected-head attention 流向 non-image history；仅记录 decision-position attention signature。
10. **R-020 三角色统一可视化（运行中）**：对 indices 80–89 的真实 positive/Yes 与 same-class negative/No 分别做一次推理一张图，统一展示 reference retrieval、query localization 和 Yes/No decision 双图 heatmaps。禁止跨 inference 拼图；per-panel min-max 仅供空间解释。
11. **下一主阶段：E-003 错误样本 attention audit（待 R-020 完成后启动）**：回到 E003-R-004b 的自然生成结果，专注分析 `identification=Yes` 但 localization 失败的 positive 样本，而不是继续细分 decision row 的文本历史。
   - 主错误集合：133 个 identification TP 中 `IoU<0.1` 的 35 个 accepted-low-IoU positives；低 IoU 只表示定位失败，不自动等于 wrong instance。
   - 高优先级子集：单人视觉初筛的 7 个 possible-wrong-instance cases，固定 IDs=`22,23,42,43,93,94,138`；必须始终标记 `screening_only_not_confirmed`。
   - 对照：从相同 class/尺度条件下选择 localization-correct、identification=Yes 的 matched positives；匹配规则须在读取 attention 前固定，不按 heatmap 结果挑选。
   - 冻结三组候选，不在错误样本上重新选头：
     ```text
     cross-image reference retrieval = L17H00,L07H22,L02H05,L09H18
     query bbox localization         = L18H15,L19H03,L22H00,L20H08
     Yes/No shared frequency control = L03H20,L04H29,L10H29,L12H21
     ```
   - 分析位置严格分开：`query-object visual rows→reference keys`、自然生成 bbox coordinate token `p-1→reference/query keys`、自然生成 Yes/No token `p-1→reference/query keys`。优先重放 E003 原始自然输出及其 token 序列；若 exact replay 不一致，run 必须 gate-failed，不能用 teacher-forced替代后宣称解释原错误。
   - 输出：每个错误 inference 一张 `reference|query` 统一图；错误预测 bbox 与 GT 同时标注（颜色/图例固定）；三组 combined map；逐样本 attention concentration、retrieval object/background contrast、decision visual budget；7 个 screening cases 单列，不伪造 non-target GT。
   - 比较目标：错误与 matched-correct 样本间的 attention signature 差异；不得把 heatmap 直接解释为“模型错误理解了身份”、wrong-instance 确认率或因果机制。
   - 后续确认：若 7 个样本出现稳定差异，再要求多实例 annotation/人工 taxonomy 或因果干预；attention audit 本身只用于提出可检验机制假设。
