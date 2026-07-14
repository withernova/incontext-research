# Token 干预关键结果汇总（E-001 / E-002）

> **目的：** 用一个本地表格压缩记录当前 token 干预实验的主要证据链。  
> **范围：** E-001 的 container / copy-padding 现象；E-002 的内部 token 替换、support-token contamination，以及 support/query token shuffle 结果。  
> **重要 caveat：** E-002 干预位置是 Qwen3-VL/IPLoc-ID 的 post-merge visual tokens，即 `image_outputs.pooler_output`，发生在 visual embeddings 被 `inputs_embeds.masked_scatter(image_mask, image_embeds)` 写入 LLM input embeddings 之前。LaSOT 没有实例 mask，因此 object footprint 使用 bbox 近似，而不是 segmentation mask。

## 1. E-001：copy-padding / container expansion 效应

| 实验 | 干预 | n / 数据 | 指标 | 结果 | 解释 |
|---|---|---:|---|---:|---|
| E-001 R-004c | query object token copy-padding / container expansion | 60 个 COCO visual-prompt 样本 | intervention / baseline 的平均预测框面积比 | **1.222** | 将 object-related tokens 向外复制后，预测框平均变大。 |
| E-001 R-004c | 同上 | 60 个 COCO visual-prompt 样本 | 相对 GT 的平均面积变化 | **+0.127** | 干预后预测面积相对 GT 增大。 |
| E-001 R-004c | 同上 | 60 个 COCO visual-prompt 样本 | 预测面积增大的样本比例 | **0.591** | 59.1% 的 matched cases 在干预后预测面积变大。 |
| E-001 R-004c | 同上 | 60 个 COCO visual-prompt 样本 | 平均 IoU 变化 | **-0.083** | 向外扩张通常降低定位精度。 |

**E-001 小结：** 向外复制 object tokens 支持一种 container-style effect：扩大 object-token support 会让预测框倾向于扩张，但并不会提升定位质量。

---

## 2. E-002：内部 token 替换 / contamination

### 2.1 R-012：将 reference tokens 替换进 negative-query 的 object slots

| 实验 | 模式 | negative 数 | TP | TN | FP | FN | F1 | neg_FPR | 关键点 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| R-012 | baseline | 27 | 27 | 22 | 5 | 0 | 0.915 | 0.185 | same-class negative query 上的 baseline。 |
| R-012 | query_obj_replace_ref_full | 27 | 27 | 14 | 13 | 0 | 0.806 | **0.481** | 完整 reference-token replacement 显著增加 false positives。 |
| R-012 | query_obj_replace_ref_center50 | 27 | 27 | 22 | 5 | 0 | 0.915 | 0.185 | center50 replacement 没有比 baseline 增加 FP。 |
| R-012 | query_obj_replace_ref_center25 | 27 | 27 | 24 | 3 | 0 | 0.947 | 0.111 | center25 replacement 在此 run 中没有造成损害。 |
| R-012 | query_obj_shuffle_full | 27 | 27 | 26 | 1 | 0 | 0.982 | 0.037 | 仅打乱 query 自己的 object tokens 没有诱导明显 FP。 |

**R-012 caveat：** 后续可视化检查发现 source / destination token 数可能严重不平衡，例如 support tokens 可能被重复写入大量 query slots。因此 R-012 更稳妥的解释是 **reference-token stamping / contamination 敏感性 pilot**，而不是干净的自然 identity transfer 证明。

### 2.2 R-014：逐步、部分 support-token contamination，主要使用 no-repeat 设置

| 实验 | 模式 | negative 数 | TP | TN | FP | FN | F1 | neg_FPR | 相对 baseline 的 neg_FPR 变化 | 解释 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R-014 | baseline | 27 | 27 | 23 | 4 | 0 | 0.931 | 0.148 | — | 本 run 的 baseline。 |
| R-014 | query_obj_mix_ref_p25_norepeat | 27 | 27 | 20 | 7 | 0 | 0.885 | 0.259 | +0.111 | 只混入一部分唯一 support tokens 已经会增加 FP。 |
| R-014 | query_obj_mix_ref_p50_norepeat | 27 | 27 | 20 | 7 | 0 | 0.885 | 0.259 | +0.111 | 此 run 中与 p25 接近。 |
| R-014 | query_obj_mix_ref_p75_norepeat | 27 | 27 | 16 | 11 | 0 | 0.831 | 0.407 | +0.259 | 更强 contamination 导致更多 FP。 |
| R-014 | query_obj_replace_ref_p100_norepeat | 27 | 27 | 15 | 12 | 0 | 0.818 | **0.444** | +0.296 | capped one-to-one replacement 也显著增加 FP。 |
| R-014 | query_obj_replace_ref_p100_repeat | 27 | 27 | 15 | 12 | 0 | 0.818 | **0.444** | +0.296 | repeat/stamping 在此 run 中没有超过 no-repeat p100。 |
| R-014 | query_obj_shuffle_full | 27 | 26 | 27 | 0 | 1 | 0.981 | **0.000** | -0.148 | 仅打乱 query 自己的 object tokens 没有制造 negative FP。 |

