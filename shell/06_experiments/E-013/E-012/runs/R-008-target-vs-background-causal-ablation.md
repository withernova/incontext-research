# R-008-target-vs-background-causal-ablation · Target-specific causal validation：逐head与集合、CE与自由生成

- workflow: v2 / ready_to_run / 等待执行授权
- review_status: approved
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
R-005 各冻结 selector 的 Reference heads 中，直接移除 bbox 坐标预测行上的 Reference GT A_jV_j，是否比移除面积匹配或 attention-mass 匹配的 Reference 背景 A_jV_j 更显著地损害 bbox CE 与自由生成 IoU，并且该差异是否强于 high-gradient-only、legacy 与同层随机 heads？

## 2. 目的
在严格 sequence/image-disjoint Causal split 上把 R-005 的空间/梯度候选推进到因果验证：先逐 head 检验 target-specific damage，再检验冻结 Top-3/Top-5 集合的冗余或协同，最后用自由生成评估 teacher-forced 局部效应是否影响真实 bbox；不依据 R-008 结果重新选 head。

**假设或预期**：若 combined selector 找到的是 target-grounded causal information-flow heads，则目标区域 AV removal 应产生 ΔCE_target>0，且 TargetSpecificDamage=ΔCE_target-E[ΔCE_bg]>0；这一配对差异应强于 G-only、legacy、G×T(a)、G×T(d) 与同层随机对照，并在自由生成中对应更大的 IoU 损害。

## 3. 方法（干预 · 对照 · 指标与判定规则）
前置与冻结：只使用 R-005 在 Discovery/Calibration 冻结、Confirmation 通过的 selector、阈值及 Top-3/Top-5；Causal split 与此前所有 components/图像零重合；不按 baseline correct/error、框大小或 effect 大小删样本。

干预节点：Qwen 文本 self-attention 的 post-softmax/dropout 后、A@V 前；只作用于 x1,y1,x2,y2 四坐标 token 的 p-1 prediction rows，不重新 softmax。对 head h、row r、Reference token j，用 m_j∈[0,1]：o'_{hr}=Σ_j(1-m_j)A_{hrj}V_{hj}+Σ_{j∉R}A_{hrj}V_{hj}。主干预为 m=g（fractional target removal）或等价的 AV edge scaling；另报告硬 token mask 作为敏感性分析，但不混为同一 estimand。

每个 sample×head 的固定条件：
C0 baseline；C1 empty/no-op hook；C2 remove Reference target AV；C3 remove same-token-count/area-matched background；C4 remove attention-mass-matched background；C5 remove shifted-GT null；必要时 C6 full-head/full-Reference removal 只作上界。背景 mask 仅从 Reference 非目标区域预冻结采样，匹配 tolerance、重复数和失败处理写入 config；匹配失败显式计数，不用最近似样本静默替代。

比较集合：R-005 E12-A legacy Gradient+IoU、G-only/high-gradient-only、G×T(a)、G×T(d)、combined/null-calibrated；每组固定 Top-3/Top-5；同层同数量随机 heads 用预冻结 seed 生成。先逐 head，后集合消融；逐 head 结果决定能否给单 head 结论，集合结果仅描述冗余/协同。

Teacher-forced 主指标：L0=L(C0)；ΔCE_target=L_target-L0；ΔCE_bg=L_bg-L0；TargetSpecificDamage=ΔCE_target-E_b[ΔCE_bg,b]。selector增量为 DiD_selector=TargetSpecificDamage_selector-TargetSpecificDamage_control。必须同时检验 ΔCE_target>0 与 TargetSpecificDamage>0，按 sequence cluster-bootstrap 给95% CI；对冻结的少量逐head检验报告 multiplicity-adjusted或完整未校正区间，禁止只报显著者。

自由生成外部效度：每一条件从独立、清空的 KV cache 开始，冻结 decode 参数与 bbox parser。记录 IoU、mIoU、IoU≥0.5、invalid/multiple/truncated/文本退化率。令 DamageIoU_target=IoU_0-IoU_target，DamageIoU_bg=IoU_0-IoU_bg，GenerationTargetSpecificDamage=DamageIoU_target-E_b[DamageIoU_bg,b]（等价于 ΔIoU_bg-ΔIoU_target，前提是ΔIoU=IoU_condition-IoU_0）。

判定：某逐head只有在 empty-hook通过、目标实际被移除、ΔCE_target正向CI不跨0、TargetSpecificDamage正向CI不跨0、且相对同层random/high-gradient-only的DiD为正时，才支持固定范围内 target-specific causal head。selector集合需另行满足同样方向；自由生成一致则增加外部效度，不一致时保留teacher-forced局部结论并报告。

