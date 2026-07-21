# E-003 · 评测审计成立依据与证据链

> 本文件回答：为什么 E-003 是一个成立的评测审计、它具体审计论文的哪一处覆盖缺口，以及现有结果能否被表述为“论文存在缺漏”。

## 1. 被审计对象不是论文的模型能力，而是任务定义与指标口径的对应关系

IPLoc-ID 将 POIL 的理想输出定义为：positive query 返回目标实例的正确 bbox，negative query 返回 rejection：

\[
f^*(x)=\begin{cases}
B^t,&\delta(x)=1\\
\varnothing,&\delta(x)=0.
\end{cases}
\]

这意味着 positive 的端到端成功同时要求：

1. identification 接受该 query；
2. localization 找到目标实例的位置。

论文的方法叙述也把生成 bbox 称为 reference-conditioned candidate，并声称后续 identification component 判断该 candidate 是否对应 reference instance。[[personal2026]] §3.1.1 Personalized object identification and localization；[[personal2026]] §3.3.1 Sequential generation of localization and identification

但论文的 evaluation metric 小节只说明分别使用 mIoU 测量 bbox localization、F1 测量 instance identification；实验设置也继续分别报告二者。[[personal2026]] §3.1.2 Evaluation metric for POIL；[[personal2026]] §4.1.2 Evaluation procedure

因此 E-003 审计的准确表述是：

> **论文已分别测量两个 component，但未在已读取正文中报告一个要求“positive identification 与 localization 同时正确”的 joint end-to-end metric。**

这是一项 metric coverage gap，而不是“论文没有评测 localization”、不是“F1 算错”，也不是研究不端指控。

## 2. 为什么不能用 F1 与 mIoU 的数值差代替

F1 与 mIoU 的统计对象和量纲不同：

- identification F1 来自 positive/negative decision 的 TP/FP/FN；
- mIoU 是 bbox overlap 的连续均值；
- 二者不可直接相减后解释为“多少比例错误推理”。

此外，分别较高的 component metrics 也不保证同一 positive sample 上同时成功。例如，一批定位正确样本与一批 identification 正确样本可以部分错开。

所以需要在 per-sample prediction 上构造 joint event，而不是比较两个汇总数。

## 3. E-003 的 joint metric 定义

对每个 positive query，给定 identification decision \(\hat y\)、预测框 \(\hat B\)、GT \(B^*\) 和阈值 \(\tau\)：

\[
\mathrm{TP}_{\tau}=\mathbb{1}[y=1,\hat y=1,\mathrm{IoU}(\hat B,B^*)\ge\tau].
\]

计数规则：

- positive + Yes + IoU≥τ：joint TP；
- positive + No：joint FN；
- positive + Yes + IoU<τ：**joint FN**，因为端到端目标没有完成；
- negative + Yes：joint FP；
- negative + No：joint TN。

随后：

\[
F1_{joint,\tau}=\frac{2TP_\tau}{2TP_\tau+FP+FN_\tau}.
\]

预先报告 \(\tau\in\{0.3,0.5,0.7\}\)，避免只选择最有利阈值。该指标是对论文 component metrics 的补充，不替代 mIoU、identification F1、positive recall 或 negative FPR。

## 4. E-003 的三层证据链

### L1 · 指标覆盖审计

问题：identification-only F1 是否高估同一样本上的 joint success？

所需证据：完整 positive/negative records、Yes/No、positive GT/pred bbox、per-sample IoU、Joint F1@多阈值。

当前主证据：`E003-R-004b`。

### L2 · 结果有效性审计

问题：低-IoU identification TP 是否来自真实定位失败，而非坐标转换、bbox格式、annotation/frame 对齐或 parser bug？

所需证据：低-IoU逐例重新解析、坐标转换复算、GT/frame核对和可视化。

`E003-R-006-rejection-linked-bbox-audit-n140` 已完成第一阶段：140 pairs重算、35个IoU<0.1 TP可视化、paired rejected-query geometry对照。未发现positive错误框与paired negative prediction/annotation在归一化geometry上特别接近；paired距离方向上反而更大。该结果排除了一个简单的“跨图像paired bbox geometry复制”解释，但尚未完成positive图像内wrong-instance/object-part/background的正式人工taxonomy。

