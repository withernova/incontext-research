# [[mechanis2026]] — (待补)

> source:

## 七问细读（survey-tool 管理）
### ① 解决了什么问题？
填补"VLM 如何在内部计算中实现物体定位（localization）"这一机制空白。此前分类机制已有较多 mechanistic 研究，但定位/检测的内部过程几乎无人系统分析。论文用 token ablation、attention knockout、causal mediation analysis（CMA）等可解释性工具，在 LLaVA-1.5 与 InternVL-3.5 上给出首个 layer/head 级别的定位机制描述，核心结论是"containerization"：物体对齐 token 集体界定空间边界，内部语义排列对预测框几乎无关；且仅极少数 attention head 因果中介定位，定位因果依赖分类关键 head（先识别后定位）。依据：[[mechanis2026]] §Abstract、§1 Introduction（findings 1–4）、§5 Discussion。

---

### ② 方法具体怎么做？
- 模型：LLaVA-1.5（7B/13B，CLIP ViT-L/14 → 2 层 MLP → Vicuna，24×24 token 一对一映射）与 InternVL-3.5 8B（InternViT-300M → Pixel Shuffle 4× 压缩 → Qwen3-8B，动态高分辨率 local tiles + global thumbnail）。依据：[[mechanis2026]] §2.1。
- 数据：COCO val 经 Singh et al. 修正 + 过滤（单类单实例、尺寸/分辨率阈值），6,403 标注 / 3,560 图；再用 LaMa inpainting 构造物体移除反例，取三模型交集得 2,248 标注 / 1,720 图作 probing 子集。依据：§2.2、§6.1。
- 任务：定位（预测 bounding box，IoU 0.5/0.7/0.9 平均成功率）+ 分类（list-based 列举 COCO 类别）。依据：§2.3。
- 实验组：(1) 视觉信息消融——在 LLM 输入端（投影后、位置编码前）用 ImageNet 全局均值 embedding 替换选定 token，四种选择策略：object mask token（含 ±padding）、register token（norm>2σ）、Integrated Gradients top-k、random。§3.1、Table 1。(2) Containerization——把物体内部 token 随机复制到外围 padding 层扩大物体测框是否等比例扩展（Fig.1），再 within-mask shuffle vs full shuffle（Table 2）。§3.1.1。(3) InternVL global/local 分离消融，按物体大小分解（Table 3、Fig.10）。§3.1.2。(4) 位置解码——每层训练线性分类器预测 token 网格位置，ImageNet 50k/10k。§3.2、Fig.2。(5) Attention knockout——按 4 层一组屏蔽 post-image token 对 object token 的注意力。§3.3.1、Fig.3。(6) CMA（activation patching）——source（有物体）→ base（inpainting 去物体），逐 head 把 source 激活 patch 进 base，teacher-forcing perplexity 计算 Mediation Fraction MF=(P_base−P_patched)/(P_base−P_src)，50 张图，分类用 binary query。§3.3.2、式(1)、Fig.4、Fig.13。(7) 累积 head 消融——按 MF 排序逐步移除 task-critical vs low-importance head 验证必要性。§3.3.3、Fig.5。

### ③ 真正的创新点是什么？
- 首次针对"定位"做机制级研究：既有 VLM 可解释性工作聚焦高层推理/VQA/幻觉/分类失败，无人定位"空间信息在模型内何处涌现、如何变换"。依据：[[mechanis2026]] §4。
- 提出 containerization 机制：物体 token 集体定义边界、内部语义排列无关——由 padding 扩展 + shuffle 两套扰动验证，是新现象，非已有分类机制研究所覆盖。依据：§3.1.1、Fig.1、Table 2。
- 多视角（global/local）解耦：global 主空间、local 主要 refine 小物体分类，互补非冗余，并按物体大小量化。依据：§3.1.2、Table 3、Fig.10。
- attention-head 级 CMA + 累积消融定位极稀疏 critical head，并据此提出"先识别后定位"顺序机制。依据：§3.3.2、§3.3.3、Fig.4、Fig.5。
- 位置信息在 LLM 早—中层重新可解码、投影层保留四角锚点的发现。依据：§3.2、Fig.2、Fig.11。

