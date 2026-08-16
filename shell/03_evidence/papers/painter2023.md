# [[painter2023]] — Images Speak in Images: A Generalist Painter for In-Context Visual Learning

> source: shell/03_evidence/papers/downloads/painter2023.pdf
> content_hash: sha256:e2091bf3cac6046bf701bffd89bac9c42d06fe9579ed5bf3d62ab3311245e4d9
> 未检测到 MinerU 产物；使用 PDF 文本抽取核验。

## 书目信息
- authors: Xinlong Wang, Wen Wang, Yue Cao, Chunhua Shen, Tiejun Huang
- year: 2023
- venue: CVPR 2023
- doi: 10.48550/arXiv.2212.02499

## TL;DR
Painter将输入/输出示例直接作为视觉prompt，并用masked image modeling训练模型依赖可见示例patch。它提供视觉in-context学习的广义先例，但主要学习“任务是什么”，未直接研究reference对象身份到query对象的对应失败。

## 与本项目相关的关键声明
- §1 Introduction：训练让模型的预测 conditioned on visible image patches；推理时用同任务input/output pair指示要执行的任务。
- §3.2：将同任务的两张输入图和对应输出拼接，以MIM预测被mask的输出；context不是额外加到residual的外部信号，而是共同参与原始forward。
- 这支持我们把自然联合计算作为主要分析对象，不应以事后residual rescue替代reference-understanding检验。

## 方法 / 设置
- 把深度、语义/实例分割、关键点和恢复任务输出统一成3通道“图像”。
- 拼接同任务示例，遮挡输出patch并重建。
- inference用输入/输出pair作为task prompt。

## 结果 / 表格
- §4报告多个in-domain与out-of-domain任务；本项目只采用其机制设计事实，不据此引用具体benchmark数值。

## 局限 / 效度威胁
- 示例主要规定任务/输出映射，不一定规定跨图实例身份。
- 不是MLLM，也没有bbox token query heads。
- 论文未进行head-level causal mediation。

## 可能引用的原句（附 §定位）
- §Abstract: “This makes the model capable of performing tasks conditioned on visible image patches.”
- §1 Introduction: “we directly use the input/output paired images from the same task as the input condition to indicate which task to perform.”

## 对我们任意声明的反驳证据
- Painter的成功不能直接证明MLLM已理解reference object；其prompt包含明确输出示例并经过专门in-context训练，条件更强。
