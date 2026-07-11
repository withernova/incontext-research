# [[detpoinc2026]] — (待补)

> source:

## 七问细读（survey-tool 管理）
### ① 解决了什么问题？
通用 MLLM 在 OdinW-13、RefCOCO 这类热门检测基准上已与 GroundingDINO 等专用检测器持平，但面对预训练里没见过的**类/任务/成像模态**（X 光、热成像、航拍、缺陷检测、材质属性）会崩；而**直接把 few-shot 视觉示例塞进 prompt（多模态 ICL）反而掉点**（Qwen3-VL-8B mAP 11.4→7.0），且前沿 MLLM 只能走 API、开源大模型在消费级硬件上微调太贵。DetPO 要解决的就是"在不能微调的前提下，如何让冻结 MLLM 用 few-shot 示例对齐 OOD 类概念"。依据：[[detpoinc2026]] §1 Introduction + Table 1。

### ② 默认了哪些前提？
(1) 前沿 MLLM 是 API-only 黑盒、开源大模型微调不可行 → 必须 gradient-free；[[detpoinc2026]] §1。(2) 目标类可以被**文本描述**刻画，因此优化对象是纯文本类描述而非视觉条件化；§3。(3) 存在少量标注的 few-shot 训练集，能跑推理拿到 FP/FN 用作迭代反馈；§3 Fig.2。(4) MLLM 能自报每框置信度，且 VQA Score 需要访问 Yes/No token 概率（Gemini 不暴露 token 概率，于是用 Qwen3-VL 替 Gemini 重打分）；§3 VQA Score。(5) 任务是"按类检出全部实例"的检测，非单实例定位；§4。

### ③ 相比已有工作的创新点？
相对 GEPA/MIPROv2 等**只用数值奖励盲优化**的通用 prompt optimizer，DetPO 把视觉 FP/FN 样本喂给 critique MLLM 去改写文本 prompt（"视觉任务该用视觉反馈"）；相对经典 FSOD（meta-learning/transfer-learning + 微调），它是**面向通用 MLLM 的黑盒/免梯度**路线；并提出 **VQA Score**（二值 Yes/No 归一化概率）为默认无每框置信度的 MLLM 校准置信度。核心 insight 是"多模态 ICL 损害检测 → 把视觉示例蒸馏进文本 prompt"。依据：[[detpoinc2026]] §3 + Fig.2，§1 + Table 1，§3 VQA Score，Table 2（超 GEPA/MIPROv2 及专用检测器）。

### ④ 实验是否足够支持结论？
基本充分：在 RF20-VL（20 个跨域数据集）+ LVIS 上，跨多模型（Qwen2.5-VL 7B/72B、Qwen3-VL 8B/30B、Gemini 3 Pro）得到一致提升，Qwen3-VL-30B 11.9→21.6、Gemini 23.8→26.3 mAP，超 GEPA/MIPROv2 与专用检测器（Table 2/3）；做了置信度消融（self-reported vs SigLIPv2 vs VQA，Table 4）、TIDE 误差分析（Fig.6）、混淆矩阵（Fig.5）、黑盒 vs 白盒微调对比（Table 5）。但**仍落后于微调**（GroundingDINO fine-tuned 33.4 > DetPO 26.3）、**医学域近乎失效**（0.2 mAP）、迭代开销近似训一个专用模型、VQA Score 把误差挤向定位/FN、Gemini 存在训练数据泄漏风险。依据：[[detpoinc2026]] §4 Table 2–5 + Fig.4/5/6，§Limitations。

### ⑤ 可能的反例？
- 基模型过弱时 prompt 优化无能为力：医学域 0.2 mAP（Table 2）。
- VQA Score 降 FP 但抬高定位误差与漏检（Fig.6）——对召回敏感场景反效果。
- 类的判别性**无法用文字描述**（如纯功能/上下文定义的类）时，文本 prompt 蒸馏失效。
- few-shot 训练集不具代表性时 prompt 过拟合训练集。
- 闭源 Gemini 的优化 prompt/图像可能进入未来预训练，数字被污染（§Limitations）。
依据：[[detpoinc2026]] Table 2（Medical）、Fig.6、§Limitations。

### ⑥ 审稿人会提哪些质疑？
1. 仍输给白盒微调（Table 5：26.3 vs 33.4），"既然能微调为何不微调？"——DetPO 的辩解是 API-only 前沿模型，但审稿人可主张开源微调才是 SOTA。
2. 迭代 prompt 优化成本≈训一个专用模型（他们自承），削弱"免梯度=便宜"的叙事。
3. 闭源 Gemini 的可复现性/公平性/训练泄漏风险。
4. VQA Score 依赖 token 概率，Gemini 不暴露 → 用 Qwen3-VL 跨模型重打分是否公平/可推广。
5. 只测 10-shot，未系统扫 shot 数。
6. RF20-VL 是较新基准，与既有 FSOD 文献可比性有限。
7. 置信度设计脆弱：SigLIPv2 重打分反而掉点（Table 4，19.4→16.4）。
依据：[[detpoinc2026]] Table 4/Table 5、§Limitations。

### ⑦ 扩展方向 → Idea
1. **把"ICL 损害检测"这个负结果变成正题**：训练 MLLM 真正利用视觉示例做检测（即 FOCUS/ICOL 的 weight-level 路线搬到检测），DetPO 的 Table 1 正是动机。[[detpoinc2026]] Table 1。
2. **黑盒 prompt 优化 + 白盒 attention 监督的混合**：API-only 走 DetPO，开源模型走 FOCUS 式 attention loss+GRPO，统一框架。
3. **training-free ICOL**：把 DetPO 的对比式 prompt 优化迁到 in-context 单实例定位（不 SFT，优化 support 描述/置信度），作为你 ICLO 项目的免训练 baseline。§3 + [[focusfor2026]] 对照。
4. **更好的置信度校准**：在 VQA Score 上加 conformal/温度校准（他们承认自报分数次优）。§Limitations。
5. 用 vLLM 加速迭代优化、扩展到视频/流式检测。§Limitations + §5。


## 图片标注（survey-tool 管理）