**干预与对照**：固定变量为 selector与Top-k；干预条件为baseline、empty hook、fractional target AV removal、area/token-count matched background、attention-mass matched background、shifted-GT null及可选full-head上界。对照为legacy、high-gradient-only、T(a)-only、T(d)-only、同层同数量random；所有条件复用同一输入和冻结模型，生成使用独立KV cache。

**指标计划**：逐head为主、Top-3/Top-5集合为补充。主报 ΔCE_target、各背景ΔCE、TargetSpecificDamage及相对 high-gradient-only/legacy/random 的 difference-in-differences，sequence cluster-bootstrap 95% CI、有效/总/匹配失败计数。自由生成报 DamageIoU_target/bg、GenerationTargetSpecificDamage、mIoU、IoU≥0.5及解析/文本退化率。selector覆盖 legacy、G、G×T(a)、G×T(d)、combined。

**指标计算定义**：o'_{hr}=Σ_j(1-m_j)A_{hrj}V_{hj}+Σ_{j∉R}A_{hrj}V_{hj}；ΔCE_target=L_target-L0；ΔCE_bg=L_bg-L0；TSD=ΔCE_target-E_b[ΔCE_bg,b]；DiD=TSD_candidate-E[TSD_control]。自由生成定义 DamageIoU_target=IoU_0-IoU_target，DamageIoU_bg=IoU_0-IoU_bg，GTSD=DamageIoU_target-E_b[DamageIoU_bg,b]。集合 synergy/descriptive interaction 可记录为 ΔCE_set-Σ_hΔCE_h，但不用于给单head因果结论。

**判定门槛 / no-silent-zero**：R-004通过且R-005列表/阈值/hash冻结；Causal与Discovery/Confirmation零component和图像重合；四坐标p-1 rows完整且不含格式token；C0/C1 logits在冻结atol/rtol内一致；每个hook命中预期layer/head/row/token数；记录requested/actual removed occupancy、token count、attention mass、AV norm；背景匹配tolerance与不可行数完整；所有selector/head/condition coverage完整；生成每条件独立cache、同decode配置、冻结parser；不得事后换head、换mask或删不利样本。

**验收判定**：逐sample×head×condition records及集合records可重算；每种selector/Top-k均有baseline、target、两类matched background、null、random controls；报告实际移除量和匹配误差、N_total/N_valid/N_unmatched、cluster-bootstrap CI。单head target-specific支持必须同时满足ΔCE_target和TSD正向CI、优于controls且empty hook通过；否则归为仅相关或未支持。

**预期特征**：把每个角色归为：因果目标特异、仅空间/梯度相关、或未支持。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
沿用唯一 shell/analyze 启动链；新增薄 config configs/head_screening/e012_target_vs_background_causal_ablation.py，entrypoint计划为iploc_szy.head_screening.target_vs_background_ablation:run_r008。公共hook复用R-004的post-softmax A@V前重放，并扩展fractional mask、area/token-count与attention-mass background matcher、逐条件独立forward/generation。config显式固定R-005 frozen_heads/threshold文件及hash、Causal manifest/hash、mask规则、匹配tolerance/repeats、Top-k、random seed、bootstrap、decode/parser和输出目录；缺值拒绝运行。产物：input_manifest.json、frozen_heads.json、intervention_masks.jsonl、teacher_forced_records.jsonl、generation_records.jsonl、integrity.json、summary.json和selector/head图表。测试需覆盖no-op parity、精确edge scaling、target/background匹配、独立KV cache、metric符号与样本计数。当前仅完成方法登记，尚未实现/审核/授权执行。

**数据身份与构造**：master manifest 的 Causal split，与 Discovery/Confirmation component 互斥；只进入 R-007 通过的角色和冻结 heads；不按 baseline 对错删样本。

**数据规模**：建议约占独立 components 的30%；实际数量由 master split 固定。

