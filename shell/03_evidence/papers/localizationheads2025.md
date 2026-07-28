# [[localizationheads2025]] — Your Large Vision-Language Model Only Needs A Few Attention Heads For Visual Grounding

> source: `shell/03_evidence/papers/localizationheads2025.pdf`
> content_hash: `sha256:14dcc4524734751f2678b3581676f4e0d01823a73f112e5b4722aa8e9c800b6c`
> content_hash 以原始 PDF 计算；以下阅读以 MinerU `.md` 为准。
> mineru_md: `papers/Your Large Vision-Language Model Only Needs A Few Attention Heads For Visual Grounding_2025/hybrid_auto/Your Large Vision-Language Model Only Needs A Few Attention Heads For Visual Grounding_2025.md`
> mineru_images: `papers/Your Large Vision-Language Model Only Needs A Few Attention Heads For Visual Grounding_2025/hybrid_auto/images`
> 引用格式：`[[localizationheads2025]] §小节`。

## 书目信息
- title: Your Large Vision-Language Model Only Needs A Few Attention Heads For Visual Grounding
- authors: Seil Kang; Jinyeong Kim; Junhyeok Kim; Seong Jae Hwang
- year: 2025
- venue: CVPR 2025（Highlight）
- arXiv: 2503.06287
- official paper page: https://openaccess.thecvf.com/content/CVPR2025/html/Kang_Your_Large_Vision-Language_Model_Only_Needs_A_Few_Attention_Heads_CVPR_2025_paper.html
- code: https://github.com/seilk/LocalizationHeads
- code HEAD checked at analysis time: `9ffe219d20ec376eb4dd14d42c54bb3299ffdb4a`

## TL;DR

论文不做 activation patching/CMA，而是直接从冻结 LVLM 的 decoder self-attention 中读取“最后一个输入文本 token → 图像 token”的逐 head attention map。通过跨样本的 image-attention sum 与 spatial entropy 两阶段统计，固定选择少数 localization heads；将 top-3 attention maps 平滑并聚合后，直接得到 pseudo-mask/bbox。该路线比 E-004 当前 CMA 更容易复现，而且已有公开代码，但它提供的是 attention-based grounding evidence，不自动等于 causal mediation evidence。

## 方法 / 设置

### 1. Attention读取位置

对每个 layer/head，使用最后一个输入文本 token `q_txt` 作为 query，取其对视觉 tokens 的注意力：

\[
a^{\ell,h}=\operatorname{softmax}(q_{txt}K^\top/\sqrt{d_h}),
\]

后续只保留视觉 token 范围。论文假设最后一个输入 token 汇总了整个文本表达。[[localizationheads2025]] §3

### 2. Criterion 1：image attention sum

\[
S_{img}^{\ell,h}=\sum_{i\in image}a^{\ell,h}[i].
\]

在 RefCOCO train 的1,000个随机 image-text pairs上，对每个head计算平均值；阈值 `τ` 取排序曲线最大曲率点。仅保留 `S_img >= τ` 的heads。论文分析排除LLM前两层。[[localizationheads2025]] §4.1

### 3. Criterion 2：spatial entropy

将视觉attention恢复为二维grid，先做 `ReLU(map - mean(map))`，对非零区域做8邻域connected components。按每个component面积占全部激活面积的比例计算Shannon entropy：

\[
H(A^{\ell,h})=-\sum_n P(C_n)\log P(C_n).
\]

低entropy表示注意力集中为少量空间簇。每个样本在通过Criterion 1的heads中选entropy最低的10个，然后统计每个head跨样本的selection frequency。最终固定选择frequency最高的top-k heads，而不是逐样本greedy选择。[[localizationheads2025]] §4.1–4.2、Appendix §B.1

### 4. Grounding输出

论文主设置 `k=3`。每张top-head map使用Gaussian smoothing（kernel 7、σ=1.0），逐元素求和并按均值二值化得到pseudo-mask；保留最大convex hull并取tight bbox。RES中该bbox还可作为SAM prompt。[[localizationheads2025]] §5、Appendix §B.2

### 5. 统计协议

- RefCOCO train，避免validation leakage；
- 每trial 1,000随机pairs；
- selection frequency重复5次并平均；
- REC指标Acc@0.5；RES/ReasonSeg指标cIoU；
- 论文使用单张A6000 48GB，仅inference，无fine-tuning。[[localizationheads2025]] Appendix §A

