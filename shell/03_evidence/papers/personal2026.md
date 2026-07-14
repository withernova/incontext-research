# [[personal2026]] — Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models

> source: `papers/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026/hybrid_auto/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026.md`
> mineru_md: `papers/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026/hybrid_auto/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026.md`

## 七问细读（survey-tool 管理）

### ① 解决了什么问题？
论文指出 IPLoc/POL 假设 query image 一定包含 reference object，因此 localization-only 方法在 negative query 上仍会输出 bbox，导致实际检索/视频 grounding 场景中的 false positives。论文提出 POIL：query 可能包含或不包含 reference instance，模型需要 positive 时定位、negative 时拒绝。见 [[personal2026]] §1 Introduction, §3.1.1。

### ② 默认了哪些前提？
- 目标是 reference-conditioned instance-level localization，而不是 category-level FSOD。
- 输入包含 N 个 reference images、label、reference bbox，以及 target image 和 label。
- 数据来自 video/tracking-style public datasets，可从同一 sequence 采 reference/positive query，并从不同 instance 采 negative query。见 [[personal2026]] §3.5。

### ③ 相比已有工作的创新点？
- 将 POL 扩展为 POIL，显式加入 negative-query rejection。
- 提出 IPLoc-ID：先生成 candidate bbox，再通过 fixed self-posed query 生成 Yes/No identification answer。
- 构造基于 LaSOT、PDM/BURST、GOT-10K、VastTrack 的 POIL 数据集。见 [[personal2026]] §3.3, §3.5。

### ④ 实验是否足够支持结论？
论文报告 mIoU 与 F1，并指出 localization-only IPLoc 的 F1 接近 balanced setting 下 all-positive 的理论基线约 0.667；IPLoc-ID 大幅提升 F1，同时 mIoU 接近 IPLoc。主要表格包括 Table 3 与 Table 8-11。见 [[personal2026]] §4.1.2, §4.4。

### ⑤ 可能的反例？
- 如果 negative query 多为 out-of-class，rejection 可能退化为类别识别；因此 in-class negative（LaSOT/VastTrack）更关键。
- 当前设置每个 query 只关注单个 object，不处理多目标同时定位与识别。论文也在 limitation 中承认。见 [[personal2026]] §5。

### ⑥ 审稿人会提哪些质疑？
- 官方训练代码和额外模型是否完全开放；论文称 inference code、dataset construction scripts、minimal trained models 在 GitHub，training code/additional models upon acceptance。见 [[personal2026]] Data and code availability。
- reproduced IPLoc 与原始 IPLoc 不完全一致，论文也承认原 IPLoc 完整训练配置未公开。见 [[personal2026]] §4.1.1。
- POIL 是否过度依赖 video dataset 的 sequence/subclass 结构。

### ⑦ 扩展方向 → Idea
对本项目最直接的 E-002：使用 POIL positive/negative protocol 评估 Rex-Omni/ICOL 模型是否真的做 instance-level matching。若 localization-only baseline 在 in-class negatives 上仍高 false-positive，而 self-posed/identification objective 能降低 false-positive，则可把研究重点从“内部 token 排列”转向“reference-conditioned identification/rejection”。

## 图片标注（survey-tool 管理）
- Figure 1：展示 positive/negative query 下不同方法行为；localization-only 方法容易在 negative query 上 false-positive。
- Figure 2：POIL 数据构造与 IPLoc-ID 框架：reference + positive/negative query；bbox candidate + self-posed query + answer。
- Table 2：LaSOT/PDM/GOT-10K/VastTrack 定制数据集规模与 negative 类型。
- Table 8-11：各数据集 mIoU/F1 主结果。
