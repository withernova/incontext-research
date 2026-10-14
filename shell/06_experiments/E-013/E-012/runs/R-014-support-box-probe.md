# R-014-support-box-probe · 强行改写参考帧框坐标的影响

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
把 prompt 里 support 帧的 BBOX 坐标强行改掉，模型预测的框会受多大影响？是只靠 query 图像，还是真的在用 support 框当先验？

## 2. 目的
不改注意力、不动 head，只改输入里的 support 框文本：分别用保持数值只改写法、退化框、随机框、平移 5%/25%、换成别的样本的框、以及换成 query 的 GT 框，测量对自由生成定位与 teacher-forced 读出的影响。用来判断前面"删参考图通道几乎不掉点"是不是因为模型其实主要依赖 support 框给出的空间先验。

## 3. 方法（干预 · 对照 · 指标与判定规则）
干预：只在输入侧改写 prompt 中 support 帧的 BBOX 文本（其余输入与权重完全不变），逐模式跑自由生成与 teacher-forced 读出。模式 8 种：respace（数值不变只改写法，作为文本扰动的对照）、zero（[0,0,0,0]）、center（[250,250,750,750]）、random（随机合法框）、shift5/shift25（沿 x 平移 5%/25% 画幅，保持框宽）、shuffle_box（用下一条样本的 support 框替换）、oracle_query_gt（换成 query 的 GT 框，信息上界）。条件=基线 + 8 模式 = 9 条；样本 100（LaSOT 50 + GOT10k 50）。指标：自由生成 mIoU 变化为主，teacher-forced argmax 框 IoU 为确定性辅助轴，teacher-forced 坐标 CE 为机制诊断；另记 support_box_used 以便核对扰动确实生效。

**干预与对照**：support 框改写模式（8 种）× 其余输入与权重固定；基线为原始 prompt 同一权重

**指标计划**：主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化；核对项：support_box_used 与生成的框是否跟着扰动框移动。

**判定门槛 / no-silent-zero**：基线空 hook parity；每个扰动条件重新 collate 后强制校验 bbox token 对齐与序列长度预算；记录 support_box_used 原文以便复算；respace 作为文本扰动的阴性对照。

**验收判定**：沿用事先冻结阈值：守住 = 配对 ΔmIoU 的 95% CI 下界 > −0.01；主报告为 8 种改写模式的 Δ 与 CI 排序，并对照 respace（写法扰动）判断哪些差异来自坐标本身。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
模块 iploc_szy/head_screening/keepset_pruning.py 新增 intervention=support_box 与 8 种改写模式（perturb_support_box/perturb_support_messages/support_box_conditions）；扰动条件重新 collate 并强制校验 bbox token 对齐；run() 改为接受上下文。新增 configs/experiments/E-012/analysis/e012_r014_support_box_probe_step741.py 与对应 launcher。数据 R-001 冻结索引 LaSOT 50 + GOT10k 50；模型 E-009 step741（与 R-011/R-012/R-013 同 checkpoint）。commit 7b3df29548034fe62fdf97a7df0f0390514ca57f。

**数据规模**：100 条（LaSOT 50 + GOT10k 50）；9 条件 × 100 条 = 900 次生成（另加每条件 teacher-forced 前向），约 1 小时。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/analysis/e012/e012_r014_support_box_probe_step741.sh`
- commit: `7b3df29548034fe62fdf97a7df0f0390514ca57f`
- workspace: 02
- tmux: incontext-E-012-R-014-support-box-probe
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-014-support-box-probe/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/r014-support-box-probe-step741-v1
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
只改 support 框文本、不改图像；support 与 query 同段视频，坐标归一化带来的先验强度可能随数据集而异；样本仅 LaSOT+GOT10k；自由生成 mIoU 有运行间噪声。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "R-012/R-013 显示参考图的视觉通道对 bbox 预测影响很小，但 support 帧的框是以文本形式写进 prompt 的（且 support 与 query 同段视频、坐标已归一化），这本身是很强的空间先验；不单独测它，就无法判断模型到底靠什么定位。",
  "implementation_details": "模块 iploc_szy/head_screening/keepset_pruning.py 新增 intervention=support_box 与 8 种改写模式（perturb_support_box/perturb_support_messages/support_box_conditions）；扰动条件重新 collate 并强制校验 bbox token 对齐；run() 改为接受上下文。新增 configs/experiments/E-012/analysis/e012_r014_support_box_probe_step741.py 与对应 launcher。数据 R-001 冻结索引 LaSOT 50 + GOT10k 50；模型 E-009 step741（与 R-011/R-012/R-013 同 checkpoint）。commit 7b3df29548034fe62fdf97a7df0f0390514ca57f。",
  "metric_plan": "主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化；核对项：support_box_used 与生成的框是否跟着扰动框移动。",
  "data_scale": "100 条（LaSOT 50 + GOT10k 50）；9 条件 × 100 条 = 900 次生成（另加每条件 teacher-forced 前向），约 1 小时。",
  "variables_controls": "support 框改写模式（8 种）× 其余输入与权重固定；基线为原始 prompt 同一权重",
  "integrity_gates": "基线空 hook parity；每个扰动条件重新 collate 后强制校验 bbox token 对齐与序列长度预算；记录 support_box_used 原文以便复算；respace 作为文本扰动的阴性对照。",
  "acceptance_criteria": "沿用事先冻结阈值：守住 = 配对 ΔmIoU 的 95% CI 下界 > −0.01；主报告为 8 种改写模式的 Δ 与 CI 排序，并对照 respace（写法扰动）判断哪些差异来自坐标本身。",
  "conclusion_scope": "在该模型/协议/样本集下，support 帧 BBOX 文本的坐标内容是 bbox 预测的强因果输入（改错框掉点 0.12–0.36 mIoU），且表面写法扰动（respace）不影响 mIoU；但不构成跨模型/协议泛化，也不说明该先验在网络内部被使用的具体位置。R-012/R-013 的\"参考图视觉通道几乎不重要\"需与此并读：模型更像是在用 support 框文本这一空间先验 + query 图像，而非参考图的视觉内容。",
  "claim_boundary": "最多支持「在该模型、该协议、该样本集下，support 框坐标文本对 bbox 预测的因果影响有多大」；不构成跨模型/协议泛化，也不直接说明注意力层面的机制。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
