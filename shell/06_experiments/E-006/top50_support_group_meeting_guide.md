# E-006 组会讲解：什么是 top50 attention support？

> 对应 canonical run：`E006-R-005-simple-top50-support-components-positive-extremes-n111-640`
>
> 本文只解释该 run 已执行的固定算法和已观测结果，不引入新的 threshold sweep。

## 1. 一句话定义

`top50 attention support` **不是取数量排名前50%的tokens**，而是：

> 在指定目标图像的 merged-token span 内，寻找一个最小的高-attention token集合，使该集合承载至少50%的“图像内条件attention质量”。

它也不是“模型有50%的全局attention落在这张图上”。本实验先把目标图像外的所有文本、另一张图像、特殊token等排除，再对目标图像内部重新归一化。因此它回答的是：

```text
条件于这个head已经分给目标图像的attention，
图像内部最强的哪些位置合起来承载了一半？
```

不能回答：

```text
这个head对目标图像投入了多少全局attention预算？
```

## 2. attention map从哪里来

对一个固定 head `h` 和一种关系：

```text
G→R：reference bbox token p-1 rows → reference image keys
Q→R：natural query bbox token p-1 rows → reference image keys
Q→Q：natural query bbox token p-1 rows → query image keys
```

若 bbox 文本对应多个输出tokens，先对这些 `p-1` query rows 的 attention 逐位置取均值：

\[
a_i=\frac{1}{|T|}\sum_{t\in T}A^{(h)}_{t-1,i},\qquad i\in I,
\]

其中：

- `T` 是 reference 或 natural-query bbox 的精确 token positions；
- `t-1` 遵守 autoregressive alignment：row `t-1` 预测 token `t`；
- `I` 是当前关系的目标 image span；
- G→R 使用 reference bbox rows；Q→R/Q→Q 使用 archived natural query bbox rows；
- 每个 head 单独计算，不先把多个heads平均。

## 3. 图像内条件归一化

只保留目标 image span 内的 merged visual tokens，并归一化：

\[
p_i=\frac{\max(a_i,0)}{\sum_{j\in I}\max(a_j,0)+10^{-30}},
\qquad \sum_{i\in I}p_i\approx1.
\]

标准 softmax attention 本来非负；`max(a_i,0)` 是防御性处理。`10^{-30}` 只防止除零。

因此 `p_i` 的分母**不是完整序列的所有key tokens**。例如 Q→R 中，query图像和文本key都不在分母中。由此产生的重要边界是：

> 一个head即使全局只给reference image很少的attention，也仍会在reference内部得到一个top50 support。本实验描述空间落点，不衡量跨模态全局预算。

## 4. “从大到小选最少tokens”的精确算法

把 `p_i` 按从大到小排序：

\[
p_{(1)}\ge p_{(2)}\ge\cdots\ge p_{(N)}.
\]

选择最小整数：

\[
k^*=\min\left\{k:\sum_{j=1}^{k}p_{(j)}\ge0.5\right\}.
\]

support集合为：

\[
S_{50}=\{(1),\ldots,(k^*)\}.
\]

脚本的等价核心代码：

```python
v = np.maximum(attention_map.reshape(-1), 0)
v = v / (v.sum() + 1e-30)
order = np.argsort(-v, kind="stable")
k = np.searchsorted(np.cumsum(v[order]), 0.5, side="left") + 1
selected = order[:k]
```

### 最小性的含义

它同时保证：

```text
sum(top k*) >= .5
sum(top k*-1) < .5
```

所以没有任意多选token。若最强单token已经占 `.63`，则 `k*=1`；若attention接近均匀，可能需要接近一半图像tokens。

### 为什么实际selected mass通常大于0.5

最后一个token不能被切成一部分，所以会越过阈值。例如排序质量为：

```text
.22, .17, .12, .09, ...
```

则：

```text
前2个=.39 <.50
前3个=.51 >=.50
```

