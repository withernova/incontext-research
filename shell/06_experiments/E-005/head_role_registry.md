# E-005 Attention-derived Head Role Registry

> 状态：开发期、attention-derived、非因果。这里的“角色”表示在指定 query 定义下通过空间质量审核的候选，不表示该 head 因果负责对应功能。

## 1. Reference grounding candidates

定义：原始 prompt 顺序中，`reference bbox token p` 的 `p-1` prediction rows → reference visual keys。

有效候选：

```text
L15H13
L16H23
L18H15
```

频率伪阳性：

```text
L10H29
L04H29
```

证据边界：测量 user-input reference bbox 与 reference 图像区域的绑定；不等于 reference identity encoding。

## 2. Cross-image reference retrieval candidates

定义：原始 prompt 顺序中，GT-conditioned query-object visual rows → reference visual keys。

有效候选：

```text
L17H00
L07H22
L02H05
L09H18
```

频率伪阳性：

```text
L11H03
```

证据边界：这些 heads 对 query-object rows 到 reference-object region 呈空间选择性，且强于 query-background rows；positive 与 same-class negative 的 paired 差异不稳定，故不支持 identity-selective 或因果 reference use。

## 3. Query bbox localization candidates

定义：assistant 输出 `query bbox token p` 的 `p-1` prediction rows → query visual keys。

有效候选：

```text
L18H15
L19H03
L22H00
L20H08
```

频率伪阳性：

```text
L24H27
```

证据边界：在新 sequence n=70 上通过双 span 空间确认，但仍为 teacher-forced、attention-derived、非因果定位 signature。

## 4. 当前重合关系

```text
reference grounding ∩ query localization:
  L18H15

cross-image reference retrieval ∩ query localization:
  ∅（当前有效候选的 exact-head overlap）

cross-image reference retrieval ∩ reference grounding:
  ∅（当前有效候选的 exact-head overlap）
```

不同 query 定义下的 Top-5 frequency overlap 不能代替逐 head GT 质量审核。

## 5. Identity-decision attention signature（E005-R-019b）

定义：

```text
gold Yes/No decision token p 的 p-1 row → reference visual keys
gold Yes/No decision token p 的 p-1 row → query visual keys
```

Reference-span frequency Top-5：

```text
L10H29
L12H21
L10H09
L03H20
L04H29
```

Query-span frequency Top-5：

```text
L12H21
L03H20
L10H29
L02H11
L04H29
```

两侧交集：

```text
L03H20, L04H29, L10H29, L12H21
Jaccard = 0.667
```

质量结论：这些 heads 在 positive/negative、reference/query 两侧的 object GT enrichment 约为 `0.10–0.13`，pointing 均为 `0`，空间质量门禁全部失败。Selected-head median attention budget 约为：

```text
reference image = 8.5%–10.7%
query image     = 9.6%–10.1%
other history   = 80%–81%
```

它们与当前有效 reference-grounding、cross-image retrieval、query-localization candidates 的 exact-head overlap 均为 0。故只能记录为稳定的 decision-position attention signature，不能称为 object-localizing identity-decision heads；raw attention 不能证明视觉 identity evidence 或因果判别作用。
