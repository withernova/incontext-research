# E-005 双卡 640 同分辨率复核：高浓度核心结果

> 日期：2026-07-28  
> 状态：`completed / inference_only / attention-derived non-causal`  
> 范围：R-024–R-033；核心科学结果来自 R-027、R-028、R-029c、R-030c、R-033。失败的 R-029/R-029b 仅为 manifest schema 实现错误，无科学输出。

## 1. 一句话结论

在原始 E003-R-004b positive n=140 上，accepted-positive localization failures 的最强 attention-derived 特征不是 prompt-stage reference grounding 消失，而是 **natural bbox rows 经 query-localization heads 投向 query visual keys 的 GT 空间命中（Q→Q）大幅下降**：error `5/35=14.3%`，correct `73/76=96.1%`；Q→Q target mass 中位数 `.0175 vs .4379`，enrichment `.662 vs 16.00`。相反，G→R hit 近乎相同（`94.3% vs 94.7%`）。G→R 与 Q→R target-mass discrepancy 在 error 中方向上更大，但 sequence-cluster CI 跨 0；扩大 n=280 后连续相关接近 0，因此“binding discrepancy 是稳定主机制”的假设未获稳定支持。

## 2. 输入、模型与分辨率边界

```text
模型：Qwen3-VL-8B-Instruct + IPLoc-ID LoRA
模型路径：/home/featurize/work/mechanism/models/Qwen3-VL-8B-Instruct
GPU：RTX 4090 24GB ×2
精度：bf16
attention：HF standard eager, output_attentions=True
设备：device_map=auto, max_memory=22GiB/GPU
分辨率：max_side=640
```

`640` 是公开代码默认 `max_side`，且与归档自然生成一致；论文正文没有披露明确 resize 规则，故不得称其为论文明确 benchmark 分辨率。

R-025 工程门禁：5/5 两图 forward、36/36 attention layers、全部 finite、exit 0；峰值显存约 GPU0 `8.17 GiB`、GPU1 `9.71 GiB`。这证明双 4090 可运行标准完整 640 eager attention，不需要降到 224。

## 3. 三种角色与自回归对齐

令 token 位置 `p` 的 token 由 attention row `p-1` 预测。

```text
G→R（prompt-stage reference grounding）
  reference bbox token p-1 rows
  × reference-grounding heads L15H13,L16H23,L18H15
  → reference visual keys

Q→R（natural bbox-stage reference lookback/binding）
  archived natural query bbox token p-1 rows
  × query-localization heads L18H15,L19H03,L22H00,L20H08
  → reference visual keys

Q→Q（natural bbox-stage query localization）
  同一 archived natural query bbox token p-1 rows
  × 同一 query-localization heads L18H15,L19H03,L22H00,L20H08
  → query visual keys
```

G→R 与 Q→R 使用不同 rows 和不同 head 集合；其差异不能解释为同一电路中信息随时间丢失。Q→R 与 Q→Q 使用相同 rows/heads，但 key span 不同。

## 4. 指标定义

### 4.1 Fractional merged-token occupancy

GT bbox 对 merged-token cell `i` 的覆盖比例为 `o_i∈[0,1]`。这是 merged-token support，不是 pixel segmentation。报告：

```text
tokens_any_overlap = count(o_i>0)
fractional_coverage = Σ_i o_i
```

### 4.2 Target mass

对 raw nonnegative attention map 归一化：

\[
v_i=A_i/(\sum_j A_j+\epsilon)
\]

GT target mass：

\[
P_{target}=\sum_i v_i o_i
\]

它表示 attention 预算中落入 GT 覆盖区域的比例，是正式绝对强度指标；不能由 panel 内 min-max 热图颜色替代。

### 4.3 GT enrichment

\[
E=\frac{\sum_i A_i o_i/(\sum_i o_i+\epsilon)}
        {\sum_i A_i(1-o_i)/(\sum_i(1-o_i)+\epsilon)+\epsilon}
\]

`E>1` 表示 GT 区域的平均 attention density 高于 GT 外。

### 4.4 Pointing 与 strict hit

```text
pointing = raw-map argmax cell 与 GT 有非零重叠
strict hit H(map)=1 iff：
  enrichment > 1
  AND pointing=true
  AND GT overlaps >=2 merged tokens
```

文件/manifest 中 `G→R、Q→R、Q→Q hit` 均按此定义。它是 attention-derived spatial signature，不是因果影响。

