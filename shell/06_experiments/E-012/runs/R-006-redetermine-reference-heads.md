# R-006-redetermine-reference-heads · 冻结 Query/Reference 候选的独立目标贡献确认

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
哪些 head 不仅对 bbox 预测重要，而且真正影响 bbox loss 的 Reference visual contribution 主要来自 Reference 目标区域？

## 2. 目的
重新确定 Reference Head。方法与 Query Run 完全对称，只把视觉角色、GT 和背景对照换为 Reference 图像。

**假设或预期**：若存在可信 Reference Head，它应同时具备：较高 bbox-loss relevance、较高 Reference visual contribution、目标区域贡献高于 Reference 匹配背景，并能在 discovery 重采样中稳定出现。

## 3. 方法（干预 · 对照 · 指标与判定规则）
**干预与对照**：扫描全部36×32 heads；只把主视觉角色换成 Reference。保存 Q/R/text-other 全部分区；使用 Reference GT、面积/形状匹配背景、目标邻近环带和 Query 坐标投影对照。所有参数和阈值与 R-005 对称。

**指标计划**：聚合和选择顺序与R-005逐项相同：样本内计算→样本等权→Top-M relevance pool→target-vs-null/logTCE/bootstrap gate→固定排序→最多K_head且允许零候选。所有M/K/null/bootstrap参数必须与R-005相同。

**指标计算定义**：详细实现合同：shell/06_experiments/E-012/dual_role_metric_contract.md（e012.dual-role-head-metrics/v1）。Run 页面自动列出的旧 query→query/ bbox含标点 Experiment 指标仅为历史指标，不控制本 Run。 与R-005完全同式但r=R：C_role在Reference keys求和；C_target/C_bg使用Reference GT fractional occupancy；TCR、logTCE、TargetVsNullLog使用Reference背景null。禁止继续使用旧公式中j∈query的固定范围。 指标合同文件：shell/06_experiments/E-012/dual_role_metric_contract.md；contract_sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06。

**判定门槛 / no-silent-zero**：L_coord不含格式token；Reference span/grid/GT occupancy完整；Q/R/text-other贡献均保存；Reference null预冻结；1152 heads齐全；不得借用Query排名或降低门槛；invalid和零分母显式记录。

**验收判定**：与R-005对称的all_heads、reference_candidates、bootstrap、records/summary/integrity齐全并可重算；候选含三层证据和输入哈希；零候选可完成。

**预期特征**：得到冻结的 Reference Head 候选及逐 head 三层证据，或得出当前标准下没有 Reference Head 候选。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
**数据身份与构造**：与 R-005 使用同一个 master manifest 的同一 Discovery split，以便公平比较；这只共享 discovery 数据，不使用 R-005 的 Query 排名来挑 Reference heads。

**数据规模**：与 R-005 完全相同的 Discovery 样本。

**代码架构**：统一启动合同：shell/06_experiments/E-012/unified_execution_contract.md。所有可脚本化分析必须走 tools/run/e012_dual_role_analysis.sh → Python config → tools/launch.py(action=analyze) → tools/analyze.py → analysis.entrypoint；Shell不接收实验参数，不允许独立tee日志或绕过公共launcher。launch统一创建work_dir/logs/console-<uuid>.log；worker统一config snapshot和status.json；entrypoint只写records/integrity/summary。 必须与R-005复用同一entrypoint，只通过config visual_role=reference切换；不得复制算法或Shell。

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
- tmux: incontext-E-012-R-006-redetermine-reference-heads
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-006-redetermine-reference-heads/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-006-redetermine-reference-heads/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
这些 head 是 discovery 候选，尚未独立复现，也未证明因果性或 identity routing。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "metric_plan": "聚合和选择顺序与R-005逐项相同：样本内计算→样本等权→Top-M relevance pool→target-vs-null/logTCE/bootstrap gate→固定排序→最多K_head且允许零候选。所有M/K/null/bootstrap参数必须与R-005相同。",
  "data_definition": "与 R-005 使用同一个 master manifest 的同一 Discovery split，以便公平比较；这只共享 discovery 数据，不使用 R-005 的 Query 排名来挑 Reference heads。",
  "data_scale": "与 R-005 完全相同的 Discovery 样本。",
  "variables_controls": "扫描全部36×32 heads；只把主视觉角色换成 Reference。保存 Q/R/text-other 全部分区；使用 Reference GT、面积/形状匹配背景、目标邻近环带和 Query 坐标投影对照。所有参数和阈值与 R-005 对称。",
  "metric_definition": "详细实现合同：shell/06_experiments/E-012/dual_role_metric_contract.md（e012.dual-role-head-metrics/v1）。Run 页面自动列出的旧 query→query/ bbox含标点 Experiment 指标仅为历史指标，不控制本 Run。 与R-005完全同式但r=R：C_role在Reference keys求和；C_target/C_bg使用Reference GT fractional occupancy；TCR、logTCE、TargetVsNullLog使用Reference背景null。禁止继续使用旧公式中j∈query的固定范围。 指标合同文件：shell/06_experiments/E-012/dual_role_metric_contract.md；contract_sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06。",
  "integrity_gates": "L_coord不含格式token；Reference span/grid/GT occupancy完整；Q/R/text-other贡献均保存；Reference null预冻结；1152 heads齐全；不得借用Query排名或降低门槛；invalid和零分母显式记录。",
  "expected_outcome": "得到冻结的 Reference Head 候选及逐 head 三层证据，或得出当前标准下没有 Reference Head 候选。",
  "acceptance_criteria": "与R-005对称的all_heads、reference_candidates、bootstrap、records/summary/integrity齐全并可重算；候选含三层证据和输入哈希；零候选可完成。",
  "claim_boundary": "这是 E-012 的选头与机制诊断，不修改 Claim。通过空间筛选只能称候选；只有独立确认和目标对背景因果消融都通过，才可在固定模型、数据和干预范围内称目标特异 head。",
  "audit_paths": "shell/06_experiments/E-012/dual_role_metric_contract.md sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06；shell/06_experiments/E-012/dual_role_target_specific_head_program.md sha256=06ad63348717efc4e9e8d6ccb893823ea4ee170a1c1385ffd92500ef0cd72a54"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
