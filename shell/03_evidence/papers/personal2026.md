# [[personal2026]] — Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models

> source: `papers/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026/hybrid_auto/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026.md`
> mineru_md: `papers/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026/hybrid_auto/Personalized Object Identification and Localization via In-Context Inference with Vision-Language Models_2026.md`

## 七问细读（survey-tool 管理）
### ① 解决了什么问题？
**事实。** 论文研究 reference-conditioned 的实例级目标定位：输入若干带框参考图像和类别标签，模型需要在 query image 中找到与参考图像属于同一具体实例的对象，而不是找到任意同类别对象。传统 OD/FSOD 主要解决类别级检测，不能保证区分同类别的不同实例。[[personal2026]] §1 Introduction, §2 Related Works, §3.1.1 Personalized object identification and localization

**事实。** 现有 IPLoc 将 query image 默认限定为正样本，输出空间中只有 bounding box；即使 query 中没有参考实例，它仍必须生成一个框，因而会在图像检索、视频 grounding 等包含大量无关图像的场景中产生 false positives。[[personal2026]] §1 Introduction, §3.2.2 Limitation of IPLoc

**事实。** 论文将任务扩展为 personalized object identification and localization（POIL）：当 query 中存在参考实例时输出其 bounding box；不存在时输出拒绝符号 $\varnothing$。其理想映射为 $f^*(x)\in\mathcal{B}\cup{\varnothing}$，由 query 是否包含同一实例的条件 $\delta(x)$ 决定。[[personal2026]] §3.1.1 Personalized object identification and localization

**推断。** 论文真正试图修复的不是单纯的定位误差，而是 localization-only formulation 无法表达“目标不存在”的结构性缺陷。其核心研究问题可概括为：如何让 VLM 在保持 reference-conditioned localization 能力的同时，学习实例级接受或拒绝决策。[[personal2026]] §3.2.2 Limitation of IPLoc, §3.3 The Proposed IPLoc-ID

---

### ② 方法具体怎么做？
#### 输入

输入为：

$$
x=\left\{(I_k^{\mathrm r},\ell,B_k^{\mathrm r})\right\}_{k=1}^{N},I^{\mathrm t},\ell
$$

其中包含 $N$ 张 reference images、对应的类别标签和 reference bounding boxes，以及一张 target/query image 和 query label。测试时不更新模型参数，reference data 仅作为 in-context information。[[personal2026]] §3.1.1 Personalized object identification and localization, §3.3.2 Fine-tuning with positive and negative examples

#### 输出

IPLoc-ID 生成一个连续的自回归文本序列：

$$
y=\langle B\rangle\langle Q\rangle\langle A\rangle
$$

其中：

* $\langle B\rangle$：query image 中的候选 bounding box；
* $\langle Q\rangle$：固定的 self-posed query；
* $\langle A\rangle$：`Yes` 或 `No` 的 identification answer。

解释器随后将该文本转换为结构化结果：答案为正时输出候选框 $B$，答案为负时输出 $\varnothing$。[[personal2026]] §3.3.1 Sequential generation of localization and identification, §3.3.3 Interpretation of generated results

#### 训练阶段

**事实。**

1. 使用 LoRA 对自回归 VLM 进行参数高效微调，主干参数冻结，只优化低秩更新参数。[[personal2026]] §3.4 Implementation of IPLoc-ID
2. 训练目标联合优化 bounding-box generation、固定 self-posed query generation 和 identification answer generation，而不是先训练定位、再单独训练识别。[[personal2026]] §3.3.2 Fine-tuning with positive and negative examples
3. 正样本中，$B^{\mathrm t}$ 是参考实例在 query 中的真实框，答案为 `Yes`。负样本中，$B^{\mathrm t}$ 是 query 中“最合理候选对象”的真实框，答案为 `No`；因此负样本仍要求模型先定位一个候选对象，再拒绝该候选。[[personal2026]] §3.3.2 Fine-tuning with positive and negative examples
4. 训练集来自 LaSOT，共 700 个 paired samples；每个 sample 共享同一组 reference data，并产生一个 positive query 和一个 in-class negative query，即共 1,400 个独立 query cases。[[personal2026]] §3.5 Datasets for the POIL task, §3.5.2 Training set
5. 继承 IPLoc 的 pseudo-label label noise：训练时随机将类别名替换为伪标签，以降低模型对具体类别名称的依赖，促进基于参考图像和框进行匹配。[[personal2026]] §3.2.1 Formulation of IPLoc, §4.3.4 Ablation on loss terms with label noise
6. 对 $N=1,2,4,8$ 分别训练独立模型，而不是使用一个模型适配任意 reference 数量。[[personal2026]] §3.5.4 N-shot settings

