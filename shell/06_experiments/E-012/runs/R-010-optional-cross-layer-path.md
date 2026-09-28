# R-010-optional-cross-layer-path · 后续跨层路径：Reference target-grounded heads 到下游A@V读出

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
R-008 逐head通过的上游 Query/Reference target-specific heads，其目标区域 AV 扰动是否通过独立冻结的下游 A@V heads 传播到 bbox loss：clean 下游输出能否在 corrupt run 中救回损害，corrupt 下游输出能否在 clean run 中迁移损害，并且两者均强于matched-background与同层随机路径？

## 2. 目的
在 R-008 至少一个角色/逐head通过后，检验 U→D→bbox 的固定候选跨层中介，而不是要求同一 head 同时承担路由、编码与输出控制。采用双向 rescue/transfer 与 identity controls，支持或削弱具体冻结路径；不搜索完整 circuit。

**假设或预期**：若冻结上游U通过下游D传递目标特异信息，则target corruption应改变D并提高bbox CE；把同输入clean D patch进corrupt run应产生正RescueEffect，把corrupt D patch进clean run应产生正TransferEffect；二者的target-minus-background及candidate-minus-random DiD都应为正。

## 3. 方法（干预 · 对照 · 指标与判定规则）
条件触发：仅当 R-008 至少一个逐head target-specific gate通过。上游 U 只能来自R-008逐head通过列表；要求 layer(U)<layer(D)。下游 D 由独立 Discovery A@V probe按与bbox坐标loss的读出相关性冻结，使用与路径评估零重合的数据；D列表、层、rows、Top-k、阈值在任何rescue/transfer结果前锁定，禁止按路径效果反选或追加。

每个固定样本和U→D路径先运行并缓存：
Clean：无干预，保存四坐标p-1 rows的D_clean；
Target-corrupt：按R-008同一fractional GT mask移除U的目标A_jV_j，保存D_target与L_target；
Background-corrupt：按R-008同一匹配器移除等token/area或等attention-mass背景，保存D_bg与L_bg。
所有缓存绑定sample、checkpoint、layer/head、row、span与输入hash，禁止跨样本/row误patch。

路径干预：
1) clean identity：clean→clean，把D_clean写回clean run，应复现L_clean/logits；
2) corrupt identity：D_target→target-corrupt，应复现L_target/logits；
3) clean-D rescue：U target-corrupt后，在D节点将D_target替换为D_clean，得到L_rescue；
4) corrupt-D transfer：clean U运行，在D节点将D_clean替换为D_target，得到L_transfer；
5) 对matched-background corruption重复3/4；
6) 同层同数量U controls与D controls、row-shuffled D和sample-shuffled D作为路径特异对照。D节点必须固定为下游head的A@V输出、output projection前；patch只改冻结bbox rows，shape/dtype/device严格一致。

指标：UpstreamDamage UD=L_corrupt-L_clean；RescueEffect RE=L_corrupt-L_rescue；RescueFraction RF=RE/UD，仅当UD>damage_floor，否则undefined；TransferEffect TE=L_transfer-L_clean；DownstreamRelativeChange DRC=||D_corrupt-D_clean||_2/max(||D_clean||_2,norm_floor)。目标特异路径量：RE_TSD=RE_target-E_b[RE_bg,b]；TE_TSD=TE_target-E_b[TE_bg,b]；再减同层随机U/D控制得到DiD_RE与DiD_TE。可辅助报告 mediated proportion=clip(RE/UD,范围仅描述)，但UD很小时不解释。

Query→D与Reference→D分开报告；逐路径为主，冻结路径集合为补充。对sample先计算再按sequence cluster-bootstrap 95% CI，不筛baseline错误样本。必要但非充分条件：UD_target>0且DRC_target>0。中介支持要求 RE_target>0、TE_target>0、RE_TSD>0、TE_TSD>0，且DiD_RE/DiD_TE均正向CI不跨0；rescue单向通过或transfer单向通过只记部分/不对称证据。

停止规则：任一identity parity、hook coverage、U<D、缓存身份、条件coverage失败则停止该Run；target corruption不比background强时不解释rescue；不得因路径失败扩大D扫描、改变rows或追加head。

**干预与对照**：上游变量为R-008通过的Query或Reference head及target vs matched-background corruption；下游变量为独立冻结D。条件含clean、target/background corrupt、clean→clean identity、corrupt→corrupt identity、clean-D rescue、corrupt-D transfer；对照为同层random U、同层random D、row-shuffled D、sample-shuffled D。

