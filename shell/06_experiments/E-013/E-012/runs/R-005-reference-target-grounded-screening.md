# R-005-reference-target-grounded-screening · Reference target-grounded screening：C_R、T(a)、T(d) 与冻结确认

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
哪些 Reference heads 不仅对四个 bbox 坐标字段的 teacher-forced loss 重要，而且其 Reference attention 与实际 prediction-relevant visual contribution 都优先来自 Reference GT；这种标准能否保留高 T(a)、低 IoU 的局部 head，并在 sequence/image-disjoint Confirmation 上复现？

## 2. 目的
在 R-004 真实 checkpoint 梯度门禁通过后，按 E12-A→E 的可归因递进比较 legacy Gradient+IoU、gradient-only、G×T(a)、G×T(d)、G√(T(a)T(d)) 与 null-calibrated 完整 selector。Discovery/Calibration 负责定阈值与冻结 Top-k，Confirmation 只复核、不重选；本 Run 只产生 target-grounded Reference Head 候选，不作因果声明。

**假设或预期**：若 IoU≥0.5 会误删局部但有效的 Reference heads，则高 G+高 T(a)+低 IoU（例如讨论中的局部型类别，而非预先指定某个结果 head）应被 T(a) selector 保留。若 contribution localization 提供 attention map 之外的信息，则 T(a) 与 T(d) 不完全等价，且完整 selector 在独立 Confirmation 上应比 gradient-only 和 legacy selector 更稳定。

## 3. 方法（干预 · 对照 · 指标与判定规则）
前置：R-004 必须在同一模型/checkpoint、四坐标 subtokens、真实 Q/R span-grid 上通过 A·∂L/∂A=<∂L/∂o,A V>、empty-hook 与 signed finite difference；否则停止。

数据：一次性冻结 master manifest，并按 sequence/video 与共享任一 Reference/Query 图像的 connected component 切分 Discovery+Calibration 和 Confirmation，component 零重合；按数据集与目标尺寸分层，不按 baseline 正误筛样本。

逐 sample n、head h、Reference token j、坐标 prediction row r 记录：
1) Prediction relevance / contribution：e_{nhrj}=A_{nhrj}·∂L_coord/∂A_{nhrj}=<∂L_coord/∂o_{nhr}, A_{nhrj}V_{nhj}>；c_{nhj}=Σ_r |e_{nhrj}|；G_{nh}=C^R_{nh}=Σ_{j∈R}c_{nhj}。L_coord 是 x1,y1,x2,y2 四字段全部 subtokens 的平均 CE，纯括号/逗号/空白不进入主损失。
2) Reference 内 attention distribution：a_{nhj}=Σ_r A_{nhrj}/Σ_{k∈R,r}A_{nhrk}。
3) contribution distribution：d_{nhj}=c_{nhj}/(Σ_{k∈R}c_{nhk})。
4) fractional GT occupancy g_{nj}∈[0,1]。对 x∈{a,d}：M(x)=Σ_j x_j g_j，b=mean_j(g_j)，u=max_j(g_j)，T_raw(x)=(M(x)-b)/(u-b)，T(x)=clip(T_raw(x),0,1)。u=b、attention mass=0 或 C_R=0 时记 undefined，不用 epsilon 伪造空间分布。

按固定顺序做 selector ablation：
E12-A legacy：高 G 且 support/GT IoU≥0.5；
E12-B attention：S^a=G_tilde·T(a)；
E12-C contribution：S^d=G_tilde·T(d)；
E12-D combined：S=1[G≥τ_G]·G_tilde·sqrt(T(a)T(d))，并同时要求 T(a)≥τ_a、T(d)≥τ_d；
E12-E calibrated：在 D 上使用 Calibration 中 same-size shifted-GT、radial-position-matched null 与 fixed-center negative control 冻结 τ_G/τ_a/τ_d；
对照：G-only/high-gradient-only、同层随机同数量 heads。不得从 A 直接跳到 D，也不得用下游性能回调筛选阈值。