### L3 · candidate-verification 机制诊断

问题：论文所述 \(p(A\mid x,B,Q)\) 是否会随 candidate region 改变？

所需证据：固定 reference/query，只改变 assistant autoregressive history 中的 candidate；比较 constrained `Yes` vs `No` logits。

计划/失败链：`R-005`–`R-005e`。这是 prefix-conditioned verifier probe，存在 exposure shift；即使 candidate 不敏感，也不能单独证明自然生成路径完全忽略 bbox。

## 5. 当前实证为什么足以支持“存在评测覆盖缺口”

`E003-R-004b` 在同一份 per-sample outputs 上得到：

```text
Identification F1        = 0.9603
Joint F1 @ IoU>=0.3      = 0.8050
Joint F1 @ IoU>=0.5      = 0.7639
Joint F1 @ IoU>=0.7      = 0.6909
```

完整性：280 records，140 positive + 140 negative。133 个 identification TP 中，44 个 IoU<0.5；它们在 identification-only 口径下是 TP，在 Joint@0.5 中是 FN。

这直接证明：

> 在该本地 deterministic LaSOT POIL reconstruction 上，回答 Yes 的正确性与 bbox 定位正确性并不等价；identification-only F1 高于 joint end-to-end success。

## 6. 为什么当前还不能强称“Personal 论文结论错误”

当前 E-003 不满足官方复现等价性：

- manifest 是根据本地 LaSOTTesting 确定性重建，不是论文官方 JSON/split；
- 当前只审计 Qwen3-VL-8B、1-shot、单次 checkpoint/run；
- 论文通常报告三次独立训练/评测平均，而本 run 不是三训练 seed 复现；
- 尚未完成低-IoU coordinate/annotation audit；
- 尚未在论文四个数据集与 N={1,2,4,8} 全范围重复；
- forced candidate 是分布外 prefix intervention。

所以当前分级结论是：

1. **已证实（本地设置）**：identification-only F1 与 joint correctness 明显解耦；
2. **正文覆盖审计**：已读取论文正文分别报告 mIoU/F1，未发现 Joint F1–IoU；
3. **尚未证实（官方设置）**：论文表格中的具体 F1 在官方 split 上以同等幅度高估 joint success；
4. **尚未证实（机制）**：verifier 忽略 candidate，或模型依赖 background/category/container shortcut。

推荐正式措辞：

> The reported identification-only F1 does not, by itself, establish end-to-end POIL success because it does not require the accepted positive candidate to be correctly localized. On our deterministic local LaSOT reconstruction, this distinction is substantial.

避免措辞：

```text
论文造假
F1 是假的
论文完全没有评测定位
模型完全不看 candidate
```

## 7. 要把“本地覆盖缺口”升级为“论文级稳健缺漏”还需要什么

最低升级条件：

1. 获得官方 test manifests 或作者确认的数据生成配置；
2. 原 checkpoint/公开权重和官方 parser 下复算 per-sample joint metrics；
3. 至少覆盖论文主表对应的 LaSOT setting，最好覆盖其他 datasets/N-shot；
4. 低-IoU cases 完成坐标、annotation、frame 和 visualization audit；R-006已完成bbox/path/threshold与35张可视化的自动审计，但positive图像内多实例语义标签仍待补；
5. sample-clustered paired bootstrap CI；
6. 明确区分“论文没有报告该指标”与“按该指标模型表现下降”；
7. 若主张 candidate verifier 缺陷，再加入自然生成 history 与 forced-prefix 的 matched controls。

## 8. 审核入口

```text
论文正文：
papers/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026/hybrid_auto/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026.md

数据与主结果：
shell/06_experiments/E-003/runs/E003-R-001-data-rehydrate-local-lasot-n140.md
shell/06_experiments/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128.md
shell/06_experiments/E-003/result.md

后续有效性与机制协议：
shell/06_experiments/E-003/detailed_protocol.md
```
