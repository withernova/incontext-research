# E-002 internal-token mechanism plan（补充，2026-07-13）

## 核心提醒
E-002 不是普通 POIL/IPLoc benchmark。核心是检验：

> MLLM 在 IPLoc / reference-conditioned instance localization 中的瓶颈，是否来自没有充分使用 object-internal visual token 的细粒度空间结构/顺序。

E-001 已知：support object 内部 token shuffle 后 Rex-Omni 仍能检测。因此证据链应是：

1. instance-level hard setting 在任务上需要内部细节/顺序；
2. 当前模型在 hard setting 中对内部 token 顺序扰动不敏感或利用不足；
3. token-level 机制实验优先，image-patch perturbation 只是辅助 proxy，二者必须区分。

## 必须区分的两类扰动

### A. Image/patch-level perturbation（辅助）
- 在输入图像 bbox/crop 内切 grid patch 后 shuffle / replace。
- 优点：工程快，模型无关，能快速发现现象。
- 缺点：引入像素级 artifact；改变低层视觉统计；不等价于 MLLM visual encoder token 排列。
- 结论定位：只能作为 proxy / pilot，不作为最终 token-mechanism 证明。

### B. Visual-token-level perturbation（主机制）
- 在模型 visual encoder 输出后，对 GT object mask/bbox footprint 对应 visual tokens 做 shuffle / replacement / copy。
- 保持原图像、prompt、视觉编码以外流程不变。
- 与 E-001 一致：应优先在 visual(...) 后、scatter/merge into LLM embeddings 前干预。
- 结论定位：这是内部 token 细节/顺序机制的主证据。

## Hard 样本挖掘：不仅看图像相似，还要看 visual-token feature 接近程度

启发：如果 reference 与 same-class negative 的 object-internal tokens 在模型视觉层特征空间很接近，但 identity 不同，则是更强 hard negative。

### 候选 hard score
对每个样本构造：reference r、positive p、negative n。

基础约束：
- same category；
- bbox area/aspect ratio 接近；
- crop-level视觉相似；
- sequence identity 不同（negative）。

进一步加入模型视觉特征：
- 提取 object footprint 内 visual tokens：T_r, T_p, T_n；
- 计算 token-set similarity，而不是只看全局 crop embedding。

可用指标：
1. mean pooled cosine：cos(mean(T_r), mean(T_n))；
2. token-set Chamfer similarity：
   - mean_i max_j cos(T_r[i], T_n[j]) 与反向平均；
3. order-aware similarity：
   - 对齐到 normalized bbox grid 后逐 cell cosine；
4. order-gap：
   - unordered token-set similarity 高，但 order-aware similarity 低，说明“bag of internal parts”像，但空间排列不同；这种特别适合证明内部顺序重要。

Hard negative 优先级：
- category same；
- silhouette/area/aspect similar；
- unordered token similarity high；
- order-aware token similarity low 或局部结构排列不同；
- identity different。

这类样本能逼迫模型不能只用类别或 token bag，必须使用内部 token 的空间排列。

## 实验路径更新

### R-002a image-patch hard pilot
当前 autoloop 的 patch shuffle/replacement 只作为 pilot：
- hard subset mining；
- bbox-internal patch shuffle；
- 看是否存在明显 decision/mIoU 变化。

### R-002b visual-feature hard mining
新增：用 Qwen3-VL / Qwen2.5-VL / Rex-Omni visual layer 抽取 object token features，重排 hard subset。
输出：
- `LASOT_hard_tokenfeat_*.json`
- token similarity report；
- 每个样本可视化：reference / negative / positive + token similarity heatmap。

### R-003 token-level shuffle on hard-tokenfeat subset
对视觉 token 做：
- ref_internal_token_shuffle；
- pos_internal_token_shuffle；
- neg_internal_token_shuffle；
- ref_pos_internal_token_shuffle；
- full_image_token_shuffle control。

比较：
- TP/TN/FP/FN；
- positive mIoU；
- negative FPR；
- decision flip rate；
- bbox shift/area shift；
- output text yes/no flip。