IoU、Coverage、attention entropy、retained-mass components 只描述 whole-object/local-part/multi-part/diffuse phenotype，不作为有效性硬门槛。先画 sample×head 及 head-mean 的 x=T(a), y=T(d) 二维图，显式统计四象限，特别记录 T(a)高/T(d)低。

跨样本汇总：S_bar_h=(1/N)Σ_n S_{nh}；F_h(τ)=(1/N)Σ_n 1[S_{nh}≥τ]。报告 overall、dataset-wise、small/medium/large target、sequence-wise bootstrap；Discovery 冻结 Top-3/Top-5（允许少于或为零），Confirmation 只按冻结阈值和列表复核资格率、排名稳定性与 selector Jaccard，不补头。

**干预与对照**：主角色仅 Reference；同一 A/V/A@V 与四坐标 prediction rows。变量是 selector（legacy、G、G×T(a)、G×T(d)、combined、null-calibrated）；对照为 high-gradient-only、同层随机、same-size shifted GT、radial-position-matched null、fixed center。IoU 只作 phenotype。Discovery/Calibration 与 Confirmation 严格隔离。

**指标计划**：主指标为 G=C_R、T_raw(a)/T(a)、T_raw(d)/T(d)、S^a、S^d、S_combined、S_bar_h 与 F_h(τ)。辅助空间 phenotype 为 fractional IoU、Coverage、Entropy、Components。比较 A/B/C/D/E 五阶段及 G-only/同层随机；先逐样本算再样本等权，sequence cluster-bootstrap 给 95% CI。Confirmation 报冻结 Top-3/Top-5 的资格通过率、undefined率、dataset/size 分层和集合 Jaccard，不重新排序补头。

**指标计算定义**：e_{nhrj}=A_{nhrj}∂L_coord/∂A_{nhrj}=<∂L_coord/∂o_{nhr},A_{nhrj}V_{nhj}>；c_{nhj}=Σ_r|e_{nhrj}|；G_{nh}=C^R_{nh}=Σ_{j∈R}c_{nhj}；a_{nhj}=Σ_rA_{nhrj}/Σ_{k∈R,r}A_{nhrk}；d_{nhj}=c_{nhj}/C^R_{nh}。对 x∈{a,d}：T_raw(x)=(Σ_jx_jg_j-mean(g))/(max(g)-mean(g))，T(x)=clip(T_raw(x),0,1)。S^a=G_tilde T(a)，S^d=G_tilde T(d)，S=1[G≥τ_G]G_tilde√(T(a)T(d)) 且资格要求 T(a)≥τ_a、T(d)≥τ_d。S_bar_h=N^{-1}Σ_nS_{nh}；F_h(τ)=N^{-1}Σ_n1[S_{nh}≥τ]。

**判定门槛 / no-silent-zero**：R-004 real-checkpoint gate先通过；四坐标字段全部subtokens且排除纯格式token；Q/R顺序、span、merged grid、fractional occupancy一致；36×32=1152 heads完整；同一post-softmax A和A@V节点；先逐row取|e|再求和；N_total/valid/undefined逐原因齐全；null与阈值在看Confirmation和ablation前冻结；Discovery/Calibration/Confirmation component零重合；输入、checkpoint、records和阈值文件均哈希；零候选是合法结果。

**验收判定**：records 能重算每个 sample×head 的 A、G/C_R、c/d 摘要、T_raw/T、undefined原因、phenotype及所有 selector 分数；二维 T(a)-T(d) 图和四象限计数完整；A–E 排名与 high-gradient-only/random 对照齐全；Calibration 冻结阈值与 Top-3/Top-5；Confirmation 不重选并报告资格率、稳定性、分层结果及 95% CI。只有筛选候选，不称 causal head。

**预期特征**：冻结Top-3/Top-5 Target-grounded Reference Head候选，或在固定标准下得到零候选；这里只形成screening候选，不作因果Claim。