因此选3个，保存的 `selected_mass=.51`。这个 overshoot 是离散token的正常结果，不是阈值改变。

### 精确并列

代码使用稳定排序。若多个token数值完全相同且跨过边界，只按原始row-major顺序选到满足阈值为止，不自动把全部并列token扩入support。标准浮点attention中精确并列通常少见，但这是实现边界。

## 5. 一个220-token图像的直观例子

本run中 merged grid token数：

```text
median=220
Q1=220, Q3=220
min=84, max=300
最常见grid=11×20（94/111样本）
```

假设某个head在11×20=220个reference tokens内：

```text
前1个累计=.18
前2个=.31
前3个=.40
前4个=.47
前5个=.53
```

那么：

```text
k*=5
selected-token-count=5
top50 support只覆盖5/220=2.27%的token位置
但承载该head在reference内部53%的条件attention
```

这正是“attention质量”与“空间面积”的区别。

## 6. k*本身表达什么

在图像token数近似相同的前提下：

```text
k*小：图像内attention质量集中在少量merged tokens
k*大：至少一半attention分散在更多merged tokens
```

但它不是无混杂的“集中度”：

- grid token总数可在84–300变化；
- 不同head的attention分布天然不同；
- selected tokens可能空间相邻，也可能散成许多小岛；
- `k*`不说明selected tokens是否落在GT；
- `k*`也不说明该图像获得多少全局attention。

因此 E-006 同时报告 token数、联通子图和GT相交，而不单独依赖 `k*`。

## 7. Q→R真实selected-token-count

| Head | Error k* 中位数 [Q1,Q3] | Correct k* 中位数 [Q1,Q3] | Error token占比中位数 | Correct token占比中位数 |
|---|---:|---:|---:|---:|
| L18H15 | 9 `[4,11.5]` | 12.5 `[6.75,16]` | 4.09% | 5.91% |
| L19H03 | 6 `[2,20]` | 17 `[5.75,27]` | 3.64% | 7.95% |
| L22H00 | 35 `[17,42]` | 38 `[31,43]` | 17.27% | 18.18% |
| L20H08 | 6 `[2,15.5]` | 12 `[3,20]` | 2.73% | 5.45% |

这里不能说 correct 的 Q→R 更“集中”。相反，在这四个heads里，correct通常需要更多tokens才能累计到50%。结合命中结果，正确表述是：

> correct中的Q→R top50 support一般更广/包含更多tokens，同时更常与reference GT相交；它不是更小、更紧凑的support。

特别是 L22H00：

```text
k* median error=35，correct=38
component median error=17，correct=19.5
```

该head的top50 support很碎，任意小岛碰GT容易饱和，所以 `largest-component-hit` 比普通 `support-hit` 更有解释力。

## 8. selected mass的实际范围与overshoot

Q→R selected-mass中位数：

| Head | Error | Correct |
|---|---:|---:|
| L18H15 | .5128 | .5083 |
| L19H03 | .5098 | .5072 |
| L22H00 | .5037 | .5041 |
| L20H08 | .5178 | .5093 |

多数非常接近 `.5`，说明最小集合规则按预期工作。个别样本可明显越过 `.5`，因为单个高权重token足以跨过边界；全run保存了每个head/sample的真实 `selected_mass`，没有强制重标为恰好 `.5`。

## 9. support与GT如何结合

GT bbox被投影到 merged-token grid。每个cell记录bbox占该cell的面积比例：

\[
o_i\in[0,1].
\]

因此：

### H：support hit

\[
H=\mathbf{1}[\exists i\in S_{50}:o_i>0].
\]

只要一个selected token与GT有任意fractional overlap就算hit，属于宽松指标。

### M：majority on GT

\[
P_{GT}=\sum_{i\in I}p_io_i,
\qquad M=\mathbf{1}[P_{GT}>0.5].
\]

注意 M 使用**全部image-span tokens**，不是只在top50 support里算；并且采用 fractional occupancy。它表示图像内条件attention中超过一半落在GT区域，是严格指标。

