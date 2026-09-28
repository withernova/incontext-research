# R-004-contribution-calculation-check · Reference contribution 链式法则与梯度正确性门禁

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-05fc6928ba6c6e3a10f6e147 / failed
- spec_drift_fields（批准后有改动）：acceptance_criteria, implementation_details, implementation_ref, implementation_summary, integrity_gates, metric_definition, purpose, research_question, variant

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
同一 post-softmax A 与同一 head-output 节点上，Reference edge 的 A·∂L_coord/∂A 是否与 <∂L_coord/∂o,AV> 数值一致，并与小幅 AV 移除的有限差分一致？

## 2. 目的
在进入筛选前验证 Reference visual contribution 的代数等价、bbox prediction-row hook、AV 重放和 signed finite difference；本 Run 不选择 head。

**假设或预期**：如果 hook、bbox 预测行、Query/Reference token 范围和梯度链路都正确，同一贡献用两种方式计算应一致；对目标区域做微小缩放时，反传方向也应与有限差分一致。

## 3. 方法（干预 · 对照 · 指标与判定规则）
**干预与对照**：分别检查 Query 全图、Query 目标/背景、Reference 全图、Reference 目标/背景；主分析只用四个 bbox 坐标 token 的预测行，括号和标点另报；包含无干预 hook、两种独立贡献计算和多个固定 epsilon 的有限差分。

**指标计划**：先逐样本/层/head/坐标prediction-row/区域计算，再汇总；不生成Top-k。R-004通过需要：e与e_value、FD与signed derivative、empty hook、Q/R span-grid-GT occupancy 均达到实现前 required config 冻结的容差。epsilon集合、容差、样本/head数无默认值，缺失即拒绝运行。

**指标计算定义**：主损失为四个坐标字段全部 subtokens 的平均 CE。e_rj^h=A_rj^h·∂L_coord/∂A_rj^h=<∂L_coord/∂o_r^h,A_rj^hV_j^h>；跨bbox rows的token贡献为c_j^h=Σ_r|e_rj^h|。小幅移除AV→(1-ε)AV的导数为-e；完整置零不要求一阶近似。

**判定门槛 / no-silent-zero**：两路计算必须取同一post-softmax A、同一A@V前head output和同一L_coord；空hook重放一致；Q/R span、merged grid、坐标subtokens与p-1行完整；有限差分只对signed导数；任何门禁失败停止R005。

**验收判定**：内核级代数与有限差分记录可重算；真实checkpoint上8–16个冻结样本、少量预冻结heads通过两路代数容差、empty-hook和small-ε signed有限差分。合成检查通过不能替代真实模型门禁。

**预期特征**：确认后续选头指标可以使用，或明确暴露计算错误并停止。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
check_reference_chain_rule.py对8组固定合成输入分别在FP64/FP32验证A·dL/dA与<dL/do,AV>，并验证epsilon=1e-3/1e-2的AV移除有限差分。dual_role_metrics.py提供坐标行校验、逐edge贡献、C_R、T(a)、T(d)及undefined处理。

**数据身份与构造**：从后续拟用数据中预先冻结一个小型跨数据集检查集。只检查实现，不根据结果挑样本或挑 head；同一视频和共享图像不得跨后续数据 split。

**数据规模**：小型 correctness smoke；具体样本数、head 数和 epsilon 在代码方案提交审核前冻结。

**代码架构**：统一启动合同：shell/06_experiments/E-012/unified_execution_contract.md。所有可脚本化分析必须走 tools/run/e012_dual_role_analysis.sh → Python config → tools/launch.py(action=analyze) → tools/analyze.py → analysis.entrypoint；Shell不接收实验参数，不允许独立tee日志或绕过公共launcher。launch统一创建work_dir/logs/console-<uuid>.log；worker统一config snapshot和status.json；entrypoint只写records/integrity/summary。 当前已实现公共骨架、fail-closed config和纯指标原语；真实Qwen hook/科学worker尚未实现，不能标implementation-ready。

**实现摘要**：已完成Qwen3-VL eager-attention内核级链式法则检查与Reference空间指标原语。合成检查通过；真实checkpoint worker仍未完成，因此R004保持为未完成的真实模型门禁。