### 4.5 Binding discrepancy

\[
D_{signed}=logit(P_{G→R})-logit(P_{Q→R})
\]

\[
D_{abs}=|D_{signed}|
\]

其中 `logit(P)=log(P/(1-P))`。主比较为 error 与 correct 的 `D_abs` 中位数差；不用 raw-map pixel L2/top-k overlap 作为主指标。

### 4.6 Full-map JSD

G→R 与 Q→R 在 reference grid 上归一化分布的 Jensen–Shannon divergence，仅为次要诊断；不同 rows/head 角色使其不能被解释为同一 map 应完全相等。

## 5. 原始 E003 positive n=140：核心结果（R-029c/R-033-positive）

### 5.1 自然行为分组

```text
localization-error：positive image + natural Yes + IoU<0.1       n=35
localization-correct：positive image + natural Yes + IoU>=0.7    n=76
localization-partial：positive image + natural Yes + .1<=IoU<.7  n=22
identification-fn：positive image + natural No                    n=7
```

### 5.2 三角色空间指标

| 指标 | localization-error n=35 | localization-correct n=76 |
|---|---:|---:|
| G→R strict-hit rate | 33/35 = **94.3%** | 72/76 = **94.7%** |
| Q→R strict-hit rate | 9/35 = **25.7%** | 26/76 = **34.2%** |
| Q→Q strict-hit rate | 5/35 = **14.3%** | 73/76 = **96.1%** |
| G→R target mass median | **.1981** | **.3287** |
| Q→R target mass median | **.02317** | **.10450** |
| Q→Q target mass median | **.01750** | **.43787** |
| Q→Q enrichment median | **.6625** | **16.004** |

关键结构：

```text
G→R hit 几乎不分 error/correct：prompt reference grounding普遍存在。
Q→R 在两组都较弱，correct方向更高，但不是最强分离项。
Q→Q 在error中大幅下降，是当前最清楚的行为相关attention signature。
```

注意：Q→Q 由 natural bbox token rows 提取，是 archived-output teacher replay；它描述输出坐标阶段的 attention signature，不证明这些 heads 因果地产生 bbox。

### 5.3 Discrepancy 结果

```text
D_abs median：
  error   = 2.1006
  correct = 1.5269
  error-correct = +0.5737

sequence-cluster bootstrap 95% CI：[-0.2216, 1.4190]
Spearman(D_abs, IoU)，accepted extremes n=111：
  rho=-0.1860, p=.05067
```

解释：方向符合“error discrepancy 更大”，但 cluster CI 跨 0，相关仅弱负且边界；不能称稳定确认。

640 reference coverage：

```text
median=9 tokens
<=1：3/140
2–3：16/140
>=4：121/140
```

低覆盖已显著缓解，但仍需报告，不能把插值热图当新增空间信息。

## 6. 冻结 matched 35×2 的 224→640 复核（R-028）

样本完全继承 R-023 的冻结 35 error + 35 geometry-matched correct；不重新匹配。

```text
640 target-consistent state 11：
  error   9/35 = 25.7%
  correct 13/35 = 37.1%
  correct-error = +11.43 percentage points
  paired bootstrap 95% CI = [-11.43, 34.29] pp

conditional Q→R binding given eligible G→R：
  error   9/33 = 27.3%
  correct 13/33 = 39.4%

reference coverage median：
  224 replay = 4 tokens
  640 replay = 6 tokens

四状态完全稳定：39/70
```

Raw paired结果：

```text
G→R target-mass paired median(correct-error)=+.00286
95% CI[-.04268,.03979]

Q→R target-mass paired median(correct-error)=+.03230
95% CI[.00604,.08811]
```

因此 640 下较稳定的 matched 信号是 correct 的 Q→R target mass 更高；G→R mass 无明显组差。离散 state 对分辨率敏感（仅 39/70 保持），所以旧 224 频率不能直接当同分辨率结论。

## 7. 扩充 n=280 的 sequence-aware 结果（R-024/R-026/R-027）

数据：70 个不与旧 0–139 manifest 重叠的 LaSOT sequences，每 sequence 4 个时间分散 query，共 280 positive cases；与 R-014 unseen70 共用这些 sequences，非官方 IPLoc split。统计以 sequence 为 cluster。

