# E003-R-006 · Rejection-linked low-IoU bbox audit（人工解释补充）

> 结构化 registry note：`E003-R-006-rejection-linked-bbox-audit-n140.md`。本文件保存不会被 survey-tool 重写的结果解释。

## 问题

对 R-004b 中回答 Yes 但定位失败的 positive cases，检验其预测框是否与同一 sample 中本应拒绝的 same-class negative query 上的：

1. 模型自然生成 candidate bbox；
2. annotated distractor bbox；

在各自图像归一化到 `[0,1]^2` 后特别接近。

## 设计

- source：R-004b 280 records，140 positive/negative pairs；
- 主距离：normalized `xyxy` corner RMSE，越低越近；
- 辅助：unit-canvas IoU、center/shape/area；
- control：同类别另一 reconstructed sample 的 negative box；每类恰有2 samples，因而是within-class swap；
- 10,000次class-stratified pairing permutation；
- 10,000次sample bootstrap；seed=20260720；
- 分析全部140 positive、133 identification TP、44个TP且IoU<0.5、35个TP且IoU<0.1；
- 为35个IoU<0.1 cases生成 reference/positive/reject 三联图。

跨图像的 unit-canvas overlap 只表示 layout/scale geometry，不表示两个图像中的对象真实重叠或身份相同。

## 完整性

```text
source records=280
paired samples=140
errors=0
IoU<0.1 identification TP=35
IoU<0.5 identification TP=44
visualizations=35
0.1/0.5 threshold membership disagreement=0
```

Attempt-001错误使用整数化pixel bbox复算IoU；attempt-002发现两例odd-width/resize路径存在不超过0.00112的数值差。两次失败日志均远端保留。Attempt-003使用raw float bbox，要求差异≤0.002且预注册阈值归属完全一致，最终通过。

## 主结果：原假设未获支持

### IoU<0.1 identification TP（n=35）

| 目标 | paired RMSE | same-class control RMSE | paired-control | paired更近比例 | permutation p(lower) |
|---|---:|---:|---:|---:|---:|
| negative prediction | 0.2880 | 0.2527 | +0.0353 | 0.400 | 0.9180 |
| negative annotation | 0.2924 | 0.2772 | +0.0152 | 0.429 | 0.6637 |

若原假设成立，应看到 paired RMSE 更低、delta为负、`p(lower)`较小。实际没有出现；方向上 paired box 甚至平均更远。

### IoU<0.5 identification TP（n=44）

```text
paired negative prediction: delta=+0.0450, paired-closer=0.341, p(lower)=0.9777
paired negative annotation: delta=+0.0303, paired-closer=0.341, p(lower)=0.8391
```

全样本与全部identification TP也同样没有“paired更近”的证据。

因此当前结论是：

> 在跨图像归一化bbox geometry层面，低IoU positive错误框没有表现出与其paired rejected-query bbox特别接近的证据。

这是否证了“完全没有identity confusion”？没有。geometry不是视觉特征或身份相似度；positive图像内的wrong-instance还需要多实例annotation或人工semantic labels。

## 更重要的辅助观察

Negative queries的candidate localization：

```text
negative generated candidate IoU>=0.5: 83/140
其中最终回答No:                    82/140
negative candidate mean IoU:         0.5327
median IoU:                          0.6706
```

在35个极低IoU positive TP对应的paired negatives中：

```text
negative No:                         33/35
negative candidate IoU>=0.5:         16/35
negative No && candidate IoU>=0.5:   15/35
```

这说明模型经常能够在negative query中先框住那个同类别、但不是reference identity的对象，然后回答No。它表明candidate generation/localization与identity rejection在行为上是可分的，也与论文的sequential design相容。

因此它不能被写成论文缺陷本身。更准确的含义是：

- negative上的No不是简单因为“没框到任何对象”；
- identification component可能确实有一定same-class instance rejection能力；
- positive低IoU failure更可能需要在positive图像内部检查wrong-instance selection，而不是寻找跨图像坐标复制；
- 论文仍缺少`accepted positive candidate必须定位正确`的joint metric，因为negative rejection能力并不消除positive localization failures。

## 可视化初看（非正式语义标注）

35张contact sheets显示不少positive低IoU框落在同一图像中的另一个同类实例或邻近实例，例如多目标 cattle、elephant、person、zebra、train 等；也存在背景、局部、错误尺度与明显类别定位失败。该观察尚未按预注册人工taxonomy双人审核，不能作为正式计数。

这提示下一步比跨图像geometry更直接：

1. 在positive query内部标注所有same-class instances；
2. 计算prediction对target GT与non-target same-class boxes的IoU；
3. 定义`wrong-instance hit`：target IoU<τ且某non-target IoU≥τ；
4. 将其与object-part/background/container/coordinate-suspect分开；
5. 再对target box、wrong-instance box和background做forced-candidate Yes/No logit probe。

## 审核入口

```text
remote:
/home/featurize/work/mechanism/explog/E-003/runs/E003-R-006-rejection-linked-bbox-audit-n140/
  config/run.md
  logs/attempt-001-failed-rounded-box-iou.log
  logs/attempt-002-failed-overstrict-iou-tolerance.log
  logs/run.log
  analysis/summary.json
  analysis/summary.md
  results/per_sample_geometry.json
  visualizations/manifest.json
  visualizations/sample-*.png
  manifests/provenance.json

local:
shell/06_experiments/E-003/artifacts/E003-R-006-rejection-linked-bbox-audit-n140/
```
