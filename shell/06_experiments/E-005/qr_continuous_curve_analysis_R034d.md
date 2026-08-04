# E005-R-034d：Q→R 连续指标、阈值曲线与空间曲线离线复核

> 日期：2026-07-28  
> 状态：`completed_offline_no_new_forward / inference_only / attention-derived non-causal`  
> 输入：冻结的 R-027、R-028、R-029c 逐样本结果；无新 forward、无样本/head 重选。  
> 实现：`codespace/e005_adapter/posthoc_qr_curve_analysis.py`  
> 失败记录：R-034 缺少 scipy；R-034b NumPy bool subtraction；两者均在统计输出前失败。R-034c 首次完整产出；R-034d 增加 cluster/pair Spearman CI 与 ECDF/ROC 图，作为最终版本。

## 1. 分析问题与反 threshold-fishing 约束

本次不问“如何放宽 strict hit 才显著”，而问：

> Q→R 对 reference GT 的连续 attention signal，是否在不同数据、阈值、coverage 与空间指标下稳定地区分自然定位 error 与 correct？

分析前冻结：

```text
Q→R enrichment threshold τ = {.5,.75,1,1.5,2,4,8}
coverage cutoff = {all, >=2, >=4, >=8 merged tokens}
两种事件：
  density-only: enrichment > τ
  density+pointing: enrichment > τ AND raw argmax overlaps GT
两个conditioning：
  G-density-valid: G→R enrichment>1
  G-strict-valid: G→R enrichment>1 AND pointing AND coverage>=2
```

没有选择“最佳阈值”，没有用最佳 cutoff 报 accuracy。每个阈值的 CI 仅作为敏感性曲线，未做多重比较校正，不能把个别 CI 不跨0当独立确认性显著检验。

Bootstrap：`B=10000, seed=20260728`。R-028 按冻结 pair 重采样；R-027 按 LaSOT sequence cluster 重采样；R-029c 每个原始样本对应不同 sequence，因此 cluster 数等于样本数。

## 2. 数据定义

| 数据 | error | correct | 统计单元 | 说明 |
|---|---:|---:|---|---|
| R-027 enlarged640 | 48 | 177 | 67 sequences | 70 sequences×4 frames 中 accepted extremes；多frame按sequence cluster |
| R-028 matched640 | 35 | 35 | 35 frozen pairs | error/correct geometry-matched；最强的面积/几何控制 |
| R-029c original140 | 35 | 76 | 111 sequences | 原始 positive accepted extremes |

连续 IoU 关联额外纳入 partial/middle：R-027 `n=270`；R-029c `n=133`。R-028 只有两端组 `n=70`。

## 3. Q→R target mass：最稳定的信号

定义：

\[
P_{Q\to R}=\sum_i \frac{A_i}{\sum_j A_j}\,o_i
\]

其中 `o_i` 为 reference GT 对 merged-token cell 的 fractional occupancy。

### 3.1 描述统计

| 数据 | error median [Q1,Q3] | correct median [Q1,Q3] | median correct/error ratio |
|---|---:|---:|---:|
| R-027 | `.04626 [.01521,.12147]` | `.08467 [.03971,.20090]` | `1.83×` |
| R-028 | `.02317 [.00705,.10930]` | `.07415 [.02000,.12580]` | `3.20×` |
| R-029c | `.02317 [.00705,.10930]` | `.10450 [.03652,.19662]` | `4.51×` |

完整范围：

```text
R-027 error .00149–.35082；correct .00297–.56177
R-028 error .00060–.42853；correct .00295–.59223
R-029c error .00060–.42853；correct .00295–.59223
```

分布明显重叠，故不是确定性分类信号。

### 3.2 组差与不确定性

```text
R-027 enlarged640：
  median(correct)-median(error) = +.03841
  sequence-cluster bootstrap 95% CI = [-.00543,.08529]

R-028 matched640：
  paired median(correct-error) = +.03230
  pair bootstrap 95% CI = [.00604,.08811]
  mean paired difference = +.02314
  pair signs = 26 positive / 9 negative / 0 ties
  exact two-sided sign-test p = .00599

R-029c original140：
  median(correct)-median(error) = +.08133
  sequence-bootstrap 95% CI = [.02409,.11570]
```

结论：Q→R target mass 在三个分析中方向一致；原始 n140 与冻结 matched70 的 CI 不跨0，expanded n280 的组中位数差 CI 轻微跨0。它比 strict hit 更稳定。

### 3.3 区分能力：ROC AUC

以“更高 Q→R mass 预测 correct”为 score：

| 数据 | ROC AUC | 95% cluster/pair bootstrap CI | Average precision | correct prevalence |
|---|---:|---:|---:|---:|
| R-027 | `.645` | `[.522,.762]` | `.864` | `.787` |
| R-028 | `.617` | `[.492,.743]` | `.586` | `.500` |
| R-029c | `.708` | `[.594,.812]` | `.814` | `.685` |

AP 受 correct prevalence 强烈影响，不能跨数据直接比较；ROC AUC 更适合此处。AUC 仅表示关联/排序能力，不是机制证明，也没有产生可部署 cutoff。