### ④ 实验说明了什么？
- object token 消融使定位降至 <10%、分类 20–30%，远大于等量 random/gradient 消融；正 padding 加剧、负 padding（保持原边界）影响小 → 关键信息在物体边界内。依据：[[mechanis2026]] Table 1、§3.1。
- padding 扩展后预测框随 +1/+2 等比例对齐（Fig.1 对角强对齐）；within-mask shuffle 仅微降定位、分类不受影响 → containerization。依据：Table 2、§3.1.1。
- 单视角消融中等下降、双视角同时消融大幅下降；global 消融定位 −36.4% vs local −9.7%；小物体对两视角都敏感、大物体 local 消融甚至 +6.5% → 互补、global 主空间。依据：Table 3、Fig.10、§3.1.2。
- 位置解码：backbone 末端衰减，LLM 早—中层峰值（LLaVA-7B L12、13B L13、InternVL L7），四角高准确率。依据：Fig.2、Fig.11、§3.2。
- knockout：LLaVA 早—中、InternVL 中—后层下降最大；CMA 同区域稀疏高 MF head，top-10 共享仅 1–2 个；累积消融 critical head 远大于 low-importance；消融分类 head 也伤定位 → 稀疏、专门化、顺序机制。依据：Fig.3、Fig.4、Fig.5、§3.3。
- Pascal VOC 复现 object 消融一致性。依据：Table 5、§7.3。

### ⑤ 依赖哪些前提，边界在哪里？
前提：
- CLIP 全局监督特征像素精度不足但 VLM 仍能定位，故定位机制"涌现"自弱空间表征。依据：[[mechanis2026]] §1。
- bounding-box + IoU 可作定位代理；单类单实例过滤不破坏一般性。依据：§2.2、§2.3、§6.1。
- LaMa/diffusion inpainting 能干净移除物体以隔离上下文幻觉。依据：§2.2。
- 线性探针、activation patching、knockout 反映因果而非仅相关。依据：§3.2、§3.3。
- 分类 CMA 用 binary query，配对设计下高幻觉率不影响因果估计。依据：§3.3.2、§6.2。
边界：
- 仅 ViT→MLP→LLM 两族三尺寸；未涉 decoder-only / 非 CLIP backbone。依据：§2.1、§5。
- 只分析固定模型 attention head，未涉 MLP、训练动态、分割、关系定位、视频。依据：§5。
- containerization 仅 padding≤2、within-mask shuffle；细长/镂空/多实例未测。依据：§3.1.1。
- CMA 仅 50 张图。依据：§3.3.2。

### ⑥ 作为审稿人，最关键的质疑是什么？
1. 架构覆盖窄：仅 LLaVA + InternVL，均为 ViT→MLP→LLM，结论外推到 Qwen-VL/Molmo/Llama-Vision 存疑。依据：[[mechanis2026]] §2.1、§5。
2. CMA 50 张样本过小，MF 排序与 head 重叠（top-10 共享 1–2）的统计稳定性需 bootstrap。依据：§3.3.2。
3. 任务简化（单物体、bbox、封闭词表）与真实 grounding benchmark 距离大，外部效度存疑。依据：§2.2、§2.3。
4. 分类 CMA 用 binary query 与主实验 list query 不一致，且幻觉率更高（FPR 0.56–0.70 vs 0.27–0.45），head 重要性可比性存疑。依据：§3.3.2、§6.2。
5. "先识别后定位"仅由"消融分类 head 伤定位"间接推断，未排除共享早期处理的并行解释；缺跨层定向 patch / 时间证据。依据：§3.3.3。
6. inpainting 分布漂移可能污染 base perplexity。依据：§2.2、§3.3.2。
7. 线性位置探针低估非线性编码。依据：§3.2。

### ⑦ 对当前项目有什么启发？
- containerization 提示可设计"边界 token 强监督 + 内部排列不变"的 grounding loss，在弱标注下提框精度。依据：[[mechanis2026]] §3.1.1、§5。
- 稀疏 critical head 可作 in-context 干预靶点：把示例图（带框）的定位 head 激活 patch 到查询图 forward，实现 few-shot in-context 定位增强——最贴合本项目 in-context object localization 主题，优先进入 claim 分解。依据：§3.3.2、§3.3.3。
- 动态视角路由：按物体大小/任务决定 local tile 数，降 token 成本而不损精度。依据：§3.1.2。
- 构造细长/镂空/多实例反例集检验 containerization 失效边界，提出形状感知 head 筛选。依据：§3.1.1、Fig.10。
- 跨架构（SigLIP/DINOv2 + 显式 2D PE）复现 CMA，判别"顺序机制"是否普适。依据：§3.3.3、§5。



## 图片标注（survey-tool 管理）