- 公共包：`iploc_szy/head_screening`
- 入口：`iploc_szy.head_screening.dual_role_metrics:run_r004_scaffold`
- 配置：`configs/head_screening/e012_contribution_calculation_check.py`
- Shell launcher：`tools/run/e012_dual_role_analysis.sh`
- 复用模块：tools/launch.py, tools/analyze.py, iploc_szy/run_snapshot.py
- 新增模块：iploc_szy/head_screening/dual_role_metrics.py, tests/check_reference_chain_rule.py
- 测试：tests/test_dual_role_metrics.py, tests/check_reference_chain_rule.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_dual_role_analysis.sh configs/head_screening/e012_contribution_calculation_check.py`
- commit: ``
- workspace: 02
- tmux: incontext-E-012-R-004-contribution-calculation-check
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-004-contribution-calculation-check/logs/console-<uuid>.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-004-contribution-calculation-check
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
当前结果只覆盖已安装attention内核的合成Q/K/V与token CE；未覆盖真实图像、LoRA checkpoint、真实bbox行、BF16/GPU和GT occupancy。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "implementation_summary": "已完成Qwen3-VL eager-attention内核级链式法则检查与Reference空间指标原语。合成检查通过；真实checkpoint worker仍未完成，因此R004保持为未完成的真实模型门禁。",
  "implementation_details": "check_reference_chain_rule.py对8组固定合成输入分别在FP64/FP32验证A·dL/dA与<dL/do,AV>，并验证epsilon=1e-3/1e-2的AV移除有限差分。dual_role_metrics.py提供坐标行校验、逐edge贡献、C_R、T(a)、T(d)及undefined处理。",
  "metric_plan": "先逐样本/层/head/坐标prediction-row/区域计算，再汇总；不生成Top-k。R-004通过需要：e与e_value、FD与signed derivative、empty hook、Q/R span-grid-GT occupancy 均达到实现前 required config 冻结的容差。epsilon集合、容差、样本/head数无默认值，缺失即拒绝运行。",
  "data_definition": "从后续拟用数据中预先冻结一个小型跨数据集检查集。只检查实现，不根据结果挑样本或挑 head；同一视频和共享图像不得跨后续数据 split。",
  "data_scale": "小型 correctness smoke；具体样本数、head 数和 epsilon 在代码方案提交审核前冻结。",
  "variables_controls": "分别检查 Query 全图、Query 目标/背景、Reference 全图、Reference 目标/背景；主分析只用四个 bbox 坐标 token 的预测行，括号和标点另报；包含无干预 hook、两种独立贡献计算和多个固定 epsilon 的有限差分。",
  "metric_definition": "主损失为四个坐标字段全部 subtokens 的平均 CE。e_rj^h=A_rj^h·∂L_coord/∂A_rj^h=<∂L_coord/∂o_r^h,A_rj^hV_j^h>；跨bbox rows的token贡献为c_j^h=Σ_r|e_rj^h|。小幅移除AV→(1-ε)AV的导数为-e；完整置零不要求一阶近似。",
  "integrity_gates": "两路计算必须取同一post-softmax A、同一A@V前head output和同一L_coord；空hook重放一致；Q/R span、merged grid、坐标subtokens与p-1行完整；有限差分只对signed导数；任何门禁失败停止R005。",
  "expected_outcome": "确认后续选头指标可以使用，或明确暴露计算错误并停止。",
  "acceptance_criteria": "内核级代数与有限差分记录可重算；真实checkpoint上8–16个冻结样本、少量预冻结heads通过两路代数容差、empty-hook和small-ε signed有限差分。合成检查通过不能替代真实模型门禁。",
  "claim_boundary": "这是 E-012 的选头与机制诊断，不修改 Claim。通过空间筛选只能称候选；只有独立确认和目标对背景因果消融都通过，才可在固定模型、数据和干预范围内称目标特异 head。",
  "audit_paths": "shell/06_experiments/E-012/diagnostics/R004_chain_rule_kernel_20260914.json；shell/06_experiments/E-012/diagnostics/R004_chain_rule_kernel_20260914.md；shell/06_experiments/E-012/implementation/tests/check_reference_chain_rule.py；shell/06_experiments/E-012/implementation/tests/test_dual_role_metrics.py"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
