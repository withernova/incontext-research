# E-012：重新确定 Query Head 与 Reference Head

> 状态：本地规划说明；对应 Run 已登记为 draft/code_planning。本文不代表审核通过、执行授权或实验结果。
>
> 当前没有可引用的 Solid Run 或显式 Run/Object reference。因此下面只定义接下来怎么做，不把已有 draft 数值或 head 列表当作结论。
>
> 详细公式、聚合顺序、方向、缺失值和产物字段统一见 [`dual_role_metric_contract.md`](dual_role_metric_contract.md)。后续 Agent 必须优先按该合同实现；Run 页面自动展示的旧 `query→query`、bbox 含标点指标仅是 Experiment 历史指标，不控制本轮双角色新主线。

## 一句话主线

过去的问题是：

> 哪些 head 的 attention map 和 GT 框长得像？

现在的问题是：

> **哪些 head 不仅对 bbox 预测重要，而且真正影响 bbox loss 的 visual contribution 主要来自目标区域？**

Query 和 Reference 都要按同一标准重新做一遍：

1. 这个 head 是否对 bbox 预测重要？
2. 它影响 bbox loss 的 visual contribution 是否主要来自对应图像？
3. 这部分 contribution 是否主要来自目标区域，而不是背景？
4. 去掉目标区域 contribution，是否比去掉等量背景 contribution 更伤害 bbox？

前 3 点用于找候选和独立确认，第 4 点才是因果检查。

---

## Run 主线总览

| Run | 直接要回答的问题 | 产出 |
|---|---|---|
| `R-004-contribution-calculation-check` | 我们计算 visual contribution 的方法到底对不对？ | 计算通过/失败，不选 head |
| `R-005-redetermine-query-heads` | 哪些 head 对 bbox 重要，而且有效贡献主要来自 Query 目标区域？ | 冻结 Query Head 候选 |
| `R-006-redetermine-reference-heads` | 哪些 head 对 bbox 重要，而且有效贡献主要来自 Reference 目标区域？ | 冻结 Reference Head 候选 |
| `R-007-confirm-query-reference-heads` | 两组候选在新样本上还能成立吗？ | Query/Reference 分别 PASS/FAIL |
| `R-008-target-vs-background-causal-ablation` | 去掉目标 contribution 是否比去掉等量背景更伤 bbox？ | 是否能称目标特异因果 head |
| `R-009-optional-generation-validation` | teacher-forced loss 上的效应会影响自由生成 bbox 吗？ | 可选外部效度 |
| `R-010-optional-cross-layer-path` | 这些 head 是否通过下游 A@V heads 共同影响 bbox？ | 可选跨层机制线索 |

核心主线是 R-004→R-005/R-006→R-007→R-008。R-009、R-010 只有前面通过后才考虑。

---

## R-004：先确认 contribution 算法没有错

### 为什么先做它

当前已有一次 signed gradient 与有限差分方向不一致的记录。在这个问题解决前，即使 absolute score 能排出 head，也不能确认我们测到的是预期的局部贡献。

### 做什么

在小型预冻结样本上，同时取得：

- attention probability `A`；
- value vector `V`；
- head 输出 `A@V`；
- bbox loss 对 `A` 的梯度；
- bbox loss 对 `A@V` 的梯度。

然后用两种方式独立计算同一条视觉边的贡献：

```text
方式一：A × dL/dA
方式二：<dL/d(A@V), A×V>
```

两者应该一致。还要分别对以下区域做小幅缩放和中央有限差分：

- Query 目标区域；
- Query 背景区域；
- Reference 目标区域；
- Reference 背景区域；
- Query/Reference 各自完整视觉区域。

### 必须通过的检查

- 无干预 hook 必须复现原 logits；
- 两种贡献计算必须在冻结容差内一致；
- 多样本、多 head、多区域的反传方向必须与有限差分一致；
- Query/Reference visual span、token grid 和 GT mask 必须准确对应；
- 主分析只使用四个 bbox 坐标 token 的预测行；括号和标点单独报告。

### 停止规则

R-004 不通过，就停止后面的重新选头。不能用“反正只看绝对值”绕过它。

---

## R-005：重新确定 Query Head

### 研究问题

> **哪些 head 不仅对 bbox 预测重要，而且真正影响 bbox loss 的 Query visual contribution 主要来自 Query 目标区域？**

### 对每个 head 连续检查三件事

#### 1. 它对 bbox loss 是否重要？

计算 bbox 坐标预测行经过 Query visual tokens 的绝对贡献：

```text
Query visual contribution =
Σ |attention × bbox-loss gradient|
```

这里的 gradient 已经经过 value 和后续网络，因此不是单纯看 attention map。

#### 2. 它的 visual contribution 是否确实来自 Query？

