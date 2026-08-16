# [[mixformer2022]] — MixFormer: End-to-End Tracking with Iterative Mixed Attention

> source: shell/03_evidence/papers/downloads/mixformer2022.pdf
> content_hash: sha256:00426f22cde799fe6f12fd1800245cd92fd83f982dce2b82fce95d5eac0e644d
> 未检测到 MinerU 产物；使用 PDF 文本抽取核验。

## 书目信息
- authors: Yutao Cui, Cheng Jiang, Limin Wang, Gangshan Wu
- year: 2022
- venue: CVPR 2022
- doi: 10.48550/arXiv.2203.11082

## TL;DR
MixFormer用反复的 mixed attention 同时完成 template/search 特征提取与信息整合，目标是形成 target-specific search features。它支持“reference理解和query定位不是两个可随意拆开的阶段，而应在多层中迭代耦合”的邻近假设。

## 与本项目相关的关键声明
- §Abstract：同步 feature extraction 与 target information integration，使模型提取 target-specific discriminative features，并让 target 与 search 广泛通信。
- §1 Introduction：把 target 信息更充分整合进 search area，有利于捕获二者相关性。
- §3.1：MAM 对各自序列做 self-attention，并在 template/search 之间做 cross-attention；模型通过堆叠 MAM 渐进提取 coupled features。
- §3.1 Asymmetric MAM：作者认为 target-query→search 的反向 cross-attention 可能因 distractors 带来负面影响并可裁剪；更重要的是 search→template，即“query/search 当前表征读取reference/template”。这与我们重点审计 bbox rows 的 Q→R 在方向上高度接近。
- §4 attention visualization：作者观察到背景 distractors 随层被抑制，templates 的 foreground 之间发生交互；但这是可视化观察，不是机制因果证明。

## 方法 / 设置
- 输入 target template 和 search area 两组 tokens。
- target/search 各自 self-attention，同时执行跨序列 attention。
- 迭代堆叠 mixed-attention blocks，最后由 localization head输出框。

## 结果 / 表格
- §4 Table 4：包含 MAM framework 消融，支持联合特征提取与信息整合的有效性；本笔记暂不抄录未逐格复核的数值。
- §4 Table 5：asymmetric MAM 的 AUC 与完整版本接近，说明不是所有方向的信息流同等重要。

## 局限 / 效度威胁
- 专门训练的 tracker，不是 MLLM，也没有 autoregressive bbox token。
- target crop 干净，和整图 reference+bbox prompt 不同。
- 没有给出“某个 head 的 template alignment差→同head search alignment差→框错”的样本级中介分析。

## 可能引用的原句（附 §定位）
- §Abstract: “simultaneous feature extraction and target information integration.”
- §3.1: “It carries out self-attention on tokens in each sequence themselves... Meanwhile, it conducts cross-attention between tokens from two sequences to allow communication between target template and search area.”
- §3.1: “the cross attention from the targets query to search area is not so important and might bring negative influence due to potential distractors.”

## 对我们任意声明的反驳证据
- 成功 tracking 依赖多层 mixed attention 与训练出的 coupled features，故单次推理时 residual 注入或单层 attention shape replacement 缺乏结构依据；这支持停止把 R-006c 视为核心机制验证。