#### 推理阶段

1. 根据 reference context 和 query image 生成候选框 $B$。
2. 在输出序列中接入固定问题：`Do all these boxes have the same object?`
3. 基于输入、候选框和固定问题生成 `Yes` 或 `No`。
4. 解释器检测生成文本中的答案与 bounding box：出现 `No`、`Not found`、`different`、`not the same` 等否定表达，或没有有效框时，判定为 negative；否则判定为 positive。
5. positive 返回候选框，negative 返回拒绝结果。[[personal2026]] §3.3.1 Sequential generation of localization and identification, §3.3.3 Interpretation of generated results, §3.4 Implementation of IPLoc-ID

#### 核心流程

reference images、labels、reference boxes 与 query image
→ reference-conditioned candidate localization
→ 固定 self-posed query
→ `Yes/No` instance identification
→ interpreter
→ bounding box 或 rejection

#### 关键模块

* **候选框生成模块：** 延续 IPLoc 的 sequence-completion 机制，但将 bounding box 从最终结果重新解释为待验证候选。[[personal2026]] §3.2.1 Formulation of IPLoc, §3.3 The Proposed IPLoc-ID
* **Self-posed query：** 作为候选框与 identification answer 之间的固定语言桥梁，不承担额外随机决策。[[personal2026]] §3.3.1 Sequential generation of localization and identification
* **Identification answer：** 在候选框已经生成后输出 `Yes/No`，决定接受还是拒绝。[[personal2026]] §3.3.1 Sequential generation of localization and identification
* **Unified objective：** 在同一训练目标中保持定位与识别能力，避免两阶段训练导致定位能力灾难性遗忘。[[personal2026]] §3.3.2 Fine-tuning with positive and negative examples, §4.3.1 Unified objective vs. two-stage training
* **Interpreter：** 将自由文本输出规范化为 POIL 所需的 bounding box 或 $\varnothing$。[[personal2026]] §3.3.3 Interpretation of generated results, §3.4 Implementation of IPLoc-ID

---

### ③ 真正的创新点是什么？
**事实：任务层创新。** 将只处理正 query 的 personalized object localization 扩展为 POIL，把 negative-query rejection 纳入正式任务定义，并明确区分类别级 FSOD 与 reference-conditioned instance-level detection。[[personal2026]] §1 Introduction, §3.1.1 Personalized object identification and localization

**事实：方法层创新。** 将 IPLoc 输出的 bounding box 从“最终答案”改为“候选区域”，再在同一个自回归序列内通过固定 self-posed query 和 `Yes/No` answer 完成候选验证。[[personal2026]] §3.3 The Proposed IPLoc-ID, §3.3.1 Sequential generation of localization and identification

**事实：训练层创新。** 使用统一目标同时学习候选框生成与正负识别；相比先定位、后识别的两阶段训练，统一目标能够避免 identification fine-tuning 对 localization 的灾难性遗忘。[[personal2026]] §3.3.2 Fine-tuning with positive and negative examples, §4.3.1 Unified objective vs. two-stage training

**事实：数据与评估层创新。** 基于 LaSOT、PDM/BURST、GOT-10K 和 VastTrack 构建成对 positive/negative POIL 数据，并通过 LaSOT 和 VastTrack 的 in-class negatives 检验同类别不同实例之间的拒绝能力。[[personal2026]] §3.5 Datasets for the POIL task, §3.5.1–§3.5.3

**推断。** 最核心的贡献不是某一句 self-posed prompt，而是“先生成候选，再在统一序列中做接受或拒绝”的结构分解。不同 self-posed query 措辞的结果总体接近，说明性能主要来自任务监督、序列结构和 identification objective，而非特定提示词本身。[[personal2026]] §4.3.2 Unified objective vs. conditional branching, §4.3.3 Ablation on self-posed query

---

### ④ 实验说明了什么？
#### 主要事实