同一 head 同时保存：

- Query visual contribution；
- Reference visual contribution；
- text/other contribution。

这样可以排除“它只是一个整体贡献都很大的 head”。

#### 3. Query contribution 是否主要来自 Query GT？

把 Query visual contribution 分成：

- Query GT 目标区域；
- Query 背景区域。

除目标占全部 Query contribution 的比例外，还要按目标面积归一化，并与以下同图对照比较：

- 同面积平移到背景的框；
- token 数和形状尽量匹配的背景区域；
- 目标周围但不含目标的环带；
- 把 Reference 框的归一化坐标投影到 Query 图像得到的坐标复制对照。

### 怎样选候选

顺序必须固定：

1. 先按 Query visual contribution 形成候选池；
2. 再要求 Query GT contribution 高于匹配背景；
3. 再检查不同视频/样本重采样时是否稳定出现；
4. 每个角色最多保留 10 个，允许少于 10 个或零个；
5. 不达标时禁止用排名靠后的 head 补满。

attention heatmap 必须输出，但只作为解释图；不能因为图看起来像 GT 就入选。

### 结果边界

R-005 只能产出 **Query Head 候选**，不能称为已确认或因果 Query Head。

---

## R-006：重新确定 Reference Head

### 研究问题

> **哪些 head 不仅对 bbox 预测重要，而且真正影响 bbox loss 的 Reference visual contribution 主要来自 Reference 目标区域？**

### 方法

R-006 与 R-005 完全对称，只做以下替换：

```text
Query visual span      → Reference visual span
Query GT               → Reference GT
Query background       → Reference background
Reference坐标投影对照 → Query坐标投影对照
```

除此之外，候选池大小、空间对照、稳定性检查、最多 head 数量和统计规则必须相同。

### 为什么必须单独登记

我们不应先把 Q/R 混在一起生成一套 head，也不应拿 Query 排名帮助挑 Reference Head。分开登记后，可以直接看清：

- Query Head 候选是谁；
- Reference Head 候选是谁；
- 两组是否重合；
- 哪一组证据更稳定。

集合重合只作描述：低重合不自动证明功能分工，高重合也不证明同一 head 同时完成两项功能。

### 结果边界

R-006 只能产出 **Reference Head 候选**，不能称为已确认、identity-selective 或因果 Reference Head。

---

## R-007：用独立样本确认两组候选

### 研究问题

> R-005 的 Query Head 候选和 R-006 的 Reference Head 候选，在完全没有参与选头的新样本上还能成立吗？

### 做什么

不重新选 head，只评估冻结列表：

- Query candidates 对 Query GT 的 contribution 是否仍高于匹配背景；
- Reference candidates 对 Reference GT 的 contribution 是否仍高于匹配背景；
- 两组候选是否优于同层、同数量的随机 heads。

Query 和 Reference 分别给出 PASS/FAIL，允许：

- Query PASS / Reference PASS；
- Query PASS / Reference FAIL；
- Query FAIL / Reference PASS；
- 两者都 FAIL。

不能因为一方失败就回到 confirmation 数据上重新选 head。

### 通过标准

候选集合在独立样本上的“目标减匹配背景”效应方向稳定，cluster-bootstrap 95% CI 不跨 0，并优于同层随机 head controls。逐 head 结果是辅助分析，不能替代候选集合的主检验。

### 结果边界

通过 R-007 后可以称为 **独立确认的 target-aligned Query/Reference Head**；仍不能称因果 head。

---

## R-008：目标区域对等量背景的因果消融

### 研究问题

> 对确认后的 Query/Reference Heads，去掉目标区域的 visual contribution，是否比去掉等量背景 contribution 更明显地损害 bbox？

这是整条主线最关键的因果实验。

### Query 和 Reference 分开做

对每个通过 R-007 的角色，执行：

1. baseline / empty hook；
2. 去掉该角色 GT 目标区域的 attention edges；
3. 去掉同一图像中等 attention mass 的背景 edges；
4. 去掉同 token 数的背景 edges，作为另一种匹配方法；
5. 去掉另一视觉角色的目标 edges；
6. 对同层随机 heads 重复同样条件。

主干预位置：文本 self-attention 中 softmax/dropout 后、A@V 前，只作用于四个 bbox 坐标预测行，不重归一化。

### 主要结果怎么说

首先报告：

> 移除目标区域比移除等量背景多造成多少 bbox CE 损害？

技术记录可写为：

```text
目标特异损害 =
(目标移除后的 CE - baseline CE)
-
(匹配背景移除后的 CE - baseline CE)
```

还要检查这个差异是否大于同层随机 heads 的对应差异。

### 通过标准

只有同时满足下面条件，才称为固定范围内的“causally target-specific Query/Reference Head”：