### 3.4 与连续 IoU 的 Spearman 关联

| 数据 | n | Spearman ρ | 95% cluster/pair bootstrap CI |
|---|---:|---:|---:|
| R-027（含partial） | 270 | `.259` | `[.114,.385]` |
| R-028 extremes | 70 | `.221` | `[-.005,.447]` |
| R-029c（含partial） | 133 | `.344` | `[.180,.494]` |

这与旧 `D_abs` 结果形成重要对比：

```text
D_abs在R-027：rho=-.037，p=.576
Q→R mass在R-027：rho=.259，cluster CI[.114,.385]
```

因此，若保留 Q→R，应该优先使用**绝对 target mass**，而不是 G→R/Q→R 相对 discrepancy。

## 4. Q→R enrichment：不如 target mass 稳定

### 4.1 描述统计

| 数据 | error enrichment median | correct median | pointing error | pointing correct |
|---|---:|---:|---:|---:|
| R-027 | `3.300` | `3.683` | `.417` | `.412` |
| R-028 | `2.557` | `4.435` | `.257` | `.371` |
| R-029c | `2.557` | `2.843` | `.257` | `.355` |

Enrichment 分布重尾：例如 R-029c error mean `8.51`、correct mean `6.54`，尽管中位数 correct 更高。这说明少量 error map 可形成非常尖锐的 reference-GT density peak；“峰很尖”不等于自然定位正确。

组差：

```text
R-027 median difference = +.383，CI[-1.404,2.658]
R-028 paired median difference = +2.237，CI[-.351,4.133]
R-029c median difference = +.286，CI[-2.463,1.720]
```

ROC AUC：

```text
R-027 .549 CI[.402,.690]
R-028 .628 CI[.487,.765]
R-029c .524 CI[.396,.650]
```

连续 IoU 关联也不稳定甚至方向为负：

```text
R-027 rho=-.156 CI[-.324,.015]
R-028 rho=+.166 CI[-.070,.402]
R-029c rho=-.095 CI[-.263,.077]
```

所以 enrichment 不能取代 target mass 作为主连续指标。

## 5. Enrichment threshold curves

### 5.1 Density-only，不要求 argmax pointing

全样本 correct-error rate difference：

| τ | R-027 | R-028 matched | R-029c |
|---:|---:|---:|---:|
| .5 | +.008 | +.057 | +.059 |
| .75 | +.042 | +.143 | +.106 |
| 1 | +.112 | +.200 | +.154 |
| 1.5 | +.200 | +.200 | +.108 |
| 2 | +.112 | +.257 | +.086 |
| 4 | +.026 | +.143 | **-.058** |
| 8 | +.010 | +.143 | **-.044** |

曲线揭示了 strict hit 丢失的信息，但也揭示了限制：

1. 中等阈值 `.75–2` 中 correct 通常更常超过阈值；
2. R-028 matched 的方向最连续；
3. R-029c 在高阈值 `4/8` 发生反转，与 error 重尾一致；
4. expanded R-027 只有 `τ=1.5` 的 pointwise cluster CI 不跨0：difference `+.200`、CI `[.032,.366]`，不能在无多重校正下单独强调。

R-028 paired CIs：

```text
τ=.75: +.143 CI[.029,.257]
τ=1.0: +.200 CI[.029,.371]
τ=1.5: +.200 CI[-.029,.429]
τ=2.0: +.257 CI[.029,.486]
```

这说明 matched 数据中 moderate density threshold 的方向较一致，但不是所有阈值都稳定。

### 5.2 加入 pointing 后，差异大幅变弱

全样本 `density + pointing`：

```text
R-027：各τ correct-error约 -.007 到 +.030，全部CI跨0
R-028：τ<=4约 +.114；τ=8为+.143，全部CI跨0
R-029c：低τ约+.098，τ=4/8反转为-.005/-.029，全部CI跨0
```

因此 strict hit 的主要问题确实是 raw argmax pointing：

> Q→R 差异更像分布式 reference-target attention budget，而不是“最高单个token是否指中GT”。

但不能进一步声称“pointing条件错误”；它测的是更严格、不同的空间性质。

### 5.3 Grounding-conditioned 结果

在 G→R strict-valid 后，R-028 完整 matched pairs 为 `33`：

```text
Q→R density-only correct-error：
τ=.75  +.152 CI[.032,.290]
τ=1    +.242 CI[.097,.452]
τ=1.5  +.242 CI[.032,.484]
τ=2    +.303 CI[.065,.548]
```

R-029c G-strict-valid：error33/correct72：

```text
τ=1 difference=+.192 CI[.019,.371]
其余多数阈值CI跨0；τ>=4方向反转
```

R-027 G-strict-valid：error41/correct171：

```text
τ=1.5 difference=+.215 CI[.032,.397]
其余阈值多数CI跨0
```

Conditioning 后仍呈“moderate enrichment 更常见于 correct”，但不是宽阈值范围内单调稳定的效应。

