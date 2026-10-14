# R-013-reference-key-source-sweep · 扫哪类来源 token 读到参考图会崩

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
把「某一类来源 token → reference 图像视觉 token」的注意力全部清零（不分 head），哪一类来源被删掉时定位性能会崩？

## 2. 目的
不再按 head 分组，改为扫来源 token 本身：全部行 / prompt 行 / 答案行 / 文本行 / bbox 坐标预测行 / 图像 pad 行 / reference 自身行 / query 图像行，各删一条通道，看哪一条是定位读出的命脉。

## 3. 方法（干预 · 对照 · 指标与判定规则）
干预：对全部 1152 个文本 query head，清零「来源行 → reference 图像视觉 token」的注意力边，不重归一化；来源行逐组扫描（all/prompt/answer/text/target_rows/image/reference_image/query_image），其余通路不动。生成阶段映射：all、text 在 prefill 与解码都干预；prompt、image、reference_image、query_image 只在 prefill 干预（这些行解码时不重算）；answer 只在解码干预；target_rows 用括号前缀规则。条件=基线 + 8 组 = 9 条；样本 100 条（LaSOT 50 + GOT10k 50）。指标：自由生成 mIoU 变化为主，teacher-forced argmax 框 IoU 为确定性辅助轴，teacher-forced 坐标 CE 为机制诊断。判定沿用事先冻结阈值（守住 = 配对 ΔmIoU 的 95% CI 下界 > −0.01），并报告各来源组的 Δ 与 CI 排序。

**干预与对照**：来源行分组（8 类，全部 head 一律删除对应的 reference 图像键）× 靶子图像固定 reference；基线为同一样本同一权重不干预

**指标计划**：主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化；审计：每条件实际干预行数/边数/移除注意力质量、以及生成阶段 prefill 与解码各自的行数。

**判定门槛 / no-silent-zero**：基线空 hook parity；来源行分类与实际干预行数逐条审计（prompt 类组必须在 prefill 生效、answer 组在解码生效）；报告实际干预行数为 0 的样本比例；生成轴与 teacher-forced 轴同时落盘。

**验收判定**：沿用事先冻结阈值：守住 = 配对 ΔmIoU 的 95% CI 下界 > −0.01；主报告为 8 类来源组的 Δ 与 CI 排序（哪一类删除后崩塌）。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
模块 iploc_szy/head_screening/keepset_pruning.py 新增 scope_rows/RowPlan/generation_mode 与 intervention=row_scope；新增 configs/experiments/E-012/analysis/e012_r013_reference_key_source_sweep_step741.py 与对应 launcher。靶子图像固定 reference（取 spans[0]），名单文件仅作溯源引用，本 Run 不使用 head 分组。数据：R-001 冻结索引 LaSOT 50 + GOT10k 50；模型 E-009 step741（与 R-011/R-012 同 checkpoint，可逐样本配对）。commit 3d7c4c3cdd71d5da021c2950462e757aa453b14f。

**数据规模**：100 条（LaSOT 50 + GOT10k 50）；9 条件 × 100 条 = 900 次生成，成本低（约 1 小时）。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/analysis/e012/e012_r013_reference_key_source_sweep_step741.sh`
- commit: `3d7c4c3cdd71d5da021c2950462e757aa453b14f`
- workspace: 02
- tmux: incontext-E-012-R-013-reference-key-source-sweep
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-013-reference-key-source-sweep/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/r013-reference-key-source-sweep-step741-v1
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
只删到 reference 图像键这一侧；target_rows 组是 R-011/R-012 的同一行口径但改为全 head；样本仅 LaSOT+GOT10k；自由生成 mIoU 有运行间噪声。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "R-011/R-012 只测了 bbox 坐标行的读出（且按 head 分组），无法区分\"定位读出到底依赖哪一类来源 token 去读 reference 图像\"；这条缺口决定了\"参考图信息在哪一步进入 bbox 预测\"的解释。",
  "implementation_details": "模块 iploc_szy/head_screening/keepset_pruning.py 新增 scope_rows/RowPlan/generation_mode 与 intervention=row_scope；新增 configs/experiments/E-012/analysis/e012_r013_reference_key_source_sweep_step741.py 与对应 launcher。靶子图像固定 reference（取 spans[0]），名单文件仅作溯源引用，本 Run 不使用 head 分组。数据：R-001 冻结索引 LaSOT 50 + GOT10k 50；模型 E-009 step741（与 R-011/R-012 同 checkpoint，可逐样本配对）。commit 3d7c4c3cdd71d5da021c2950462e757aa453b14f。",
  "metric_plan": "主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化；审计：每条件实际干预行数/边数/移除注意力质量、以及生成阶段 prefill 与解码各自的行数。",
  "data_scale": "100 条（LaSOT 50 + GOT10k 50）；9 条件 × 100 条 = 900 次生成，成本低（约 1 小时）。",
  "variables_controls": "来源行分组（8 类，全部 head 一律删除对应的 reference 图像键）× 靶子图像固定 reference；基线为同一样本同一权重不干预",
  "integrity_gates": "基线空 hook parity；来源行分类与实际干预行数逐条审计（prompt 类组必须在 prefill 生效、answer 组在解码生效）；报告实际干预行数为 0 的样本比例；生成轴与 teacher-forced 轴同时落盘。",
  "acceptance_criteria": "沿用事先冻结阈值：守住 = 配对 ΔmIoU 的 95% CI 下界 > −0.01；主报告为 8 类来源组的 Δ 与 CI 排序（哪一类删除后崩塌）。",
  "claim_boundary": "最多支持「在该模型、该样本集下，哪一类来源 token 读到 reference 图像对 bbox 预测是必要的」；不构成跨 checkpoint/协议泛化，也不直接给出 head 级结论。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