```text
自然分组：error48 / correct177 / partial45 / rejected10
280/280 exact alignment，unalignable=0
coverage median=8 tokens，>=4为248/280

D_abs median：
  error=1.5674
  correct=1.3045
  difference=+.2629
  sequence-cluster 95% CI=[-.3483,.9869]

Spearman(D_abs,IoU)，accepted extremes n=225：
  rho=-.03744, p=.5764
```

扩大结果未稳定支持 discrepancy–IoU 关系。它削弱了“D_abs 本身是稳健主指标”的判断，但不否定原始 n=140 中 Q→Q localization signature 的大幅组差；两者是不同指标。

## 8. 原始 negative n=140（R-030c/R-033-negative）

```text
identification-tn：natural No，136/140
identification-fp：natural Yes，4/140
```

negative bbox IoU 是 prediction 与 same-class distractor GT 的 `candidate-IoU`，不是 personalized localization correctness，不能并入 positive error/correct。

固定 attention 描述：

```text
TN n=136：G→R hit 93.4%，Q→R hit 14.7%，Q→Q hit 65.4%
FP n=4：样本太少，仅描述，不做稳定组间推断
```

generic discrepancy script 对 negative 生成的 `error/correct/middle` 标签无定位含义，正式结论只使用 TN/FP。

## 9. 可视化交付

完整五栏顺序：

```text
1 Reference clean + reference GT
2 G→R reference-head map
3 Q→R query-head map on reference keys
4 Q→Q query localization map + GT/pred
5 Query clean + GT/pred
```

颜色：turbo 蓝低红高；绿框=GT；红框=归档自然预测。每 panel 独立 min-max，仅用于空间观察。

完整 280 图：

```text
remote:
/home/featurize/work/mechanism/explog/E-005/runs/
E005-R-033-positive-full140-unified-fivepanel-640/presentation/by_behavior/
E005-R-033-negative-full140-unified-fivepanel-640/presentation/by_behavior/

positive：localization-error35 / localization-correct76 /
          localization-partial22 / identification-fn7
negative：identification-tn136 / identification-fp4
```

最终文件名只编码行为、index、class、自然决策与 IoU；attention 连续指标和 hit bits 存于 `presentation/presentation_manifest.json`。

本地预览：

```text
shell/06_experiments/E-005/visualizations/R-032/
```

## 10. 结论边界与方法决策

### 当前支持

1. 640 标准 eager attention 在双 4090 上可行，消除了 640 natural generation→224 replay 的主要分辨率混杂。
2. accepted-positive localization errors 中，prompt-stage G→R grounding strict hit 通常仍存在。
3. natural bbox-stage Q→Q query-localization attention 对 GT 的 concentration/hit 在 error 中大幅下降，是当前最强 attention-derived behavioral correlate。
4. matched 640 中 correct 的 Q→R target mass 高于 error，但二元 state 和整体 discrepancy 证据较弱且受分辨率影响。

### 当前不支持

1. 不支持“error 与 correct 中所有 attention head 作用被抹平”。
2. 不支持 `D_abs` 是跨数据稳定的定位失败主指标；n=280 的连续相关近 0。
3. 不支持 identity-selective head、wrong-instance rate或 causal localization circuit。
4. 不支持立即以单一 G→R/Q→R discrepancy loss 作为已验证训练目标。

### 最安全表述

> Prompt-stage reference grounding remains broadly present in both correct and accepted-positive localization-failure cases. The strongest error-associated attention signature at max_side=640 is a collapse of natural bbox-stage query localization toward the query GT (Q→Q), while Q→R reference target mass is also lower in matched errors. However, the proposed G→R-versus-Q→R discrepancy is not statistically stable across the matched and enlarged sequence-aware analyses. These are attention-derived, teacher-replayed, non-causal observations.

## 11. 远程审计入口

```text
R-025 smoke:
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-025-dualgpu-640-eager-attention-smoke-n5/

R-027 expanded n280:
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-027-binding-discrepancy-unseen-multiframe-n280-640/

R-028 matched 35x2 at640:
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-028-r023-matched35x2-same-resolution-640/

R-029c original positive n140:
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-029c-original140-positive-targets-binding-640/

R-030c original negative n140:
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-030c-original140-negative-targets-binding-640/

R-033 full visualizations:
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-033-positive-full140-unified-fivepanel-640/
/home/featurize/work/mechanism/explog/E-005/runs/E005-R-033-negative-full140-unified-fivepanel-640/
```
