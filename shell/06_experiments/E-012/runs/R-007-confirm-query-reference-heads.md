# R-007-confirm-query-reference-heads · Query/Reference 目标区域对质量匹配背景的局部因果干预

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
冻结的 Query Head 和 Reference Head，能否在独立样本上继续同时满足“对 bbox 重要”和“有效 visual contribution 主要来自目标区域”？

## 2. 目的
在没有参与选头的新样本上确认两组候选。这里不再选 head，只检查 R-005 的 Query Heads 和 R-006 的 Reference Heads 是否各自复现。

**假设或预期**：可信候选应在独立样本上仍优于同图匹配背景和同层随机 heads；Query 与 Reference 分别判定，可以一方通过、另一方失败。

## 3. 方法（干预 · 对照 · 指标与判定规则）
**干预与对照**：分别评估 Query candidates 和 Reference candidates；每组都使用其对应 GT、样本内匹配背景和同层同数量随机 head controls；candidate set 聚合为主，逐 head 为辅助。

**指标计划**：Q/R分别PASS：mean SetTargetVsNull的95%CI下界>0，且mean CandidateMinusControl的95%CI下界>0，完整性gate通过。候选set聚合为主；逐head仅次要并BH-FDR。bootstrap单位是sequence/shared-image component，随机head sets不是独立n。

**指标计算定义**：详细实现合同：shell/06_experiments/E-012/dual_role_metric_contract.md（e012.dual-role-head-metrics/v1）。Run 页面自动列出的旧 query→query/ bbox含标点 Experiment 指标仅为历史指标，不控制本 Run。 对冻结集合H_r，每样本 SetTargetVsNull(n,r)=mean_{head∈H_r}TargetVsNullLog(n,head,r)；同层同数量随机集合用同式；CandidateMinusControl(n,r)=候选集合值-随机集合均值。主汇总是样本等权mean/median、connected-component cluster-bootstrap 95%CI和正值比例。 指标合同文件：shell/06_experiments/E-012/dual_role_metric_contract.md；contract_sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06。

**判定门槛 / no-silent-zero**：Confirmation与Discovery component零重合；candidate/control文件在结果前冻结；candidate set空则该角色not-testable而非补头；保存n_total/n_valid/n_invalid及所有原因；同一cluster记录共同bootstrap。

**验收判定**：Q/R分别输出SetTargetVsNull、CandidateMinusControl的mean/median/95%CI/正值比例/n及PASS/FAIL/NOT_TESTABLE；所有结果由records可重算。

**预期特征**：确认哪些 Query/Reference 候选可以进入因果消融；失败者保留为 exploratory，不再称确定的 head。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
**数据身份与构造**：master manifest 的 Confirmation split；与 Discovery 和后续因果 split 按视频/共享图像 component 互斥。只读取 R-005/R-006 冻结列表，禁止重排或补头。

**数据规模**：建议约占独立 components 的30%；实际数量由 master split 固定。

**代码架构**：统一启动合同：shell/06_experiments/E-012/unified_execution_contract.md。所有可脚本化分析必须走 tools/run/e012_dual_role_analysis.sh → Python config → tools/launch.py(action=analyze) → tools/analyze.py → analysis.entrypoint；Shell不接收实验参数，不允许独立tee日志或绕过公共launcher。launch统一创建work_dir/logs/console-<uuid>.log；worker统一config snapshot和status.json；entrypoint只写records/integrity/summary。 后续薄config只读冻结candidate文件并调用公共entrypoint。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: ``
- commit: ``
- workspace: 02
- tmux: incontext-E-012-R-007-confirm-query-reference-heads
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-007-confirm-query-reference-heads/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-007-confirm-query-reference-heads/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
独立复现仍然是一阶贡献证据，不等于移除该目标区域后 bbox 一定变差。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "metric_plan": "Q/R分别PASS：mean SetTargetVsNull的95%CI下界>0，且mean CandidateMinusControl的95%CI下界>0，完整性gate通过。候选set聚合为主；逐head仅次要并BH-FDR。bootstrap单位是sequence/shared-image component，随机head sets不是独立n。",
  "data_definition": "master manifest 的 Confirmation split；与 Discovery 和后续因果 split 按视频/共享图像 component 互斥。只读取 R-005/R-006 冻结列表，禁止重排或补头。",
  "data_scale": "建议约占独立 components 的30%；实际数量由 master split 固定。",
  "variables_controls": "分别评估 Query candidates 和 Reference candidates；每组都使用其对应 GT、样本内匹配背景和同层同数量随机 head controls；candidate set 聚合为主，逐 head 为辅助。",
  "metric_definition": "详细实现合同：shell/06_experiments/E-012/dual_role_metric_contract.md（e012.dual-role-head-metrics/v1）。Run 页面自动列出的旧 query→query/ bbox含标点 Experiment 指标仅为历史指标，不控制本 Run。 对冻结集合H_r，每样本 SetTargetVsNull(n,r)=mean_{head∈H_r}TargetVsNullLog(n,head,r)；同层同数量随机集合用同式；CandidateMinusControl(n,r)=候选集合值-随机集合均值。主汇总是样本等权mean/median、connected-component cluster-bootstrap 95%CI和正值比例。 指标合同文件：shell/06_experiments/E-012/dual_role_metric_contract.md；contract_sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06。",
  "integrity_gates": "Confirmation与Discovery component零重合；candidate/control文件在结果前冻结；candidate set空则该角色not-testable而非补头；保存n_total/n_valid/n_invalid及所有原因；同一cluster记录共同bootstrap。",
  "expected_outcome": "确认哪些 Query/Reference 候选可以进入因果消融；失败者保留为 exploratory，不再称确定的 head。",
  "acceptance_criteria": "Q/R分别输出SetTargetVsNull、CandidateMinusControl的mean/median/95%CI/正值比例/n及PASS/FAIL/NOT_TESTABLE；所有结果由records可重算。",
  "claim_boundary": "这是 E-012 的选头与机制诊断，不修改 Claim。通过空间筛选只能称候选；只有独立确认和目标对背景因果消融都通过，才可在固定模型、数据和干预范围内称目标特异 head。",
  "audit_paths": "shell/06_experiments/E-012/dual_role_metric_contract.md sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06；shell/06_experiments/E-012/dual_role_target_specific_head_program.md sha256=06ad63348717efc4e9e8d6ccb893823ea4ee170a1c1385ffd92500ef0cd72a54"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