**Localization-only 方法无法拒绝负样本。** 测试集中的 positive/negative query 数量平衡，因此始终输出 positive 的方法理论 F1 为 $2/3\approx0.667$。IPLoc 在多种 backbone 和数据集上的 F1 基本停留在这一水平，符合其输出空间中没有 rejection 的理论分析。[[personal2026]] §4.1.2 Evaluation procedure, §4.4 Comprehensive Comparison with State-of-the-Art Methods

**IPLoc-ID 显著提高识别 F1，同时通常保持接近 IPLoc 的 mIoU。** 例如，在 LaSOT 上使用 Qwen3-VL-8B：

* IPLoc 的 1/2/4/8-shot mIoU 为 0.632/0.675/0.694/0.711；
* IPLoc-ID 为 0.637/0.673/0.698/0.714；
* IPLoc 的 F1 均约为 0.667；
* IPLoc-ID 的 F1 为 0.924/0.973/0.982/0.993。

这表明 rejection objective 带来的 F1 增益没有对应地产生明显定位性能损失。[[personal2026]] §4.2 Backbone Model Selection, §4.4 Comprehensive Comparison with State-of-the-Art Methods, Table 3, Table 8

**在 unseen-domain、in-class negative 的 VastTrack 上仍然有效。** 例如 Qwen3-VL-32B 的 IPLoc-ID 在 1/2/4/8-shot 下取得 0.928/0.958/0.951/0.973 的 F1，而对应 IPLoc 约为 0.667；两者 mIoU 仍处于相近区间。该结果比 out-of-class negatives 更能支持实例级拒绝能力。[[personal2026]] §3.5.3 Test set, §4.4 Comprehensive Comparison with State-of-the-Art Methods, Table 11

**跨域结果总体一致。** 在 PDM 和 GOT-10K 上，IPLoc-ID 的 F1 通常明显高于 IPLoc；但这两个数据集的 negatives 来自不同类别，因此高 F1 同时可能受益于类别级区分。[[personal2026]] §3.5.3 Test set, §4.4 Comprehensive Comparison with State-of-the-Art Methods, Table 9, Table 10

#### 消融实验说明

* 两阶段训练虽然能提高 F1，但会快速降低 mIoU，论文将其解释为 localization ability 的灾难性遗忘；统一训练则能同时提升或保持两项指标。[[personal2026]] §4.3.1 Unified objective vs. two-stage training
* 直接在“输出框”和“Not found”之间条件分支，可以取得较高 F1，但会偏向更容易生成的固定 negative response，导致 mIoU 下降。[[personal2026]] §4.3.2 Unified objective vs. conditional branching, Table 4
* 四种 self-posed query 措辞均可工作，说明方法不高度依赖唯一的 prompt wording。[[personal2026]] §4.3.3 Ablation on self-posed query, Table 5, Table 6
* Identification loss 在不同 backbone 和 label-noise 设置下均明显提升 F1；pseudo-label noise 的主要收益则体现为改善 mIoU。[[personal2026]] §4.3.4 Ablation on loss terms with label noise, Table 7

#### 推断

实验较充分地支持了“IPLoc-ID 能抑制 negative-query false positives，并基本保留 positive localization performance”这一较窄结论。

实验尚不能充分证明 identification answer 始终验证了**当前生成候选框所指向的实例**；现有 F1 更直接地验证 query-level 的存在或不存在判断。[[personal2026]] §3.3.1–§3.3.2, §3.5, §4.1.2

#### 待确认

* **[UNVERIFIED]** canonical Markdown 没有明确说明 mIoU 是否只在 positive queries 上统计，以及 negative/rejected cases 如何进入 mIoU 聚合。
* **[UNVERIFIED]** Qwen3-VL-235B 只进行一次独立试验，无法从论文材料核验其结果方差或统计稳定性。[[personal2026]] §4.4 Comprehensive Comparison with State-of-the-Art Methods

---

### ⑤ 依赖哪些前提，边界在哪里？
#### 成立前提

**事实。**

* 目标必须是由 reference images、labels 和 bounding boxes 指定的具体实例，而不是只由类别名称指定的类别级检测。[[personal2026]] §3.1.1 Personalized object identification and localization
* 模型必须是能够进行多模态、连续自回归文本生成的 transformer-based VLM，并能够可靠生成坐标和 `Yes/No` 文本。[[personal2026]] §3.3.1 Sequential generation of localization and identification, §4.2 Backbone Model Selection
* 需要针对 POIL 格式预先微调模型；“in-context”指测试时不根据当前 reference data 更新参数，不代表方法完全不需要任务级训练。[[personal2026]] §2 Related Works, §3.3.2 Fine-tuning with positive and negative examples
* 每种 $N=1,2,4,8$ reference 数量使用单独微调的模型，性能依赖训练与测试的 shot 数一致。[[personal2026]] §3.5.4 N-shot settings
* 训练依赖同时具有 reference、positive query、negative query 和 bounding-box annotation 的 tracking/video-style 数据构造。[[personal2026]] §3.5 Datasets for the POIL task