### R-004 token-level replacement / identity transfer
- 用 same-class negative 的 object-internal tokens 替换 reference internal tokens；
- 用 reference internal tokens 替换 negative query internal tokens；
- 保持 token footprint/position 不变。

若模型使用内部 identity：预测应随 donor token identity 转移。若不变：说明内部 token 内容/顺序未被有效使用。

### R-005 order vs bag-of-tokens diagnostic
构造三种 token干预：
1. spatial-order shuffle：token values same，位置打乱；
2. token-content replacement：位置不变，值替换；
3. bag-preserving but order-destroying matching：按相似 token 跨图替换。

目标区分：
- 模型是否使用内部 token 内容；
- 是否使用内部 token 空间顺序；
- 是否只使用 pooled/category-level representation。

## 需要保存的分析产物
- metrics JSON；
- generated_texts；
- per-sample flip table；
- token similarity CSV/JSON；
- 可视化面板：原图、GT bbox、预测 bbox、token footprint、token similarity heatmap；
- patch-level 和 token-level 结果必须分开放目录和表格，避免混淆。

## 当前执行原则
1. 不再把普通 n20/n140 POIL 当主线；它只是 sanity。
2. patch perturbation 可以继续跑，但必须标为 image-level proxy。
3. token-level intervention 是后续主实验，应复用 E-001 mechanism 代码风格。
4. hard mining 应加入 visual-layer token feature similarity，尤其寻找 unordered-similar but order-different 的 hard negatives。

## Mechanisms paper protocol anchors（必须遵守/对齐）
已读取 `papers/Mechanisms of Object Localization in Vision-Language Models_2026/hybrid_auto/Mechanisms of Object Localization in Vision-Language Models_2026.md`。后续 token 实验应尽量对齐该文，而不是只做输入图像 patch proxy。

关键协议点：
- 干预位置：LLM input 处，即 multimodal projection 之后、positional/autoregressive processing 之前。论文表述为 “after the multimodal projection but before positional encodings and autoregressive processing”。
- Object token 选择：将 object mask 映射到 image token grid；只要 token 与 mask 有任意 pixel overlap 即选中。
- Padding：在 token mask 上做 -2/-1/object/+1/+2 padding，以区分边界、上下文和 object footprint 贡献。
- Ablation：用 ImageNet validation 上计算的 global average visual embedding 替换选中 visual token，以保留 embedding 分布统计，而不是简单置零。
- Container extension：向 object mask 周围 padding 区域随机复制 object 内部 token，增加 object-related token footprint，并用多个随机 seed；测预测框是否随 token footprint 扩张。
- Shuffle：在 LLM input 处直接 shuffle image tokens；对比 full image token shuffle 与 object-mask-only shuffle。论文发现 object-only shuffle 对 localization 影响远小于 full shuffle，支持 containerization。
- 多视图模型要区分 global/local view；如果模型含 global thumbnail + local high-res crop，应分别分析 global object tokens 与 local object tokens。
- 注意力/因果层面：论文还有 attention knockout 与 causal mediation，但 E-002 首要复现 token perturbation；后续可扩展到 head/layer attention blocking。

E-002 改造原则：
1. Patch-level image perturbation 标为 pilot/proxy；不能替代上述 LLM-input token perturbation。
2. Qwen3-VL/IPLoc-ID token 实验应找到等价插入点：vision tower + projector 后、visual embeddings merge/scatter 到 LLM 前或刚成为 LLM input embeddings 后。
3. 若 Qwen3-VL 插入点工程代价过高，先在 Rex-Omni/vLLM 已有 E-001 subclass 上按论文协议严格复现，再迁移到 IPLoc-ID。
4. Hard mining 的 token feature 应来自同一插入点/同一层级，避免用像素 patch proxy 混淆。
5. 每个 token 机制实验至少包含：baseline、object-token ablation(global average)、object-token shuffle、full-image shuffle、object extension/copy-padding；必要时加 random token control。