**指标计划**：逐sample×固定U→D路径保存clean/target-corrupt/background-corrupt/rescue/transfer及D向量。主报UD、RE、TE、DRC、RE_TSD、TE_TSD、相对随机U/D的DiD_RE/DiD_TE和sequence cluster-bootstrap 95% CI；RF仅在UD>damage_floor时辅助。Query→D和Reference→D分开，逐路径为主、集合补充。

**指标计算定义**：UD=L_corrupt-L_clean；RE=L_corrupt-L_rescue；RF=RE/UD（仅UD>damage_floor）；TE=L_transfer-L_clean；DRC=||D_corrupt-D_clean||_2/max(||D_clean||_2,norm_floor)；RE_TSD=RE_target-E_b[RE_bg,b]；TE_TSD=TE_target-E_b[TE_bg,b]；DiD_RE=RE_TSD_candidate-E[RE_TSD_control]；DiD_TE=TE_TSD_candidate-E[TE_TSD_control]。damage_floor与norm_floor必须预冻结，分母无效记undefined。

**判定门槛 / no-silent-zero**：R-008逐head通过证据存在且列表/hash冻结；D来自独立Discovery probe且评估数据零重合；所有路径满足layer(U)<layer(D)；clean→clean和corrupt→corrupt logits/loss在atol/rtol内；hook每条件恰命中预期U/D/rows；D缓存sample/checkpoint/token rows/span/shape/dtype hash一致；target/background实际移除量与匹配误差齐全；所有clean/corrupt/rescue/transfer/control cell完整；damage_floor/norm_floor预冻结；不得按rescue结果反选路径。

**验收判定**：每路径records含U/D身份、四坐标rows、clean/corrupt/rescue/transfer loss、D向量变化、target/background masks、random/shuffle controls和所有分子分母；identity与coverage gate全过；summary可从records重算。固定路径中介支持需UD_target和DRC为正，并且RE_TSD、TE_TSD、DiD_RE、DiD_TE的cluster-bootstrap 95% CI均在正方向；否则仅记部分、无支持或实现失败。

**预期特征**：支持或削弱跨层协作解释，而不是要求同一个 head 同时完成路由、编码和 bbox 控制。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
沿用统一shell/analyze链；条件触发后新增薄config configs/head_screening/e012_optional_cross_layer_path.py，entrypoint计划为iploc_szy.head_screening.cross_layer_path:run_r010。公共模块需提供U端R-008 AV corruption、D端A@V capture/replace、缓存identity校验、clean/corrupt双向patch和cluster统计。config显式固定R-008 passed-head文件/hash、D discovery文件/hash、评估manifest/hash、路径列表、target/background masks、random/shuffle controls、damage_floor、norm_floor、atol/rtol、bootstrap seed/次数及输出目录。产物至少含input_manifest.json、frozen_paths.json、activation_cache_manifest.json、records.jsonl、integrity.json、summary.json。测试覆盖identity patch、U<D、缓存错配拒绝、rescue/transfer符号与undefined分母。当前仅方法登记，未实现/审核/授权。

**数据身份与构造**：复用冻结数据；上游只能来自 R-008 通过的 heads；下游必须由独立 A@V probe 在 Discovery 数据上冻结，不能根据 rescue 结果反选。

**数据规模**：按前置结果条件触发；路径数和样本数必须在执行前单独冻结，不得失败后扩大扫描。

