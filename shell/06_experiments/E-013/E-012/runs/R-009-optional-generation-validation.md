# R-009-optional-generation-validation · 双角色目标特异干预的自由生成外部效度

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
目标区域因果消融相对匹配背景，是否会降低自由生成 bbox IoU 或增加无效输出？

## 2. 目的
条件触发的后续验证：检查 R-008 在 teacher-forced bbox loss 上的结果，是否也会改变模型自由生成的 bbox。它不属于首轮选头主线。

**假设或预期**：若 R-008 的目标特异贡献影响实际定位，目标移除应比匹配背景移除带来更负的 IoU 变化；也允许只影响 CE 而不影响生成。

## 3. 方法（干预 · 对照 · 指标与判定规则）
**干预与对照**：沿用 Query/Reference 目标与 mass-matched 背景条件；同层随机 heads；整头消融只作最大必要性上界。生成时采用 bbox-state detector 或所有 decode rows 干预，必须在实现前由人类二选一。

**指标计划**：全体冻结样本为分母，先逐样本再等权汇总及component-cluster 95%CI；另报bbox changed、归一化坐标L1、invalid/multi-box/truncation/text-changed rate。Q/R分报；background/control不增加独立n。

**指标计算定义**：详细实现合同：shell/06_experiments/E-012/dual_role_metric_contract.md（e012.dual-role-head-metrics/v1）。Run 页面自动列出的旧 query→query/ bbox含标点 Experiment 指标仅为历史指标，不控制本 Run。 冻结唯一bbox parser：恰好一个合法0–1000 xyxy且x2>x1,y2>y1为valid；不裁剪/修复/挑最好框；invalid IoU=0并计invalid rate。DeltaIoU=IoU_condition-IoU_base；GenerationTargetSpecificDamage=mean_s DeltaIoU_bg_s-DeltaIoU_target，越高表示目标移除造成更大IoU下降。 指标合同文件：shell/06_experiments/E-012/dual_role_metric_contract.md；contract_sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06。

**判定门槛 / no-silent-zero**：GT从annotation预冻结变换，不从目标文本反解；每条件新KV cache；在线bbox-state detector或all-decode-row必须人类预选并冻结；无干预replay一致；保存原始文本、parser状态和invalid原因。

**验收判定**：所有样本/条件完整；报告GenerationTargetSpecificDamage、DeltaIoU及95%CI和全部退化率；invalid不静默删除。

**预期特征**：判断因果贡献是否具有自由生成外部效度。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
**数据身份与构造**：复用 R-008 的冻结 Causal split、heads 和 controls；所有 baseline 错误样本保留，只作预声明分层。

**数据规模**：与 R-008 相同；每条件独立 greedy generation 和独立 KV cache。

**代码架构**：统一启动合同：shell/06_experiments/E-012/unified_execution_contract.md。所有可脚本化分析必须走 tools/run/e012_dual_role_analysis.sh → Python config → tools/launch.py(action=analyze) → tools/analyze.py → analysis.entrypoint；Shell不接收实验参数，不允许独立tee日志或绕过公共launcher。launch统一创建work_dir/logs/console-<uuid>.log；worker统一config snapshot和status.json；entrypoint只写records/integrity/summary。 条件触发后才新增薄config；若需generation公共worker扩展，也不得新增专用日志流程。

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
- tmux: incontext-E-012-R-009-optional-generation-validation
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-009-optional-generation-validation/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-009-optional-generation-validation/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
自由生成没有天然 teacher-forced bbox 行，不同在线干预方案对应不同结论边界。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "metric_plan": "全体冻结样本为分母，先逐样本再等权汇总及component-cluster 95%CI；另报bbox changed、归一化坐标L1、invalid/multi-box/truncation/text-changed rate。Q/R分报；background/control不增加独立n。",
  "data_definition": "复用 R-008 的冻结 Causal split、heads 和 controls；所有 baseline 错误样本保留，只作预声明分层。",
  "data_scale": "与 R-008 相同；每条件独立 greedy generation 和独立 KV cache。",
  "variables_controls": "沿用 Query/Reference 目标与 mass-matched 背景条件；同层随机 heads；整头消融只作最大必要性上界。生成时采用 bbox-state detector 或所有 decode rows 干预，必须在实现前由人类二选一。",
  "metric_definition": "详细实现合同：shell/06_experiments/E-012/dual_role_metric_contract.md（e012.dual-role-head-metrics/v1）。Run 页面自动列出的旧 query→query/ bbox含标点 Experiment 指标仅为历史指标，不控制本 Run。 冻结唯一bbox parser：恰好一个合法0–1000 xyxy且x2>x1,y2>y1为valid；不裁剪/修复/挑最好框；invalid IoU=0并计invalid rate。DeltaIoU=IoU_condition-IoU_base；GenerationTargetSpecificDamage=mean_s DeltaIoU_bg_s-DeltaIoU_target，越高表示目标移除造成更大IoU下降。 指标合同文件：shell/06_experiments/E-012/dual_role_metric_contract.md；contract_sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06。",
  "integrity_gates": "GT从annotation预冻结变换，不从目标文本反解；每条件新KV cache；在线bbox-state detector或all-decode-row必须人类预选并冻结；无干预replay一致；保存原始文本、parser状态和invalid原因。",
  "expected_outcome": "判断因果贡献是否具有自由生成外部效度。",
  "acceptance_criteria": "所有样本/条件完整；报告GenerationTargetSpecificDamage、DeltaIoU及95%CI和全部退化率；invalid不静默删除。",
  "claim_boundary": "这是 E-012 的选头与机制诊断，不修改 Claim。通过空间筛选只能称候选；只有独立确认和目标对背景因果消融都通过，才可在固定模型、数据和干预范围内称目标特异 head。",
  "audit_paths": "shell/06_experiments/E-012/dual_role_metric_contract.md sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06；shell/06_experiments/E-012/dual_role_target_specific_head_program.md sha256=06ad63348717efc4e9e8d6ccb893823ea4ee170a1c1385ffd92500ef0cd72a54"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