- 目标移除比等 attention mass 背景移除更伤 bbox；
- cluster-bootstrap 95% CI 在正方向；
- 候选 heads 的效应强于同层随机 controls；
- 目标/背景实际移除的 attention mass 匹配成功；
- 效应不是只体现在括号或标点等格式 token 上。

如果整头消融有效、但目标对背景的局部消融无差异，只能说明这个 head 有一般功能，不能称目标特异 head。

---

## R-009：可选——自由生成 bbox 验证

只有 R-008 至少一个角色通过后再考虑。

问题是：teacher-forced bbox loss 上的目标特异效应，是否也会影响模型实际自由生成的 bbox？

主要报告：

- intervention 相对 baseline 的 IoU 变化；
- 目标移除和匹配背景移除的差；
- bbox 坐标变化；
- 无效框、多框、截断率；
- 输出文本是否整体崩坏。

自由生成时没有天然已知的 teacher-forced bbox 行，因此在线 bbox 状态检测和“所有 decode rows 干预”必须在实现前二选一。这个 Run 是外部效度，不阻塞 R-008 的局部因果结论。

---

## R-010：可选——跨层路径

只有 R-008 至少一个角色通过后再考虑。

问题是：已经通过目标特异检验的 Query/Reference Heads，是否通过另一批下游 A@V heads 共同影响 bbox？

上游 heads 必须来自 R-008，通过后冻结；下游 heads 必须由独立 A@V probe 在 discovery 数据上冻结，不能根据 rescue 结果反选。

比较：

- 上游目标区域扰动；
- 上游等质量背景扰动；
- 把 clean 下游 A@V patch 回扰动 run，能否救回；
- 把 corrupt 下游 A@V patch 到 clean run，能否迁移损害；
- 同层随机上游/下游 controls。

只有 target corruption 强于匹配背景，而且 clean rescue 与 corrupt transfer 都优于 controls，才称为固定路径下的跨层中介线索。即使通过，也不能称为完整或唯一 circuit。

---

## 数据切分：防止选头和验证混在一起

正式开始时只创建一次 master split：

1. **Discovery**：R-005/R-006 用于选 Query/Reference 候选；
2. **Confirmation**：R-007 只验证冻结候选；
3. **Causal**：R-008，及可选 R-009/R-010。

切分要求：

- 同一 sequence/video 不跨 split；
- 共享任一 Query/Reference 图像的记录视为同一个 connected component，不跨 split；
- 按数据集分层；
- 不根据 baseline 正确/错误选主样本；
- 零面积或无效 GT 在切分前显式审计和计数；
- 建议比例 40%/30%/30%，实际整数数量需在读取获准 manifest 后冻结。

---

## 技术指标摘要

本节只帮助阅读；实现时以 `dual_role_metric_contract.md` 为唯一详细定义，不允许仅凭下面摘要写代码。

逐边绝对 visual contribution：

```text
c_j = |A_j × dL_bbox/dA_j|
```

角色总贡献：

```text
C_role = Σ_{j属于Query或Reference} c_j
```

目标贡献占该角色视觉贡献的比例：

```text
TCR = C_target / (C_target + C_background)
```

单位面积目标 contribution 相对单位面积背景的 enrichment：

```text
TCE =
(C_target / target_token_occupancy)
/
(C_background / background_token_occupancy)
```

这些缩写只用于记录和实现。Run 的结论必须优先用自然语言表达：

- 这个 head 对 bbox 是否重要；
- contribution 是否来自 Query/Reference；
- 是否主要来自目标而不是背景；
- 目标移除是否比等量背景移除更伤 bbox。

---

## 命名边界

| 已有证据 | 可以怎么称呼 |
|---|---|
| 只对 bbox loss 有较大贡献 | bbox-relevant candidate |
| contribution 主要落在对应 GT，且高于背景 | target-aligned candidate |
| 在独立样本上复现 | confirmed target-aligned Query/Reference Head |
| 目标移除显著强于等量背景和随机 head | causally target-specific Query/Reference Head（仅限固定模型、数据和干预） |
| 下游 rescue/transfer 也通过 | 固定 U→D 路径的中介线索 |

attention map 好看本身不进入这张表。

---

## 当前仍需在实现前冻结的参数

1. R-004 的样本数、head 数、epsilon 集合和误差容差；
2. master manifest 的真实规模及 40/30/30 整数配额；
3. discovery 候选池大小（建议 50）和每角色最多 head 数（建议 10）；
4. 每样本生成多少个匹配背景区域；
5. bootstrap seed、次数和稳定性门槛；
6. R-009 若启动，选择 bbox-state detector 还是所有 decode rows 干预；
7. 正式新增指标的 canonical 定义。

这些参数尚未获得审核或执行授权，不得在看到结果后决定。
