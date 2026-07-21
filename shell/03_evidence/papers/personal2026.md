# [[personal2026]] — Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models

> source: `papers/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026/hybrid_auto/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026.md`
> mineru_md: `papers/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026/hybrid_auto/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026.md`

## 七问细读（survey-tool 管理）
### ① 解决了什么问题？
论文指出 IPLoc/POL 假设 query image 一定包含 reference object，因此 localization-only 方法在 negative query 上仍会输出 bbox，导致实际检索/视频 grounding 场景中的 false positives。论文提出 POIL：query 可能包含或不包含 reference instance，模型需要 positive 时定位、negative 时拒绝。见 [[personal2026]] §1 Introduction, §3.1.1。

### ② 方法具体怎么做？
输入：
输出：

训练阶段：
推理阶段：

核心流程：
输入 → 步骤1 → 步骤2 → 步骤3 → 输出

关键模块：
- 模块1：作用
- 模块2：作用
- 模块3：作用

（基于 [[personal2026]] § / Fig 补充）

### ③ 真正的创新点是什么？
- 将 POL 扩展为 POIL，显式加入 negative-query rejection。
- 提出 IPLoc-ID：先生成 candidate bbox，再通过 fixed self-posed query 生成 Yes/No identification answer。
- 构造基于 LaSOT、PDM/BURST、GOT-10K、VastTrack 的 POIL 数据集。见 [[personal2026]] §3.3, §3.5。

### ④ 实验说明了什么？
论文报告 mIoU 与 F1，并指出 localization-only IPLoc 的 F1 接近 balanced setting 下 all-positive 的理论基线约 0.667；IPLoc-ID 大幅提升 F1，同时 mIoU 接近 IPLoc。主要表格包括 Table 3 与 Table 8-11。见 [[personal2026]] §4.1.2, §4.4。

### ⑤ 依赖哪些前提，边界在哪里？
#### 成立前提
- 目标是 reference-conditioned instance-level localization，而不是 category-level FSOD。
- 输入包含 N 个 reference images、label、reference bbox，以及 target image 和 label。
- 数据来自 video/tracking-style public datasets，可从同一 sequence 采 reference/positive query，并从不同 instance 采 negative query。见 [[personal2026]] §3.5。

#### 反例与失效边界
- 如果 negative query 多为 out-of-class，rejection 可能退化为类别识别；因此 in-class negative（LaSOT/VastTrack）更关键。
- 公开manifest中的negative与positive是不同query image：LaSOT/VastTrack来自不同sequence/sub-class，PDM/GOT-10K来自不同class。因而它没有显式构造“同一positive图像包含target和同类distractor，但candidate落到distractor”的counterfactual。
- 当前设置每个 query 只关注单个 object，不处理多目标同时定位与识别。论文也在 limitation 中承认。见 [[personal2026]] §3.5.1–§3.5.3, §5。
- 需要区分作者承认的multi-target limitation与更窄的single-target multi-instance binding问题：后者仍只要求输出一个target，但必须在同图多个同类实例间绑定正确identity；原文没有直接分析`Yes + wrong-instance bbox`或candidate-answer consistency。

### ⑥ 作为审稿人，最关键的质疑是什么？
- 形式上answer建模为`p(A|x,B,Q)`并被描述为验证candidate B，但ground-truth `A*(x)`由query是否包含reference instance的`δ(x)`决定。公开数据没有显式训练/评估“图像含target A、candidate却指向同类B、答案应No”的冲突cell。因此identification F1可能主要刻画query-level acceptance/rejection，而不能完整刻画candidate-bound instance discrimination。见 [[personal2026]] §3.1.1, §3.3.1–§3.3.2, §3.5。
- 官方训练代码和额外模型是否完全开放；论文称 inference code、dataset construction scripts、minimal trained models 在 GitHub，training code/additional models upon acceptance。见 [[personal2026]] Data and code availability。
- reproduced IPLoc 与原始 IPLoc 不完全一致，论文也承认原 IPLoc 完整训练配置未公开。见 [[personal2026]] §4.1.1。
- POIL 是否过度依赖 video dataset 的 sequence/subclass 结构。

### ⑦ 对当前项目有什么启发？
对本项目最直接的 E-002：使用 POIL positive/negative protocol 评估 Rex-Omni/ICOL 模型是否真的做 instance-level matching。若 localization-only baseline 在 in-class negatives 上仍高 false-positive，而 self-posed/identification objective 能降低 false-positive，则可把研究重点从“内部 token 排列”转向“reference-conditioned identification/rejection”。


## 图片标注（survey-tool 管理）
- [[]]  | src:  | boxes: [] | note: 
- [[]]  | src:  | boxes: [] | note: 
- [[]]  | src:  | boxes: [] | note: 
- [[]]  | src:  | boxes: [] | note: 