**代码架构**：统一启动合同：shell/06_experiments/E-012/unified_execution_contract.md。所有可脚本化分析必须走 tools/run/e012_dual_role_analysis.sh → Python config → tools/launch.py(action=analyze) → tools/analyze.py → analysis.entrypoint；Shell不接收实验参数，不允许独立tee日志或绕过公共launcher。launch统一创建work_dir/logs/console-<uuid>.log；worker统一config snapshot和status.json；entrypoint只写records/integrity/summary。 条件触发后才新增薄config；复用公共path-patching模块和统一analysis日志流程。

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
- tmux: incontext-E-012-R-010-optional-cross-layer-path
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-010-optional-cross-layer-path/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-010-optional-cross-layer-path/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
rescue/transfer仍是局部、固定节点与固定rows的中介证据；patch可能产生off-manifold状态。即使双向通过，也不证明D是唯一中介、完整circuit或普遍机制；MLP、residual、其它tokens和并行heads可共同参与。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "implementation_details": "沿用统一shell/analyze链；条件触发后新增薄config configs/head_screening/e012_optional_cross_layer_path.py，entrypoint计划为iploc_szy.head_screening.cross_layer_path:run_r010。公共模块需提供U端R-008 AV corruption、D端A@V capture/replace、缓存identity校验、clean/corrupt双向patch和cluster统计。config显式固定R-008 passed-head文件/hash、D discovery文件/hash、评估manifest/hash、路径列表、target/background masks、random/shuffle controls、damage_floor、norm_floor、atol/rtol、bootstrap seed/次数及输出目录。产物至少含input_manifest.json、frozen_paths.json、activation_cache_manifest.json、records.jsonl、integrity.json、summary.json。测试覆盖identity patch、U<D、缓存错配拒绝、rescue/transfer符号与undefined分母。当前仅方法登记，未实现/审核/授权。",
  "metric_plan": "逐sample×固定U→D路径保存clean/target-corrupt/background-corrupt/rescue/transfer及D向量。主报UD、RE、TE、DRC、RE_TSD、TE_TSD、相对随机U/D的DiD_RE/DiD_TE和sequence cluster-bootstrap 95% CI；RF仅在UD>damage_floor时辅助。Query→D和Reference→D分开，逐路径为主、集合补充。",
  "data_definition": "复用冻结数据；上游只能来自 R-008 通过的 heads；下游必须由独立 A@V probe 在 Discovery 数据上冻结，不能根据 rescue 结果反选。",
  "data_scale": "按前置结果条件触发；路径数和样本数必须在执行前单独冻结，不得失败后扩大扫描。",
  "variables_controls": "上游变量为R-008通过的Query或Reference head及target vs matched-background corruption；下游变量为独立冻结D。条件含clean、target/background corrupt、clean→clean identity、corrupt→corrupt identity、clean-D rescue、corrupt-D transfer；对照为同层random U、同层random D、row-shuffled D、sample-shuffled D。",
  "metric_definition": "UD=L_corrupt-L_clean；RE=L_corrupt-L_rescue；RF=RE/UD（仅UD>damage_floor）；TE=L_transfer-L_clean；DRC=||D_corrupt-D_clean||_2/max(||D_clean||_2,norm_floor)；RE_TSD=RE_target-E_b[RE_bg,b]；TE_TSD=TE_target-E_b[TE_bg,b]；DiD_RE=RE_TSD_candidate-E[RE_TSD_control]；DiD_TE=TE_TSD_candidate-E[TE_TSD_control]。damage_floor与norm_floor必须预冻结，分母无效记undefined。",
  "integrity_gates": "R-008逐head通过证据存在且列表/hash冻结；D来自独立Discovery probe且评估数据零重合；所有路径满足layer(U)<layer(D)；clean→clean和corrupt→corrupt logits/loss在atol/rtol内；hook每条件恰命中预期U/D/rows；D缓存sample/checkpoint/token rows/span/shape/dtype hash一致；target/background实际移除量与匹配误差齐全；所有clean/corrupt/rescue/transfer/control cell完整；damage_floor/norm_floor预冻结；不得按rescue结果反选路径。",
  "expected_outcome": "支持或削弱跨层协作解释，而不是要求同一个 head 同时完成路由、编码和 bbox 控制。",
  "acceptance_criteria": "每路径records含U/D身份、四坐标rows、clean/corrupt/rescue/transfer loss、D向量变化、target/background masks、random/shuffle controls和所有分子分母；identity与coverage gate全过；summary可从records重算。固定路径中介支持需UD_target和DRC为正，并且RE_TSD、TE_TSD、DiD_RE、DiD_TE的cluster-bootstrap 95% CI均在正方向；否则仅记部分、无支持或实现失败。",
  "claim_boundary": "只有预冻结U→D路径同时通过target-over-background、clean rescue、corrupt transfer及随机/shift controls，才支持固定模型、数据、节点和rows下的跨层中介线索；不得称完整或唯一bbox circuit。",
  "audit_paths": "shell/06_experiments/E-012/dual_role_metric_contract.md sha256=bab83a1f801b158f7fbe7a027760e1e937185c439b778107e83f6ece1e3c5f06；shell/06_experiments/E-012/dual_role_target_specific_head_program.md sha256=06ad63348717efc4e9e8d6ccb893823ea4ee170a1c1385ffd92500ef0cd72a54"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