**代码架构**：统一启动合同：shell/06_experiments/E-012/unified_execution_contract.md。所有可脚本化分析必须走 tools/run/e012_dual_role_analysis.sh → Python config → tools/launch.py(action=analyze) → tools/analyze.py → analysis.entrypoint；Shell不接收实验参数，不允许独立tee日志或绕过公共launcher。launch统一创建work_dir/logs/console-<uuid>.log；worker统一config snapshot和status.json；entrypoint只写records/integrity/summary。 干预逻辑放公共包，Run只通过config声明角色、heads与conditions。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `<PI_STEWARD_PREPARE_RUNTIME_COMMAND>`
- commit: ``
- workspace: 02
- tmux: incontext-E-012-R-008-target-vs-background-causal-ablation
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-008-target-vs-background-causal-ablation/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-008-target-vs-background-causal-ablation/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
局部 AV removal 只覆盖指定bbox/decode rows及固定模型/数据；可能受残差、MLP、并行heads和非线性补偿影响。集合效应不能分配给单head；自由生成失败可能来自parser或文本退化，必须分开报告。通过也不证明identity selectivity、完整或唯一circuit。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "implementation_details": "沿用唯一 shell/analyze 启动链；新增薄 config configs/head_screening/e012_target_vs_background_causal_ablation.py，entrypoint计划为iploc_szy.head_screening.target_vs_background_ablation:run_r008。公共hook复用R-004的post-softmax A@V前重放，并扩展fractional mask、area/token-count与attention-mass background matcher、逐条件独立forward/generation。config显式固定R-005 frozen_heads/threshold文件及hash、Causal manifest/hash、mask规则、匹配tolerance/repeats、Top-k、random seed、bootstrap、decode/parser和输出目录；缺值拒绝运行。产物：input_manifest.json、frozen_heads.json、intervention_masks.jsonl、teacher_forced_records.jsonl、generation_records.jsonl、integrity.json、summary.json和selector/head图表。测试需覆盖no-op parity、精确edge scaling、target/background匹配、独立KV cache、metric符号与样本计数。当前仅完成方法登记，尚未实现/审核/授权执行。",
  "metric_plan": "逐head为主、Top-3/Top-5集合为补充。主报 ΔCE_target、各背景ΔCE、TargetSpecificDamage及相对 high-gradient-only/legacy/random 的 difference-in-differences，sequence cluster-bootstrap 95% CI、有效/总/匹配失败计数。自由生成报 DamageIoU_target/bg、GenerationTargetSpecificDamage、mIoU、IoU≥0.5及解析/文本退化率。selector覆盖 legacy、G、G×T(a)、G×T(d)、combined。",
  "data_definition": "master manifest 的 Causal split，与 Discovery/Confirmation component 互斥；只进入 R-007 通过的角色和冻结 heads；不按 baseline 对错删样本。",
  "data_scale": "建议约占独立 components 的30%；实际数量由 master split 固定。",
  "variables_controls": "固定变量为 selector与Top-k；干预条件为baseline、empty hook、fractional target AV removal、area/token-count matched background、attention-mass matched background、shifted-GT null及可选full-head上界。对照为legacy、high-gradient-only、T(a)-only、T(d)-only、同层同数量random；所有条件复用同一输入和冻结模型，生成使用独立KV cache。",
  "metric_definition": "o'_{hr}=Σ_j(1-m_j)A_{hrj}V_{hj}+Σ_{j∉R}A_{hrj}V_{hj}；ΔCE_target=L_target-L0；ΔCE_bg=L_bg-L0；TSD=ΔCE_target-E_b[ΔCE_bg,b]；DiD=TSD_candidate-E[TSD_control]。自由生成定义 DamageIoU_target=IoU_0-IoU_target，DamageIoU_bg=IoU_0-IoU_bg，GTSD=DamageIoU_target-E_b[DamageIoU_bg,b]。集合 synergy/descriptive interaction 可记录为 ΔCE_set-Σ_hΔCE_h，但不用于给单head因果结论。",
  "integrity_gates": "R-004通过且R-005列表/阈值/hash冻结；Causal与Discovery/Confirmation零component和图像重合；四坐标p-1 rows完整且不含格式token；C0/C1 logits在冻结atol/rtol内一致；每个hook命中预期layer/head/row/token数；记录requested/actual removed occupancy、token count、attention mass、AV norm；背景匹配tolerance与不可行数完整；所有selector/head/condition coverage完整；生成每条件独立cache、同decode配置、冻结parser；不得事后换head、换mask或删不利样本。",
  "expected_outcome": "把每个角色归为：因果目标特异、仅空间/梯度相关、或未支持。",
  "acceptance_criteria": "逐sample×head×condition records及集合records可重算；每种selector/Top-k均有baseline、target、两类matched background、null、random controls；报告实际移除量和匹配误差、N_total/N_valid/N_unmatched、cluster-bootstrap CI。单head target-specific支持必须同时满足ΔCE_target和TSD正向CI、优于controls且empty hook通过；否则归为仅相关或未支持。",
  "claim_boundary": "只有冻结逐head在held-out Causal split上表现为target removal损害、相对matched background的TSD及相对controls的DiD均稳定为正，才可称固定范围内 target-specific causal visual information-flow head；集合通过只能支持该冻结集合。",
  "audit_paths": "shell/06_experiments/E-012/dual_role_metric_contract.md sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06；shell/06_experiments/E-012/dual_role_target_specific_head_program.md sha256=06ad63348717efc4e9e8d6ccb893823ea4ee170a1c1385ffd92500ef0cd72a54"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
