# [[detpoinc2026]] — (待补)

> source:

## 七问细读（survey-tool 管理）
### ① 解决了什么问题？
前沿 MLLM 在常见检测基准（OdinW-13、RefCOCO）上已接近 specialist 检测器，但对 OOD 类别/任务/模态（X 光、热成像、航拍、缺陷检测等）泛化差。更反直觉的是：**多模态 ICL（直接给 few-shot 视觉示例）反而比仅用类名+文本指令更差**（Table 1：Qwen3-VL-8B 加图像后 11.4→7.0 mAP）。而前沿模型只 API 可用、开源大模型微调昂贵，无法梯度更新。

因此作者解决的是：**在黑盒（gradient-free）设定下，如何用 few-shot 多模态示例提升 MLLM 的 few-shot 目标检测精度**。核心思路是把视觉示例"蒸馏"成文本提示——提出 DetPO，用 MLLM 自身当评论家，基于自身 FP/FN 视觉反馈迭代精炼纯文本类定义，并校准逐框置信度。

依据：[[detpoinc2026]] §1 Introduction, Fig.1, Table 1；§3 第 1 段。

---

### ② 默认了哪些前提？
1. MLLM 只能黑盒访问（API 或大开源模型），**不可梯度更新**——这是整个方法论的前提（§1, §2 Prompt Optimization）。
2. 每个数据集提供 **10-shot 训练示例 + 丰富文本标注指令**（RF20-VL 设定，§4 Datasets），且存在可用的 held-out 验证集用于候选提示选择（§3 Stage 3, Appendix C）。
3. **多模态 ICL 对检测无效**这一现象被当作既定事实并作为动机（Table 1），作者将其归因于 post-training 提示结构刚性，但未深证。
4. MLLM 可同时充当**检测器与评论家**（critique = target，§1 末段）。
5. 目标概念可用自然语言判别性描述表达，且 MLLM 能理解并据此检测（§3 Contrastive Prompt Refinement）。
6. 评估遵循 COCO mAP 协议，IoU≥0.5（§4, Appendix B）。
7. 逐类（single-class）独立优化是默认范式，多类为后置拼接/摘要（Appendix J）。

依据：[[detpoinc2026]] §1, §3, §4 Datasets and Metrics, Appendix C。

---

### ③ 相比已有工作的创新点？
1. **视觉反馈驱动的提示优化**：已有黑盒提示优化（GEPA [2]、MIPROv2 [40]）把视觉任务当纯数值黑盒，只用 IoU/F1 标量奖励"盲调"提示；DetPO **直接把 FP/FN 的视觉示例（彩色框标注图）喂给 MLLM**，让它"看见"漏检/误检并据此改写类定义。作者明确强调"visual tasks should leverage visual feedback"（§3 第 2 段）。
2. **对比式提示精炼（Contrastive Refinement）**：用 FP 收紧定义（RefineExclude）、用 FN 放宽定义（RefineInclude），模拟人类标注员"学什么不该标"的过程（Fig.2, Fig.3, §3）。
3. **置信度校准组合**：自报告逐框置信度 + 可选 VQA Score 二值重排序（用 Yes token 归一化概率），并演示用 Qwen3-VL 给 Gemini 预测做跨模型重排序（§3 VQA Score, Table 4）。
4. **系统基准化**：首次在 RF20-VL 上系统揭示"多模态 ICL 反而损害检测"的现象并量化（Table 1）。

依据：[[detpoinc2026]] §3, Fig.2, Fig.3, §2 Related Works（Prompt Optimization 段）, Table 4。

---

### ④ 实验是否足够支持结论？
**支持的部分（充分）：**
- 主结果在 RF20-VL（20 数据集 × 7 超类）上跨多个 MLLM（Qwen2.5-VL 7B/72B、Qwen3-VL 8B/30B-A3B、Gemini 3 Pro）一致提升，并对比 specialist（GroundingDINO、LLMDet、SAM3、MQ-GLIP、YOLO-E）与 prompt opt 基线（GEPA、MIPROv2）（Table 2, 3）。
- LVIS Rare-50 第二基准复现趋势（Table 6）。
- 消融较完整：置信度方式（Table 4）、K-shot 3/5/10（Table 7）、采样策略 worst vs random（Table 9）、方差 3-seed（Table 8）、单类 vs 多类（Table 10）、token/时间（Fig.9,10）、TIDE 错误分解（Fig.6,8）、混淆矩阵（Fig.5）。

**不足 / 未能支持的结论：**
- **"可替代 fine-tuning"未被支持**：白盒微调 GroundingDINO 33.4 mAP 仍远超 DetPO 最佳 21.6（Table 5），作者仅以"趋势线"乐观推测未来。
- Medical 超类几乎无改善（0.1–0.4 mAP），"跨域一致提升"说法有例外。
- VQA Score 虽提 mAP，但 TIDE 显示其显著增加 FN 与定位错误（Fig.6），存在 trade-off 未充分讨论。
- worst-case 采样并未显著优于随机（Table 9 甚至随机略优），核心设计选择的必要性被削弱。
- 闭源 Gemini 评测存在训练数据泄漏风险，无法排除（§Limitations）。

依据：[[detpoinc2026]] §4 Table 2–5, Appendix E–J, Fig.6, §Limitations。

---