### 已注册指标定义
- **bbox梯度绝对贡献（逐head样本均值）** (`bbox_grad_abs_contrib_mean`)：C_lh = mean_n sum_{p,j in query} |A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]|；teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据；每条边先取绝对值，再按样本求和，最后样本等权平均；不除以视觉token数 / Qwen3-VL-8B+LoRA、36层x32 query heads=1152 heads；20条先导与690条扩展两轮eval子集
- **bbox梯度signed贡献（逐head样本均值）** (`bbox_grad_signed_contrib_mean`)：S_lh = mean_n sum_{p,j in query} A_lh[p-1,j] * dL_bbox/dA_lh[p-1,j]；对post-softmax指定边做不重归一化乘法缩放时的一阶CE导数方向；本轮有限差分与反传符号不一致，方向暂不可用于增强/抑制决策；样本等权平均 / 同上1152 heads；20条与690条两轮eval子集
- **平均bbox token CE** (`bbox_token_ce_mean`)：mean_n mean_i CE(logits[p_i-1], token[p_i])；teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率；样本等权平均 / 690条（LaSOT 300/GOT10k 90/TAO 300）与20条先导
- **头部排名集合Jaccard** (`head_ranking_jaccard`)：|A∩B|/|A∪B|；不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升；对固定Top-k集合直接计算 / 20条vs690条、690条对旧固定5 head；Top-5/Top-10/Top-50
- **有限差分与反传符号一致** (`finite_difference_sign_agreement`)：sign(central_difference) == sign(signed_derivative)；首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过；首样本单一诊断，不参与排名 / 690条run首样本dataset_index=0 L24H25，epsilon=0.02

## 4. 详细实现细节
统一入口 tools/run/e012_dual_role_analysis.sh → tools/launch.py → tools/analyze.py → reference_target_collector:run_r005_collect_and_screen。继承 e012_bbox_gradient_initial.py 的模型、manifest、collator 与训练集排除；R-005 基类冻结 split/threshold/null/bootstrap 协议。自动构造 sequence/image-disjoint 三段划分，跳过无效 bbox，生成 GT-only null masks；逐样本写 records.jsonl 与 probe NPZ，结束后输出 thresholds、frozen_heads、ranking、SVG、integrity 和 summary。真实 A/V 代数门禁首样本最大误差 0.0；聚焦测试 42 passed。

**数据身份与构造**：使用一个预先冻结的master manifest，按sequence及共享Reference/Query图像connected component划分Discovery/Calibration与Confirmation，二者零重合。具体路径、哈希、整数配额在提交执行审核前填入config；不从归档Run或旧结果推断。

**数据规模**：扫描36×32 heads。Discovery/Calibration用于null阈值和排序，Confirmation只复核冻结规则与列表；整数样本数在manifest audit后冻结，零候选允许完成。

**代码架构**：实际代码位于review_worktree_dual_role_heads：prompting/coordinates.py解析四个数值char spans；datasets/collator.py将rendered offsets映射为coordinate_token_positions；head_screening/probes.py验证并转换到p-1 rows；dual_role_metrics.py计算C_R/T(a)/T(d)；reference_target_screening.py完成离线排序、资格与split冻结确认。GPU采集独立入口需在manifest和校准参数冻结后继续接入。

**实现摘要**：已完成真实 Qwen3-VL GPU collector、R-005 target-grounded 筛选和冻结 Confirmation。collector 在 eager post-softmax、A@V 前捕获 A/V/梯度，并在原生 GPU dtype 上验证 A·∂L/∂A 与 head-output VJP；配置通过两层继承只暴露 checkpoint_path 与 screening_counts，manifest/split SHA-256 运行时生成。attempt-003 已完成 590 条。

