# [[seggpt2023]] — SegGPT: Segmenting Everything In Context

> source: shell/03_evidence/papers/downloads/seggpt2023.pdf
> content_hash: sha256:7e97099e679541b948b7c7390575fd08c3d9a28f6992b8f18d96b1e7c60830a0
> 未检测到 MinerU 产物；使用 PDF 文本抽取核验。

## 书目信息
- authors: Xinlong Wang, Xiaosong Zhang, Yue Cao, Wen Wang, Chunhua Shen, Tiejun Huang
- year: 2023
- venue: ICCV 2023
- doi: 10.48550/arXiv.2304.03284

## TL;DR
SegGPT通过训练目标强制模型依赖上下文示例，并在每层让query feature聚合reference examples。它提示：若希望reference真正决定query输出，关键通常不是事后注入，而是训练目标和逐层context integration。

## 与本项目相关的关键声明
- §1 Introduction / §3.1：随机颜色映射使固定颜色无法泄露任务，迫使模型参考contextual information完成对应区域预测。
- §3.1：构造共享同一context（同类别或同实例）的样本；同色可表示同类别或同实例。
- §3.2 Context Ensemble：feature ensemble在每个attention layer后平均query features，使query聚合所有reference examples。
- 这与我们的假设相容：query侧输出质量取决于是否从reference提取并整合了正确对应关系；但SegGPT没有分析MLLM query heads，也不能直接支持我们的自然attention中介链。

## 方法 / 设置
- 把多种segmentation统一为in-context coloring。
- 随机重映射颜色，抑制不看reference的捷径。
- reference示例和query共同输入；多示例时可做feature ensemble。

## 结果 / 表格
- §4.5 Table（context ensemble）：1-shot与多例feature ensemble有报告；具体值需按正式表头进一步核验，不在此扩张结论。

## 局限 / 效度威胁
- 密集视觉模型而非语言自回归MLLM。
- 通常有明确mask prompt，reference信号远强于bbox文本。
- 随机颜色训练本身已明确约束reference dependence；现有IPLoc-ID SFT未必具备等价约束。

## 可能引用的原句（附 §定位）
- §1 Introduction: “the model is forced to reference contextual information to complete the assigned task.”
- §3.2: “the feature ensemble strategy averages features of the query image after each attention layer so that the query image aggregates all the reference examples.”

## 对我们任意声明的反驳证据
- 它反驳“只要存在reference token，冻结模型自然就应学会正确使用”的隐含前提：SegGPT是通过专门随机化训练目标明确强迫context dependence的。