**R-014 小结：** R-012 的效应不只是 repeated-token stamping artifact。即使 support tokens 不重复使用、只部分混入 negative-query object container，也会增加 same-class negative false positives，并且从 p25/p50 到 p75/p100 大致呈现剂量效应。

---

## 3. E-002：support/query object-token shuffle 顺序实验

### 3.1 R-011：large/token-rich 子集上的 reference+query 联合 object-token shuffle

| 实验 | 模式 | negative 数 | TP | TN | FP | FN | F1 | neg_FPR | 解释 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| R-011 | baseline | 27 | 27 | 27 | 0 | 0 | 1.000 | 0.000 | large/token-rich 子集上 baseline 完美。 |
| R-011 | ref_query_obj_shuffle_full | 27 | 27 | 24 | 3 | 0 | 0.947 | 0.111 | 联合 object shuffle 有可测但有限的影响。 |
| R-011 | ref_query_obj_shuffle_center50 | 27 | 27 | 25 | 2 | 0 | 0.964 | 0.074 | center50 shuffle 也带来小幅 FP。 |
| R-011 | ref_query_obj_shuffle_center25 | 27 | 26 | 24 | 3 | 1 | 0.929 | 0.111 | center25 产生 FP，同时有 1 个 FN。 |
| R-011 | full_visual_shuffle | 27 | 27 | 0 | 27 | 0 | 0.667 | **1.000** | full visual-token shuffle 彻底破坏 negative rejection。 |

### 3.2 R-015：support-only vs query-only vs support+query shuffle

| 实验 | 模式 | negative 数 | TP | TN | FP | FN | F1 | neg_FPR | 解释 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| R-015 | baseline | 27 | 27 | 25 | 2 | 0 | 0.964 | 0.074 | support/query 分离实验的 baseline。 |
| R-015 | support_obj_shuffle_full | 27 | 27 | 26 | 1 | 0 | 0.982 | 0.037 | 只打乱 support object-token order **没有损害检测**。 |
| R-015 | query_obj_shuffle_full | 27 | 27 | 26 | 1 | 0 | 0.982 | 0.037 | 只打乱 query object-token order **没有损害检测**。 |
| R-015 | support_query_obj_shuffle_full | 27 | 27 | 26 | 1 | 0 | 0.982 | 0.037 | support 和 query 同时 shuffle 也 **没有损害检测**。 |
| R-015 | full_visual_shuffle | 27 | 27 | 0 | 27 | 0 | 0.667 | **1.000** | global visual-token structure 仍然对 negative rejection 至关重要。 |

**Shuffle 小结：** object-internal token order 在某些 run 中有小幅可测影响（如 R-011），但 R-015 显示 support-only、query-only、support+query object-order shuffle 都没有稳定破坏 POIL。这反对“模型主要由 object 内部 token 顺序支配”的强机制假设。

---

## 4. 当前综合判断

| 命题 | 证据状态 | 支持结果 | 当前表述 |
|---|---|---|---|
| 向外复制 object tokens 可以扩大预测框。 | E-001 支持 | R-004c 面积比 1.222，面积增大比例 0.591 | container expansion 会影响 localization geometry。 |
| POIL 主要由 object-internal token order 控制。 | 强说法不被支持 | R-015 shuffle modes 的 neg_FPR 均为 0.037，低于 baseline 0.074；R-014 query shuffle neg_FPR 为 0.000 | object order 可能有弱贡献，但不是主导因素。 |
| full/global visual-token structure 对 negative rejection 很关键。 | 强支持 | R-011/R-015 full_visual_shuffle 的 neg_FPR 都为 1.000 | 破坏全局视觉布局会导致 negative rejection 崩溃。 |
| query object container 对 support/reference-like token evidence 敏感。 | 支持 | R-014 no-repeat contamination 将 neg_FPR 从 0.148 提高到 0.259 / 0.407 / 0.444 | 部分 support-token contamination 可以诱导 same-class false positives。 |
| R-012 证明了干净的 identity transfer。 | 不支持 / 说法过强 | R-012 存在 source-destination token 数不平衡；R-014 是针对该问题的控制实验 | R-012 应描述为 contamination / stamping sensitivity，而不是语义 identity transfer 的证明。 |

## 一句话结论

当前证据更支持一种 **containerized reference-matching** 解释：POIL 对 object-internal token order shuffle 相对鲁棒，但 negative rejection 对全局视觉结构以及 query object 空间容器中混入的 support/reference-like token evidence 高度敏感。
