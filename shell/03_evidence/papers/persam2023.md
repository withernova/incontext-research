# [[persam2023]] — Personalize Segment Anything Model with One Shot

> source: shell/03_evidence/papers/downloads/persam2023.pdf
> content_hash: sha256:97d2853423b8e50a0082aacef1cdd99e576fc996c7dea7b4799877f846d259e3
> 未检测到 MinerU 产物；使用 PDF 文本抽取核验。

## 书目信息
- authors: Renrui Zhang, Zhengkai Jiang, Ziyu Guo, Shilin Yan, Junting Pan, Xianzheng Ma, Hao Dong, Yu Qiao, Peng Gao, Hongsheng Li
- year: 2023
- venue: ICLR 2024（论文版本需最终核对）
- doi: 10.48550/arXiv.2305.03048

## TL;DR
PerSAM几乎直接实现了“先确认reference对象内部视觉特征，再在query/test图上建立位置对应”的机制：reference mask内局部特征与test image逐位置做cosine similarity，得到confidence map，再用它引导decoder cross-attention。它是目前检索到与我们假设最接近的具体方法先例。

## 与本项目相关的关键声明
- §1 Introduction：SAM本身不能自动分割特定subject instance；PerSAM用reference image+mask做personalized segmentation。
- §3.2 Location Confidence Map：抽取reference mask内每个foreground pixel的局部特征，与test image feature逐位置计算cosine similarity；聚合所有局部部件的confidence，得到目标位置估计。
- §3.2 Target-guided Attention：用上述confidence map显式调制SAM decoder里的每个token-to-image cross-attention layer，让prompt tokens聚焦test image的foreground target区域。
- 这非常接近我们的假设链：reference内部表示质量 → reference/query correspondence map → query localization。区别是PerSAM显式构造similarity map，而我们试图在MLLM自然query heads中识别同类过程。

## 方法 / 设置
- reference image+mask得到reference foreground local features。
- 逐local feature与test feature做cosine similarity并聚合为location confidence map。
- 从map产生正/负点prompt，并用map做target-guided attention；另把target embedding融合到prompt tokens。

## 结果 / 表格
- 论文在PerSeg、one-shot segmentation和video object segmentation上评价；本轮只核验机制结构，不在未逐表核对前引用数值。

## 局限 / 效度威胁
- 使用精确/粗略mask而非bbox，reference supervision更强。
- 基于SAM视觉特征和显式similarity，不是MLLM自然attention。
- 方法成功不能证明我们的main4已经承担同一功能；反而提示应直接比较object-conditioned similarity/correspondence，而非广义residual注入。

## 可能引用的原句（附 §定位）
- §3.2: “we calculate n confidence maps for each foreground pixel i by the cosine similarity between [the reference local feature] and test image feature.”
- §3.2: “By incorporating the confidences of every foreground pixel, S can take the visual appearance of different object parts into consideration.”
- §3.2: “Target-guided Attention ... concentrates the feature aggregation within foreground target regions.”

## 对我们任意声明的反驳证据
- 它提示“query head在reference上表现差”不是唯一可行表述：更直接的失败变量可能是reference object local features与query tokens之间的显式correspondence质量；attention只是随后被该map引导的执行层。