## 6. 640 matched Q→R retained-mass fractional-token IoU 曲线

定义：按 Q→R raw attention 从高到低选取最少 token，使累计 mass 达到 `ρ∈{.05,.10,...,.95}`，将这些 token cells 与 reference GT fractional occupancy 计算 merged-token fIoU。它不是 pixel segmentation。

本次对 R-028 的 640 curves 做 pair bootstrap：

| 双侧 coverage 条件 | pairs | normalized fIoU-AUC paired median(correct-error) | 95% CI | positive/negative pairs |
|---|---:|---:|---:|---:|
| all | 35 | `.04848` | `[.00769,.07722]` | 26/9 |
| both >=2 | 33 | `.04848` | `[.00769,.07735]` | 24/9 |
| both >=4 | 26 | `.05262` | `[.01333,.07992]` | 20/6 |
| both >=8 | 12 | `.05492` | `[-.03858,.09199]` | 9/3 |

与旧 R-023 的 224 结果相比：

```text
224 both coverage>=4：paired n=15，median diff=.06795
CI[.03305,.08989]

640 both coverage>=4：paired n=26，median diff=.05262
CI[.01333,.07992]
```

方向在 640 保持，同时更高 coverage 使 eligible pairs 从15升至26。`>=8` 因只剩12 pairs，CI重新跨0。

Pointwise fIoU 差异并非每个 `ρ` 都稳定；640 coverage>=4 下较清楚的区间主要出现在：

```text
ρ=.35: mean diff=.075，CI[.003,.147]
ρ=.75: mean diff=.032，CI[.0004,.0689]
ρ=.80: mean diff=.030，CI[.0050,.0579]
```

不能选择单一最佳 `ρ`；正式结论使用预定义整条曲线的 normalized AUC。

## 7. 一个重要混杂：target mass 与 enrichment 给出不同故事

Target mass 在三个数据中更稳定地随正确性/IoU增加；enrichment 不稳定。这可能意味着：

```text
A. correct cases为reference GT分配更多总attention预算；
B. 但该预算未必形成更尖锐、更高密度的单峰；
C. target mass仍受GT token面积/coverage影响；
D. matched R-028与fIoU结果缓解但不能完全排除几何/序列长度混杂。
```

另外，R-027 与 R-029c 中 G→R target mass 也在 correct 中更高：

```text
R-027 G mass median difference=+.10287 CI[.00266,.23412]
R-029c G mass median difference=+.13057 CI[.01681,.20326]
R-028 matched G mass paired difference=.00286 CI[-.04125,.03979]
```

这表明未匹配数据中的 Q→R mass 组差可能部分反映整体“容易样本/更强target concentration”，而不完全是 output-stage binding 独有机制。冻结 matched R-028 中 G mass 无差、Q mass有差，是更干净但规模较小的证据。

## 8. 最终判断

### 得到加强的结论

1. `strict hit` 确实过于离散，尤其 argmax pointing 会丢失分布式 Q→R budget 差异。
2. Q→R **raw target mass** 是目前最稳定的 Q→R 指标：三个数据方向一致；R-028 paired与R-029c CI不跨0；R-027 ROC AUC及连续IoU相关的cluster CI不跨0。
3. R-028 的 Q→R fIoU curve AUC 在640下保持 correct>error，说明差异不仅是单一阈值产物。
4. `D_abs` 不稳定不代表 Q→R 完全无信息；问题在于把 Q→R 相对 G→R 的差作为核心指标，而不是使用绝对 Q→R strength。

### 没有得到支持的更强说法

1. Q→R enrichment 不是稳定、单调的正确性指标；高阈值可反转。
2. Q→R pointing/strict hit 不能稳定地区分 error/correct。
3. Q→R mass 不是充分分类器：ROC AUC约 `.62–.71`，分布大量重叠。
4. 不能由这些结果推断 causal binding circuit、identity selectivity 或“模型必须回看reference才能正确定位”。

### 对方法构想的影响

不建议继续把训练目标定义为单一：

```text
minimize |logit(P_G→R)-logit(P_Q→R)|
```

如果进行最小 SFT pilot，更合理但仍未验证的候选是：

```text
提高bbox-stage Q→R对reference target的pooled target mass
同时保留/约束Q→Q自然定位行为
并用CE-only continuation作对照
```

成功条件必须是：

```text
natural single-output bbox IoU / Joint F1改善
而不是只提高Q→R mass或heatmap相似度
```

在训练前，最有价值的下一步仍是 E-004 因果验证：对冻结 query-localization heads 的 Q→R/reference-span head output 做 source→base patching或受控ablation，检查自然 bbox 是否变化。

## 9. 审计路径

```text
remote final run:
/home/featurize/work/mechanism/explog/E-005/runs/
E005-R-034d-qr-continuous-threshold-curve-offline-640/

remote statistics:
.../analysis/detailed_statistics.json

local statistics and figures:
shell/06_experiments/E-005/visualizations/R-034d/
├── detailed_statistics.json
├── qr_enrichment_threshold_curves.png
└── qr_target_mass_ecdf_roc.png
```
