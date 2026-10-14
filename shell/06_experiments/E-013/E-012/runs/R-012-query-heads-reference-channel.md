# R-012-query-heads-reference-channel · 同一批查询头改删参考图像通道

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
把细删靶子从 query 图像换成 reference 图像后，只留 R-011 那三份 query head 名单是否仍然显著优于同规模随机保留集合？

## 2. 目的
只改一处：清零 bbox 坐标预测行到 reference 图像视觉 token 的注意力边（R-011 清的是 query 图像那侧）。用来判断这些 head 的"充分性"是不是角色特异的，还是两个图像通道共用同一批路由头。

## 3. 方法（干预 · 对照 · 指标与判定规则）
干预：对除保留集合外的所有文本 query head，把 bbox 坐标预测行（p-1）× reference 图像视觉 token 的注意力边清零，不重归一化；其余注意力、上下文行、MLP/残差原样保留。保留名单沿用 R-011 三份 query 侧名单（旧固定组 5、双角色筛查组 5、并集 10）。条件=基线 + 只留各组（3）+ 同层同数量同规模随机保留集合（3 规模 × 3 seed = 9），共 13 条；不做 6.25%/9.38%/18.75% 档（R-011 已显示那三档两臂无差别）。指标：自由生成 bbox 的 mIoU 变化为主，teacher-forced argmax 框 IoU 为确定性辅助轴，teacher-forced 坐标 CE 作机制诊断；样本等权、按 sequence 聚类 bootstrap 95% CI。判定沿用 R-011 事先冻结的阈值（守住 = CI 下界 > −0.01）并额外报告"只留集合 − 同规模随机"的配对差与其 CI，作为与 R-011 逐格对照的依据。

**干预与对照**：保留名单（旧固定组 5 / 双角色筛查组 5 / 并集 10）× 干预通道（reference 图像；query 通道由 R-011 提供）× 同层同数量随机保留集合 3 组

**指标计划**：主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化；审计：实际干预行数/边数/移除注意力质量、格式跑偏比例、干预行数为 0 的样本比例。

**判定门槛 / no-silent-zero**：基线空 hook parity；细删只在 bbox 坐标预测行 × reference 图像视觉键上生效并逐条审计；报告实际干预行数为 0 的样本比例；保留集合与随机对照层分布对齐；生成轴与 teacher-forced 轴同时落盘。

**验收判定**：沿用 R-011 事先冻结阈值：守住 = 配对 ΔmIoU 的 cluster-bootstrap 95% CI 下界 > −0.01；另有配对量「keep_only − 同规模随机保留集合」的 CI 作为与 R-011 对照的主报告量。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
新增 configs/experiments/E-012/analysis/e012_r012_query_heads_ref_channel_step741.py 与 tools/run/analysis/e012/e012_r012_query_heads_ref_channel_step741.sh；模块 iploc_szy/head_screening/keepset_pruning.py 增加 image_role（query|reference，默认 query，reference 取 spans[0]）与 condition_grid=extreme_only。数据：R-001 冻结索引 LaSOT 50 + GOT10k 50 = 100 条（沿用同一退化样本排除项 170/178/226/227）。模型：E-009 step741，与 R-011 同一 checkpoint，可逐样本配对。名单仍只引用冻结 JSON（sha256 19153e28…）。commit 848009252db8ef8d82120a7cfb387516fe056192。

**数据规模**：100 条（LaSOT 50 + GOT10k 50），与 R-011 的 70 条快照可逐样本配对；不含 TAO。条件 13 条 × 100 条 = 1300 次生成，另加每条件 teacher-forced 前向。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/analysis/e012/e012_r012_query_heads_ref_channel_step741.sh`
- commit: `848009252db8ef8d82120a7cfb387516fe056192`
- workspace: 02
- tmux: incontext-E-012-R-012-query-heads-reference-channel
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-012-query-heads-reference-channel/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/r012-query-heads-ref-channel-step741-v1
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
细删只覆盖读出边，其余通路未动；样本仅 LaSOT+GOT10k（无 TAO）；名单在 step247 选、评测在 step741；自由生成 mIoU 有运行间噪声；本次只测极端档，不含小规模删除曲线。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "R-011 只测了 query 通道，无法区分\"这些 head 是 query 读出的充分基\"与\"它们是两个图像通道共同的读出基\"；这一格缺失会让\"角色分工\"的说法没有对照。",
  "implementation_details": "新增 configs/experiments/E-012/analysis/e012_r012_query_heads_ref_channel_step741.py 与 tools/run/analysis/e012/e012_r012_query_heads_ref_channel_step741.sh；模块 iploc_szy/head_screening/keepset_pruning.py 增加 image_role（query|reference，默认 query，reference 取 spans[0]）与 condition_grid=extreme_only。数据：R-001 冻结索引 LaSOT 50 + GOT10k 50 = 100 条（沿用同一退化样本排除项 170/178/226/227）。模型：E-009 step741，与 R-011 同一 checkpoint，可逐样本配对。名单仍只引用冻结 JSON（sha256 19153e28…）。commit 848009252db8ef8d82120a7cfb387516fe056192。",
  "metric_plan": "主指标：自由生成 bbox 的 mIoU 变化；确定性辅助轴：teacher-forced argmax 框 IoU 变化；机制诊断：teacher-forced 坐标 token 平均 CE 变化；审计：实际干预行数/边数/移除注意力质量、格式跑偏比例、干预行数为 0 的样本比例。",
  "data_scale": "100 条（LaSOT 50 + GOT10k 50），与 R-011 的 70 条快照可逐样本配对；不含 TAO。条件 13 条 × 100 条 = 1300 次生成，另加每条件 teacher-forced 前向。",
  "variables_controls": "保留名单（旧固定组 5 / 双角色筛查组 5 / 并集 10）× 干预通道（reference 图像；query 通道由 R-011 提供）× 同层同数量随机保留集合 3 组",
  "integrity_gates": "基线空 hook parity；细删只在 bbox 坐标预测行 × reference 图像视觉键上生效并逐条审计；报告实际干预行数为 0 的样本比例；保留集合与随机对照层分布对齐；生成轴与 teacher-forced 轴同时落盘。",
  "acceptance_criteria": "沿用 R-011 事先冻结阈值：守住 = 配对 ΔmIoU 的 cluster-bootstrap 95% CI 下界 > −0.01；另有配对量「keep_only − 同规模随机保留集合」的 CI 作为与 R-011 对照的主报告量。",
  "claim_boundary": "最多支持「在该模型、该样本集、细删 reference 图像读出通道的条件下，这组 query head 的读出通路是否足以维持定位性能，以及是否比同规模随机保留集合更强」；不构成整头必要性、不构成跨 checkpoint/协议泛化。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