### ⑤ 可能的反例？
1. **弱基础域失效**：Medical 列在所有模型上 DetPO 几乎无增益（Table 2: 0.7→0.2；Table 3: 0.7→0.1→0.2），说明基础模型能力过弱时提示优化无能为力——与作者自述"intermediate regime"一致（§Limitations）。
2. **类别数扩展性**：单类逐类优化，类别多时 token/时间线性增长（Appendix F 自认），且多类拼接显著退化（Table 10：30B 19.4→16.0）。
3. **VQA Score 的副作用**：将部分 TP 错误降权，FN 与 Loc 错误大幅上升（Fig.6 右）——对高召回场景是反例。
4. **采样策略反例**：10-shot 下 random FP/FN 反而略优于 worst-case（Table 9），"选最严重错误"的直觉在小样本下不成立。
5. **闭源泄漏反例**：Gemini 3 Pro 的高分（26.4）无法完全排除 RF20-VL 图像/指令进入其预训练的风险（§Limitations）。
6. **饱和/无能两端失效**：模型已饱和或完全无能时 DetPO 无收益（§Limitations 自述）。

依据：[[detpoinc2026]] Table 2/3/9/10, Fig.6, §Limitations, Appendix F/J。

---

### ⑥ 审稿人会提哪些质疑？
1. **"实用替代 fine-tuning"主张过强**：Table 5 显示白盒微调仍领先 10+ mAP，论文标题级贡献需降调。
2. **可扩展性**：单类优化对多类数据集（LVIS 50、COCO 80）开销与延迟如何？多类设定已退化（Table 10），实际部署多类为主。
3. **VQA Score 对闭源模型不通用**：Gemini API 不暴露 logit，需借用 Qwen3-VL 做后处理——引入跨模型不一致与额外成本，且改变了"纯黑盒"叙事。
4. **核心设计选择被自家消融削弱**：worst-case 采样未优于随机（Table 9），审稿人会质疑"选最严重 FP/FN"的必要性。
5. **优化开销**：作者自承"类似训练一个 specialist"（§Limitations），与"轻量黑盒"卖点冲突。
6. **shot 数上限**：仅到 10-shot，未探索 20/50/100-shot 饱和点（Table 7）。
7. **数据泄漏**：闭源模型评测泄漏无法排除，结果可信度受疑。
8. **Medical 失败缺分析**：为何 prompt 优化在医学域失效，未给机理。
9. **基准覆盖**：仅 RF20-VL + LVIS 子集，缺更大规模 OOD 基准。
10. **多模态 ICL 失效只现象不机理**：Table 1 揭示现象但"post-training 提示结构刚性"仅为推测（§1 posits），无消融验证。

依据：[[detpoinc2026]] Table 5/9/10, Fig.6, §Limitations, Appendix F/J, §1。

---

### ⑦ 扩展方向 → Idea
**论文自述 future work：** 并行化逐类优化、更好的置信校准机制、把 DetPO 用于下一代 frontier MLLM 以超越 fine-tuning、加速推理（vLLM）、解决闭源泄漏（§Limitations, Appendix F/J）。

**可衍生的新方向（针对本项目 in-context object localization）：**

1. **视觉示例→判别性文本属性的"翻译器"**：DetPO 的迭代 MLLM 推理开销大。可训练一个轻量模块（或用小模型蒸馏），直接从 few-shot 图像 + 标注生成判别性文本属性，免迭代、免大模型评论家，使 prompt 优化成本与类别数解耦。这直接攻击 §Limitations 的开销问题与 Table 10 的多类退化。

2. **多模态 ICL 失效机理 + 修复**：Table 1 显示给图像反而掉点，作者归因"post-training 提示结构刚性"但未证。可系统消融：固定 vs 自由提示模板、视觉 token 位置、指令格式，定位失效根因；进而探索**松绑 post-training 模板**或**视觉 token 插入策略**使真正的多模态 ICL 生效——若成功，可绕开"视觉→文本蒸馏"的信息损失。

3. **对比式视觉反馈迁移到 in-context localization**：本项目关注 localization 而非完整检测。DetPO 的 RefineInclude/RefineExclude 用 FP/FN 视觉反馈精炼类定义，可改造为**定位精度反馈**（用定位误差大的样本驱动提示/示例选择），用于指代表达式定位或 few-shot 定位。

4. **主动 shot 选择 + 更大 shot 探索**：Table 7 只到 10-shot 且 5→10 边际递减。可做主动学习选最具判别力的 shot，并探索 10→100-shot 是否复利。

5. **弱基础域的两阶段方案**：Medical 失败提示"先补基础能力再优化提示"。可研究在 DetPO 前加轻量域适配（如 retrieval-augmented 视觉记忆）使弱域进入"intermediate regime"。

**推荐优先 Idea（新颖性 + 可验证）：** 方向 2（多模态 ICL 失效机理与修复）——这是论文留下的最大未解释空白，且若修复成功可直接挑战 DetPO 的"必须转文本"前提，属于对本工作的正面超越而非增量。

依据：[[detpoinc2026]] §1, §3, §Limitations, Table 1/7/10, Appendix F/J。

---

> 说明：以上为基于原文的观察与推演，未引用任何未抓取论文。若需将这些声明纳入综合，应先按项目工作流写入 `kernel/claims.md` 并标注 validated 状态。方向 2 的"新颖性"尚需对 [[detpoinc2026]] §2 中引用的 Flamingo[3]/Emu2[54] 等 ICL 工作做 novelty check 后方能定级（当前标"需补"）。


## 图片标注（survey-tool 管理）
