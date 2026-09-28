# R-016-reference-frame-replacement · 换掉参考帧图像看影响

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
保留正确的 support 框文本、只把参考帧的**图像**换成别的视频序列的帧（或涂黑），模型预测的框会受多大影响？

## 2. 目的
前面已确认：删注意力时 reference 图像通道只值 0.12 mIoU，而 support 框文本被改坏要掉 0.12–0.36。本 Run 从输入侧做最后一刀：文本完全不动、只换图像本身，用来判断模型到底有没有把"框里的东西"当外观模板用。

## 3. 方法（干预 · 对照 · 指标与判定规则）
干预：只替换 prompt 中的图像本身，文本（含 support 框坐标）一字不改。四种模式：swap_reference（参考帧换成**另一个视频序列**的帧，真实、分布内、内容错误）、swap_query（查询帧换成别的序列的帧——机制正对照，应显著崩塌）、black_reference（参考帧涂黑 512×512）、black_all（两张都涂黑，只剩框文本 → 纯符号先验下界）。条件=基线 + 4 = 5 条；样本 100（LaSOT 50 + GOT10k 50，与 R-013/R-014/R-015 同索引）。指标：自由生成 mIoU 变化为主、teacher-forced argmax 框 IoU 为确定性辅助轴、CE 为机制诊断；另记 donor 所属序列以便核对扰动生效。

**干预与对照**：图像替换模式（swap_reference / swap_query / black_reference / black_all）× 文本与权重固定；swap 的 donor 强制来自另一视频序列；基线为原图原文

**指标计划**：主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU；机制诊断：坐标 token CE；核对项：donor_cluster 与生成的框。

**判定门槛 / no-silent-zero**：基线空 hook parity；换图后重新 collate 并强制校验 bbox token 对齐与序列长度预算；swap donor 必须跨序列（否则报错）；black_query/black_all 作为机制有效性的内部对照。

**验收判定**：沿用事先冻结阈值（守住 = 配对 ΔmIoU 的 95% CI 下界 > −0.01）。判定要点：swap_query 必须显著崩塌（否则说明换图未生效）；swap_reference / black_reference 若守住，则支持"模型不使用参考图外观"。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
模块 iploc_szy/head_screening/keepset_pruning.py 新增 intervention=input_image（image_part_indexes / replace_image_parts / input_image_conditions）；换图 donor 强制跨视频序列；涂黑帧按 512×512 生成到输出目录；换图后重新 collate 并强制校验 bbox token 对齐。新增 configs/experiments/E-012/analysis/e012_r016_black_reference_step741.py 与对应 launcher。模型 E-009 step741。commit 4a7db5d1967629404485de3c75340bdfb0f96756。

**数据规模**：100 条（LaSOT 50 + GOT10k 50）；5 条件 × 100 = 500 次生成，约 40–60 分钟。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/analysis/e012/e012_r016_black_reference_step741.sh`
- commit: `4a7db5d1967629404485de3c75340bdfb0f96756`
- workspace: 02
- tmux: incontext-E-012-R-016-reference-frame-replacement
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-016-reference-frame-replacement/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/r016-image-replacement-step741-v2
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
只换图像、不改文本与权重；donor 来自同一数据集另一序列；样本 LaSOT+GOT10k；自由生成有运行间噪声。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "R-013/R-015 都是注意力层面的删除（可能被旁路绕过、也可能我们没打到关键路径）；输入侧换图是更强、更无争议的干预，缺它就无法排除\"参考图其实有用但被冗余路径救了\"这一解释。",
  "implementation_details": "模块 iploc_szy/head_screening/keepset_pruning.py 新增 intervention=input_image（image_part_indexes / replace_image_parts / input_image_conditions）；换图 donor 强制跨视频序列；涂黑帧按 512×512 生成到输出目录；换图后重新 collate 并强制校验 bbox token 对齐。新增 configs/experiments/E-012/analysis/e012_r016_black_reference_step741.py 与对应 launcher。模型 E-009 step741。commit 4a7db5d1967629404485de3c75340bdfb0f96756。",
  "metric_plan": "主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU；机制诊断：坐标 token CE；核对项：donor_cluster 与生成的框。",
  "data_scale": "100 条（LaSOT 50 + GOT10k 50）；5 条件 × 100 = 500 次生成，约 40–60 分钟。",
  "variables_controls": "图像替换模式（swap_reference / swap_query / black_reference / black_all）× 文本与权重固定；swap 的 donor 强制来自另一视频序列；基线为原图原文",
  "integrity_gates": "基线空 hook parity；换图后重新 collate 并强制校验 bbox token 对齐与序列长度预算；swap donor 必须跨序列（否则报错）；black_query/black_all 作为机制有效性的内部对照。",
  "acceptance_criteria": "沿用事先冻结阈值（守住 = 配对 ΔmIoU 的 95% CI 下界 > −0.01）。判定要点：swap_query 必须显著崩塌（否则说明换图未生效）；swap_reference / black_reference 若守住，则支持\"模型不使用参考图外观\"。",
  "conclusion_scope": "在该模型/协议/样本集下：query 帧像素是决定性输入；参考帧像素贡献约 0.10–0.16 mIoU（可复现、CI 不含 0，但比 query 帧小 4–7 倍）；support 框文本是有效先验但单独不足以定位（0.16）。与 R-013（注意力删除 −0.122）与 R-014（文本污染 0.12–0.36）在量级上互证。不构成跨模型/协议泛化。",
  "claim_boundary": "最多支持「在该模型、该协议、该样本集下，参考帧的像素内容对最终框的因果贡献有多大」；不构成跨模型/协议泛化。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