### C / CG / L

把 `S50` 恢复成二维merged-token mask，用4-neighbor（上、下、左、右）连通：

```text
C：全部support components数
CG：至少含一个o_i>0 token的components数
L：token数量最大的component是否与GT相交
```

对角相邻不算连接。最大component按selected token数量定义，不按attention质量或像素面积定义；若最大大小精确并列，当前实现取component扫描顺序中的第一个，这是需公开的边界。

## 10. 组会应如何解释主结果

### G→R

```text
3/3 heads全部support-hit：
error 34/35=97.1%
correct 76/76=100%
```

所以：

> prompt/reference grounding support在两组中几乎都能触及reference GT，普通hit已经饱和。

不能说：

> error没有grounding。

### Q→R

```text
每样本hit heads：2.51 vs 3.22
correct-error=.709，CI[.086,1.329]

4/4 heads都hit：45.7% vs 71.1%

最大component命中head数：1.74 vs 2.51
difference=.770，CI[.071,1.460]
```

所以：

> correct中有更多query-localization heads的主要reference support与reference GT相交，且最大support component更常相交。

但：

```text
至少一个Q→R head满足M：
error 2.9%
correct 6.6%
```

所以不能说：

> correct时多数Q→R attention都落在reference GT。

### Q→Q

```text
hit-head mean：error 1.0/4，correct 4.0/4
```

它主要验证 archived natural bbox rows 与query空间位置的一致性。由于分组本身依据bbox IoU，Q→Q强差异具有定义性，不应包装成新机制。

## 11. 展示图怎么读

每行一个head：

```text
橙色格：S50，即承载至少50%图像内条件attention的最小token集合
绿色框：GT bbox
H：任一橙色格是否碰GT
M：全部图像内条件attention的fractional GT mass是否>.5
C：橙色格的4邻域component数
CG：碰GT的component数
L：最大component是否碰GT
```

橙色格只显示二值support，不显示格内attention强弱。因此它适合回答“主要区域在哪里、是否碎片化”，不适合比较两个橙色格谁更强。

## 12. 必须主动说明的局限

1. `50%` 是预冻结的可解释阈值，不是论文给定标准，也未在本run中扫描。
2. 这是 attention support，非activation patching/ablation，不能推断因果影响。
3. Q→R只显示对reference目标区域的空间相交，不证明identity-selective matching。
4. 条件归一化抹掉了目标图像获得的全局attention预算；本run不是global-budget audit。
5. merged-token cell约为粗网格支持，不是pixel segmentation。
6. `H`只要求任意fractional overlap，易受目标大小和碎片化影响；因此同时报告M和L。
7. component数量受grid、selected-token-count和attention碎片化共同影响，不能单独解释为“更好/更坏”。
8. teacher replay使用archived natural output；Q→Q是行为一致性检查。
9. 数据是本地split重建，非官方IPLoc-ID split。

## 13. 最推荐的一页组会结论

```text
固定定义：每head、每目标图像内，取承载50%条件attention的最小merged-token集合。

G→R：support hit几乎饱和（3/3 hit：97.1% vs100%），
说明localization-error并非简单缺失prompt-stage reference grounding。

Q→R：correct中命中reference GT的heads更多（2.51→3.22/4），
且最大component命中的heads更多（1.74→2.51/4）。

但Q→R majority-on-GT极少（至少一head：2.9% vs6.6%），
不能表述为“多数attention落在reference GT”。

Q→Q：1.0→4.0/4，仅作natural-bbox localization sanity check。

全部结果是attention-derived、teacher-replay、non-causal。
```

## 14. 审计产物

```text
逐sample/head原始记录：analysis/summary.json
补充选择统计：analysis/support_selection_details.json
bootstrap组差：analysis/poststats.json
逐样本可视化：visualizations/*.png
实验代码：codespace/e005_adapter/e006_simple_support_audit.py
正式结果：shell/06_experiments/E-006/result.md
```