- 公共包：`iploc_szy/head_screening`
- 入口：`iploc_szy.head_screening.reference_target_collector:run_r005_collect_and_screen`
- 配置：`configs/head_screening/e012_reference_target_grounded_screening.py`
- Shell launcher：`tools/run/e012_dual_role_analysis.sh`
- 复用模块：tools/launch.py, tools/analyze.py, iploc_szy/head_screening/bbox_gradient.py, iploc_szy/head_screening/r004_real_chain_rule.py
- 新增模块：iploc_szy/head_screening/reference_target_collector.py, iploc_szy/head_screening/reference_target_screening.py, iploc_szy/head_screening/dual_role_metrics.py, configs/_base_/e012_reference_target_screening.py, configs/head_screening/e012_reference_target_grounded_screening.py
- 测试：tests/test_reference_target_collector.py, tests/test_reference_target_screening.py, tests/test_dual_role_metrics.py, tests/test_coordinate_token_alignment.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/liuwenchu/projects/IPLoc/mechanism/iploc-szy/tools/run/e012_dual_role_analysis.sh configs/head_screening/e012_reference_target_grounded_screening.py`
- commit: `0e090bb820d854b0aa8204d69e5b9a3df18a3386`
- workspace: 02
- tmux: incontext-E-012-R-005-reference-target-grounded-screening
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-005-reference-target-grounded-screening/logs/console-<uuid>.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-005-reference-target-grounded-screening
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
R-005 使用绝对贡献 C_R=Σ|A·∂L_coord/∂A| 衡量 Reference 边局部敏感度，再以 Reference GT fractional occupancy 计算 T(a)、T(d) 并进行 pooled-null calibration。Confirmation 不重新排名。L17H24 的冻结综合分数均值最高（0.05049，95% CI [0.03696,0.06699]）；L21H17 严格达标频率最高且跨 GOT10k/LaSOT/TAO 较稳定（0.556/0.583/0.550）；L17H27 总体频率 0.475，低于预冻结 0.5 门槛。gradient-only Top heads 位于 L26/L29，而 target-grounded 候选位于 L17/L21，结果与角色分离假设相容，但未检验因果方向。

## 简短局限
teacher-forced 四坐标 prediction rows；梯度取绝对贡献，不保留正负方向；筛选与冻结确认只支持当前 checkpoint 和三个 eval 子集上的候选稳定性，不证明增强/抑制方向、因果必要性或完整跨层 circuit。方向性与 target-vs-background 因果效应留给 R-008。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "implementation_summary": "已完成真实 Qwen3-VL GPU collector、R-005 target-grounded 筛选和冻结 Confirmation。collector 在 eager post-softmax、A@V 前捕获 A/V/梯度，并在原生 GPU dtype 上验证 A·∂L/∂A 与 head-output VJP；配置通过两层继承只暴露 checkpoint_path 与 screening_counts，manifest/split SHA-256 运行时生成。attempt-003 已完成 590 条。",
  "implementation_details": "统一入口 tools/run/e012_dual_role_analysis.sh → tools/launch.py → tools/analyze.py → reference_target_collector:run_r005_collect_and_screen。继承 e012_bbox_gradient_initial.py 的模型、manifest、collator 与训练集排除；R-005 基类冻结 split/threshold/null/bootstrap 协议。自动构造 sequence/image-disjoint 三段划分，跳过无效 bbox，生成 GT-only null masks；逐样本写 records.jsonl 与 probe NPZ，结束后输出 thresholds、frozen_heads、ranking、SVG、integrity 和 summary。真实 A/V 代数门禁首样本最大误差 0.0；聚焦测试 42 passed。",
  "metric_plan": "主指标为 G=C_R、T_raw(a)/T(a)、T_raw(d)/T(d)、S^a、S^d、S_combined、S_bar_h 与 F_h(τ)。辅助空间 phenotype 为 fractional IoU、Coverage、Entropy、Components。比较 A/B/C/D/E 五阶段及 G-only/同层随机；先逐样本算再样本等权，sequence cluster-bootstrap 给 95% CI。Confirmation 报冻结 Top-3/Top-5 的资格通过率、undefined率、dataset/size 分层和集合 Jaccard，不重新排序补头。",
  "data_definition": "使用一个预先冻结的master manifest，按sequence及共享Reference/Query图像connected component划分Discovery/Calibration与Confirmation，二者零重合。具体路径、哈希、整数配额在提交执行审核前填入config；不从归档Run或旧结果推断。",
  "data_scale": "扫描36×32 heads。Discovery/Calibration用于null阈值和排序，Confirmation只复核冻结规则与列表；整数样本数在manifest audit后冻结，零候选允许完成。",
  "variables_controls": "主角色仅 Reference；同一 A/V/A@V 与四坐标 prediction rows。变量是 selector（legacy、G、G×T(a)、G×T(d)、combined、null-calibrated）；对照为 high-gradient-only、同层随机、same-size shifted GT、radial-position-matched null、fixed center。IoU 只作 phenotype。Discovery/Calibration 与 Confirmation 严格隔离。",
  "metric_definition": "e_{nhrj}=A_{nhrj}∂L_coord/∂A_{nhrj}=<∂L_coord/∂o_{nhr},A_{nhrj}V_{nhj}>；c_{nhj}=Σ_r|e_{nhrj}|；G_{nh}=C^R_{nh}=Σ_{j∈R}c_{nhj}；a_{nhj}=Σ_rA_{nhrj}/Σ_{k∈R,r}A_{nhrk}；d_{nhj}=c_{nhj}/C^R_{nh}。对 x∈{a,d}：T_raw(x)=(Σ_jx_jg_j-mean(g))/(max(g)-mean(g))，T(x)=clip(T_raw(x),0,1)。S^a=G_tilde T(a)，S^d=G_tilde T(d)，S=1[G≥τ_G]G_tilde√(T(a)T(d)) 且资格要求 T(a)≥τ_a、T(d)≥τ_d。S_bar_h=N^{-1}Σ_nS_{nh}；F_h(τ)=N^{-1}Σ_n1[S_{nh}≥τ]。",
  "integrity_gates": "R-004 real-checkpoint gate先通过；四坐标字段全部subtokens且排除纯格式token；Q/R顺序、span、merged grid、fractional occupancy一致；36×32=1152 heads完整；同一post-softmax A和A@V节点；先逐row取|e|再求和；N_total/valid/undefined逐原因齐全；null与阈值在看Confirmation和ablation前冻结；Discovery/Calibration/Confirmation component零重合；输入、checkpoint、records和阈值文件均哈希；零候选是合法结果。",
  "expected_outcome": "冻结Top-3/Top-5 Target-grounded Reference Head候选，或在固定标准下得到零候选；这里只形成screening候选，不作因果Claim。",
  "acceptance_criteria": "records 能重算每个 sample×head 的 A、G/C_R、c/d 摘要、T_raw/T、undefined原因、phenotype及所有 selector 分数；二维 T(a)-T(d) 图和四象限计数完整；A–E 排名与 high-gradient-only/random 对照齐全；Calibration 冻结阈值与 Top-3/Top-5；Confirmation 不重选并报告资格率、稳定性、分层结果及 95% CI。只有筛选候选，不称 causal head。",
  "conclusion_scope": "可冻结 L17H24、L17H27、L21H17 作为 R-008 的 Reference target-grounded 候选，其中按 0.5 confirmation frequency 门槛优先 L17H24 与 L21H17；不得据此宣称 head 因果必要、增强方向或跨层中介。",
  "claim_boundary": "R-005最多支持 frozen target-grounded Reference Head candidates，以及 Target Preference 是否相对 legacy IoU 保留局部候选；即使 Confirmation 复现，也不能称 target-grounded causal visual information-flow head。",
  "artifacts": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-005-reference-target-grounded-screening/attempt-003/summary.json；frozen_heads.json；ranking.csv；target_preference_a_vs_d.svg；records.json；probe/*.npz",
  "audit_paths": "/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-005-reference-target-grounded-screening/attempt-003/status.json；integrity.json；input_manifest.json；split_assignments.json；summary.json"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