## 主要结果

- 在10种LVLM上固定使用3个localization heads。[[localizationheads2025]] §6.1
- top-3通常优于top-1/2，继续增加到4/5不保证提升；10个模型的RefCOCO-val RES平均值从k=1的64.5升至k=3的67.1，k=5降至58.9。[[localizationheads2025]] §6.3 Table 4
- 两个criterion必须联合使用，并且固定跨样本head selection优于per-sample greedy。LLaVA-1.5-13B上联合+fixed为REC 87.2 / RES 76.1；仅attention-sum fixed为23.9/19.3，仅entropy fixed为31.3/25.7。[[localizationheads2025]] §6.3 Table 5
- LLaVA-1.5-7B：REC RefCOCO val 86.5，RES RefCOCO val 74.2；LLaVA-1.5-13B分别87.2和76.1。[[localizationheads2025]] §6.1 Tables 1–2
- 论文展示LLaVA-1.5-7B的例子head L14H24、L14H13；附录展示LLaVA-1.5-13B的三个heads L15H39、L16H30、L7H2。模型间head编号不可直接迁移。[[localizationheads2025]] §1 Fig.1、Appendix Fig.17–18

## 与 E-002/E-003/E-004 的关系

### 可直接借鉴

1. 用attention sum筛掉几乎不读取视觉信息的heads；
2. 用spatial entropy和跨样本selection frequency筛选稳定空间定位heads；
3. 使用fixed heads而非per-sample greedy，避免只找到任意低熵簇；
4. 将head attention map与reference/query object token regions做显式可视化和IoU审核；
5. 将localization-head ranking与E-004 identification CMA/MF ranking比较，形成localization–identification circuit overlap诊断。

### 不能直接替代

- raw attention不是causal effect；selection frequency高不证明该head对输出必要或中介removed-object信息；
- 论文任务是single-image referring expression grounding，不是in-context personalized identity matching；
- 论文读取最后一个输入文本token；E-003/E-004 prefix-conditioned verifier的候选bbox和`Yes/No` autoregressive history需要重新定义query token位置；
- Qwen3-VL使用动态视觉grid、merged tokens、GQA和deepstack，不满足论文简化的固定`P×P`视觉序列假设；必须审计每张图像span与二维grid映射；
- attention实现需要eager/output-attentions路径；当前Qwen inference backend未必直接返回逐headweights。

因此建议把它作为一个新的、独立边界的实验：

```text
E-005：attention-derived localization-head discovery and grounding audit
E-004：source→base causal mediation / identity routing
```

E-005可以更容易复现并提供候选head，但不能把E-005的attention ranking冒充E-004的CMA ranking。

## 局限 / 效度威胁

- 论文承认multi-object grounding尚未形成正式pipeline。[[localizationheads2025]] Appendix §G
- 对pooling或不保留空间顺序的LVLM不适用；需要反推视觉token顺序。[[localizationheads2025]] Appendix §G
- low spatial entropy本身不保证text semantics；这正是greedy方案较差的原因。[[localizationheads2025]] §6.3
- head发现依赖RefCOCO train的1,000样本统计，不能只在当前6个strict proxy pairs上选择并宣称稳定head。
- 公开仓库当前README描述了标准HF `output_attentions=True`、eager attention和pipeline，但代码版本晚于论文提交；正式复现应固定commit并审计其与论文公式/附录的一致性。

## 可引用原句

- “Thus, we posit that the query vector of the last input text token qtxt serves as a representative query for the whole sentence.” [[localizationheads2025]] §3
- “Among these heads, we calculate the frequency with which each head exhibits the 10-lowest spatial entropy across the samples...” [[localizationheads2025]] §4.2
- “The greedy selection method shows worse results than the fixed method.” [[localizationheads2025]] §6.3

## 对当前想法的反驳/修正证据

该论文表明：少数head的raw attention本身可能已包含强定位信号，因此“必须先依赖复杂source→base CMA才能发现所有有意义head”过强。更合理的分工是：attention criteria用于低成本候选发现和空间定位输出，CMA/ablation用于后续因果验证。另一方面，它也不能反驳E-004，因为论文没有证明localization heads对identity verification输出具有causal mediation作用。