#### 已明确的边界

* 每个 query 只处理一个目标，不支持同时识别和定位多个目标。[[personal2026]] §5 Conclusion
* 推理按单张图像独立进行，不利用视频的时间连续性、运动或跨帧一致性。[[personal2026]] §5 Conclusion
* LaSOT/VastTrack 使用 in-class negatives；PDM/GOT-10K 使用 out-of-class negatives。后两者更容易混入类别识别能力，不能单独证明细粒度实例匹配。[[personal2026]] §3.5.2–§3.5.3
* 测试集正负样本严格平衡，而真实检索场景可能高度负样本占优；论文没有报告不同 prevalence 下的 precision、false-positive burden 或 calibration。[[personal2026]] §4.1.2 Evaluation procedure
* Interpreter 依赖字符串规则，并在存在有效框且没有显式否定表达时默认判为 positive；自由文本格式错误、否定表达变体和解析策略可能影响最终 F1。[[personal2026]] §3.4 Implementation of IPLoc-ID
* 大模型实验具有较高计算成本；主要训练使用四张 A100，Qwen3-VL-235B 使用八张 B200，且后者只报告单次试验。[[personal2026]] §4.1.3 Other experimental details, §4.4 Comprehensive Comparison with State-of-the-Art Methods
* 复现的 IPLoc 与原始 IPLoc 不能保证完全一致，因为原始工作的完整训练配置和脚本未公开。[[personal2026]] §4.1.1 Training procedure
* 论文材料声明只提供 inference code、dataset construction scripts 和 minimal trained models；training code 和 additional models 计划在论文接收后开放。[[personal2026]] §Data and code availability

#### 推断出的失效边界

* 数据构造中的 negative query 来自另一张图像和另一实例，并未显式包含“query 中真实目标存在，但生成候选框落在同类 distractor 上”的冲突样本。[[personal2026]] §3.5.1–§3.5.3
* 因而现有训练主要学习“这张 query 是否包含 reference instance”，不一定能学会“当前候选框是否确实框住 reference instance”。这是 query-level presence discrimination 与 candidate-bound identity verification 的区别。[[personal2026]] §3.3.1–§3.3.2
* 对没有显著候选对象、包含多个同类实例、严重遮挡或目标与 distractor 外观高度相似的真实图像，现有数据协议提供的直接证据不足。
* 分别训练不同 shot 数模型会限制 reference 数量动态变化时的部署灵活性。

---

### ⑥ 作为审稿人，最关键的质疑是什么？
#### 核心质疑

**事实。** 方法将 identification answer 建模为：

$$
p_\theta(A\mid x,B,Q)
$$

并声称该答案用于验证候选框 $B$ 是否对应 reference object。然而 ground-truth answer 定义为：

$$
A^*(x)=
\begin{cases}
\mathrm{Yes}, & \delta(x)=1, \\
\mathrm{No}, & \delta(x)=0.
\end{cases}
$$

即监督标签只由整张 query 是否包含 reference instance 决定。[[personal2026]] §3.3.1 Sequential generation of localization and identification

**事实。** 正样本训练始终使用 reference instance 的正确框，负样本则使用另一实例的候选框；数据构造没有显式生成“正 query 中存在 reference instance，但提供或生成了错误实例候选框”的训练 cell。[[personal2026]] §3.3.2 Fine-tuning with positive and negative examples, §3.5.1–§3.5.3

**推断。** 因此，论文所声称的“candidate verification”监督并不完全 candidate-conditional。若 query 中确实存在 reference instance，但模型把 $B$ 生成到另一个同类实例上，现有 query-level ground truth 仍对应 `Yes`；论文没有直接证明 answer 会因为候选框指向错误实例而变为 `No`。

这意味着高 identification F1 可能主要说明模型学会了 query-level acceptance/rejection，而不能排除以下错误：

> `Yes + wrong-instance bounding box`

