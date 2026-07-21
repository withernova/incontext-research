# E-003 detailed metric ledger

> 数据源：E003-R-004b与其离线审计E003-R-006。所有数值均来自正式summary/per-sample outputs；local deterministic LaSOT reconstruction，**不是官方IPLoc-ID split**。

## 数据与完整性

```text
samples/clusters = 140
classes = 70
records = 280
positive = 140
same-class negative = 140
processor failures / traceback = 0
```

## Identification-only

| 项目 | 计数 | 比例 |
|---|---:|---:|
| TP（positive回答Yes） | 133/140 | 95.00% positive recall |
| FN（positive回答No） | 7/140 | 5.00% positive FN rate |
| TN（negative回答No） | 136/140 | 97.14% negative rejection rate |
| FP（negative回答Yes） | 4/140 | 2.86% negative FP rate |
| Identification F1 | — | **0.9603** |

## Positive localization

| 口径 | Mean IoU | Median IoU |
|---|---:|---:|
| 全部140 positive | **0.5745** | 0.7414 |
| 133个identification TP | **0.5880** | 0.7441 |

133个positive identification TP中的低IoU分层：

| 阈值失败 | 计数 | 占133个identification TP |
|---|---:|---:|
| IoU < 0.1 | 35 | 26.32% |
| IoU < 0.3 | 36 | 27.07% |
| IoU < 0.5 | 44 | 33.08% |
| IoU < 0.7 | 57 | 42.86% |

这些是**定位阈值失败率**，不是wrong-instance确认率。

## Joint identification–localization

Joint定义：positive只有同时满足`Yes && IoU>=tau`才为TP；positive No或Yes但IoU不足均为FN；negative仍按Yes=FP、No=TN。

| τ | Joint TP | TN | FP | Joint FN | Joint F1 | Positive joint recall | Positive joint failure |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.3 | 97 | 136 | 4 | 43 | **0.8050** | 69.29% | 43/140 = 30.71% |
| 0.5 | 89 | 136 | 4 | 51 | **0.7639** | 63.57% | 51/140 = 36.43% |
| 0.7 | 76 | 136 | 4 | 64 | **0.6909** | 54.29% | 64/140 = 45.71% |

其中“已经回答Yes、但IoU未达阈值”的数量分别是：

```text
τ=0.3: 36/133 = 27.07%
τ=0.5: 44/133 = 33.08%
τ=0.7: 57/133 = 42.86%
```

Identification F1与各Joint F1的绝对差为0.1553/0.1963/0.2694；这是**同量纲F1口径差**，可以作为coverage-gap描述。不得用F1减mIoU。

## 完整IoU阈值曲线与bootstrap不确定性

E003-R-007离线复用同一批R-004b outputs，不重跑模型。设置：

```text
IoU threshold = 0.00..1.00, step=0.01（101点）
bootstrap = 10,000 sample-clustered replicates
cluster = 同一sample的positive + negative
seed = 20260721
```

| 指标 | 点估计 | 95% percentile CI | F1 gap vs identification | gap 95% CI |
|---|---:|---:|---:|---:|
| Identification F1 | 0.9603 | [0.9348, 0.9819] | — | — |
| Joint F1@0.3 | 0.8050 | [0.7468, 0.8583] | 0.1553 | [0.1073, 0.2077] |
| Joint F1@0.5 | 0.7639 | [0.6996, 0.8216] | 0.1963 | [0.1426, 0.2562] |
| Joint F1@0.7 | 0.6909 | [0.6161, 0.7598] | 0.2694 | [0.2051, 0.3392] |

三项gap CI均不含0。曲线与完整阈值表位于：

```text
shell/06_experiments/E-003/artifacts/
E003-R-007-joint-f1-iou-threshold-curve-bootstrap-n140/
```

这些是逐阈值pointwise CI，不是覆盖整条曲线的simultaneous confidence band。

## 低IoU视觉初筛

35个`positive Yes && IoU<0.1`案例均已生成`support + positive query`可视化：

```text
shell/06_experiments/E-003/artifacts/E003-R-006-support-positive-low-iou/
```

单人视觉初筛possible same-image wrong-instance：

```text
7/35 = 20.00%（在极低IoU可视化子集内）
7/133 = 5.26%（在identification TP内）
7/140 = 5.00%（在全部positive内）
```

这三个比例均**不是确认的wrong-instance错误率**。原因：尚无第二实例正式bbox/track ID、尚未双人复核，且样本来自outcome-conditioned低IoU筛选。

## Negative candidate行为（辅助）

```text
negative candidate mIoU = 0.5327
median IoU = 0.6706
IoU>=0.5 = 83/140 = 59.29%
其中最终No = 82/83 = 98.80%
```

这说明negative candidate localization与最终identity rejection可以行为上分离；它与sequential design相容，不是论文缺陷本身。

## 结论边界

可支持：本地重建split上identification-only F1与joint correctness明显解耦，存在joint-metric coverage gap。

不可支持：官方split具有同等幅度；低IoU全部是wrong-instance；7/35是总体错误率；verifier忽略candidate；论文F1计算错误或论文未评测定位。