#### 建议作者补充的关键实验

1. 构造同一 query image 中同时包含 reference instance 和同类 distractor 的测试集。
2. 对 positive query 人为替换、扰动或交换候选框，使其落到 distractor 上，并要求 identification answer 为 `No`。
3. 单独报告 wrong-instance acceptance rate，而不是只报告 query-level F1。
4. 增加联合指标：只有输出 `Yes` 且候选框与 reference instance 的 IoU 超过阈值才计为 true positive；`Yes + wrong box` 应明确计为错误。
5. 分别报告 out-of-class negative、in-class negative 和 same-image multi-instance conflict 三种难度。
6. 在真实负样本占优的 prevalence 下报告 precision、false positives per image 和 calibration。

#### 审稿结论状态

**论文材料支持：** IPLoc-ID 能显著改善 negative-query rejection，并在现有数据协议下基本保持定位性能。

**尚未充分验证：** identification answer 是否真正绑定并验证当前生成的候选框，而不只是判断 query image 中是否存在 reference instance。

不应据此自动宣称 candidate-bound instance identification 已被完整验证。

---

### ⑦ 对当前项目有什么启发？
#### 可直接导入当前项目的建议

**建议 1：扩展 E-002 的测试单元。**

沿用当前七问中的 E-002，可将 Rex-Omni/ICOL 的 reference-conditioned evaluation 至少划分为四个 cell：

1. **Positive：** query 中存在 reference instance。
2. **Out-of-class negative：** query 中只有其他类别对象。
3. **In-class negative：** query 中存在同类别但不同实例。
4. **Binding conflict：** query 中存在 reference instance 和同类 distractor，但候选框落在 distractor 上。

前三项复现论文 POIL protocol，第四项补足论文没有显式覆盖的 candidate-bound identity 冲突。依据：[[personal2026]] §3.5 Datasets for the POIL task

**建议 2：不要只使用 localization mIoU。**

建议同时记录：

* positive-query mIoU；
* positive/negative identification precision、recall、F1；
* out-of-class 与 in-class false-positive rate；
* wrong-instance acceptance rate；
* joint success rate：`Yes` 且 `IoU(reference instance) ≥ τ`；
* invalid-output 与 interpreter-failure rate。

依据：[[personal2026]] §3.1.2 Evaluation metric for POIL, §3.4 Implementation of IPLoc-ID

**建议 3：加入三个可区分机制的基线。**

* Localization-only：始终生成框，对应 IPLoc。
* Conditional branch：先决定输出框还是 `Not found`。
* Candidate-then-identify：先生成候选框，再生成身份判断，对应 IPLoc-ID。

若第三种方法降低 in-class false positives，同时保持 positive mIoU，可支持“候选定位与实例拒绝应联合建模”；若只在 out-of-class negatives 上有效，则更可能只是类别识别。依据：[[personal2026]] §4.3.1–§4.3.2

**建议 4：把研究判断拆成两个 Claim。**

* Claim A：模型能判断 query 是否含 reference instance。
* Claim B：模型能判断当前候选框是否框住 reference instance。

论文的 POIL protocol主要验证 Claim A；当前项目应通过 binding-conflict cell 单独验证 Claim B。只有 Claim B 通过后，才能将结果解释为可靠的 candidate-bound instance matching。

**建议 5：明确项目决策规则。**

若 identification objective 在 in-class negatives 与 binding-conflict cell 上显著降低 false positives，并且 positive mIoU 基本稳定，则可优先研究 reference-conditioned identification/rejection objective，而不是只优化内部 token 排列或坐标生成格式。

若 F1 提升只出现在 out-of-class negatives，或出现大量 `Yes + wrong-instance box`，则不能把结果解释为实例级身份绑定成功，应继续加强 hard-negative construction、candidate-conditioned supervision 和联合评估。

**建议 6：数据构造优先级。**

当前项目的数据优先级建议为：

same-image 同类 distractor

> cross-image in-class negative
> out-of-class negative

前者最能区分真正的 reference-instance binding、类别匹配和 query-level presence detection。该优先级属于基于论文数据边界的研究建议，不是论文已经验证的事实。


## 图片标注（survey-tool 管理）
- [[]]  | src:  | boxes: [] | note: 
- [[]]  | src:  | boxes: [] | note: 
- [[]]  | src:  | boxes: [] | note: 
- [[]]  | src:  | boxes: [] | note: 
