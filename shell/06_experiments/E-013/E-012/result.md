# E-012 · 实验结果

## 运行汇总（survey-tool 管理）
### 历史未分组 (`legacy`)
| Run | Variant | Seed | 状态 | 指标摘要 |
|---|---|---:|---|---|
| [R-001-bbox-gradient-initial](runs/R-001-bbox-gradient-initial.md) | bbox 梯度初筛：指定 checkpoint 与三数据集 eval 样本 | 20260910 | draft | bbox梯度绝对贡献（逐head样本均值）=0.44119940996170043 CE*prob（n=20）；bbox梯度绝对贡献（逐head样本均值）=0.2949101964011788 CE*prob（n=20）；平均bbox token CE=1.2585759192705155 nats（n=20）；头部排名集合Jaccard=0.6666666666666666 ratio（n=20） |
| [R-001-bbox-gradient-halffull](runs/R-001-bbox-gradient-halffull.md) | bbox 梯度初筛扩展：690 条三数据集 eval 样本（R-001 产物补充登记） | 20260910 | draft | bbox梯度绝对贡献（逐head样本均值）=0.4672896169989869 CE*prob（n=690）；bbox梯度绝对贡献（逐head样本均值）=0.34787769309123573 CE*prob（n=690）；平均bbox token CE=1.3126453584518984 nats（n=690）；头部排名集合Jaccard=0.6666666666666666 ratio（n=690）；头部排名集合Jaccard=0.8181818181818182 ratio（n=690）；头部排名集合Jaccard=0.0 ratio（n=690）；有限差分与反传符号一致=False bool（n=1） |
| [R-002-two-stage-head-path-patching-smoke](runs/R-002-two-stage-head-path-patching-smoke.md) | 两阶段 head 协作：跨层路径 patching smoke | 20260912 | draft | （尚无结构化观测） |
| [R-003-zero-query-attention-head-path-patching](runs/R-003-zero-query-attention-head-path-patching.md) | 直接抹除 query attention 的两阶段 head 路径测试 | 20260912 | draft | （尚无结构化观测） |
| [gradient-gated-spatial-frequency-r001-v2](runs/gradient-gated-spatial-frequency-r001-v2.md) | query 图像：梯度候选与空间频率选头 | 20260910 | draft | 头部排名集合Jaccard=0.17647058823529413 ratio（n=686） |
| [reference-gradient-gated-spatial-frequency-r001-v1](runs/reference-gradient-gated-spatial-frequency-r001-v1.md) | reference 图像：梯度候选与空间频率选头 | 20260910 | draft | 头部排名集合Jaccard=0.1111111111111111 ratio（n=690） |
| [R-004-contribution-calculation-check](runs/R-004-contribution-calculation-check.md) | Reference contribution 链式法则与梯度正确性门禁 |  | failed | （尚无结构化观测） |
| [R-005-reference-target-grounded-screening](runs/R-005-reference-target-grounded-screening.md) | Reference target-grounded screening：C_R、T(a)、T(d) 与冻结确认 |  | completed | （尚无结构化观测） |
| [R-006-redetermine-reference-heads](runs/R-006-redetermine-reference-heads.md) | 冻结 Query/Reference 候选的独立目标贡献确认 |  | draft | （尚无结构化观测） |
| [R-007-confirm-query-reference-heads](runs/R-007-confirm-query-reference-heads.md) | Query/Reference 目标区域对质量匹配背景的局部因果干预 |  | draft | （尚无结构化观测） |
| [R-008-target-vs-background-causal-ablation](runs/R-008-target-vs-background-causal-ablation.md) | Target-specific causal validation：逐head与集合、CE与自由生成 |  | approved | （尚无结构化观测） |
| [R-009-optional-generation-validation](runs/R-009-optional-generation-validation.md) | 双角色目标特异干预的自由生成外部效度 |  | draft | （尚无结构化观测） |
| [R-010-optional-cross-layer-path](runs/R-010-optional-cross-layer-path.md) | 后续跨层路径：Reference target-grounded heads 到下游A@V读出 |  | draft | （尚无结构化观测） |
| [R-011-query-keepset-large-pruning](runs/R-011-query-keepset-large-pruning.md) | 只留选中注意力头的大幅裁剪曲线 |  | approved | （尚无结构化观测） |
| [R-012-query-heads-reference-channel](runs/R-012-query-heads-reference-channel.md) | 同一批查询头改删参考图像通道 |  | draft | （尚无结构化观测） |
| [R-013-reference-key-source-sweep](runs/R-013-reference-key-source-sweep.md) | 扫哪类来源 token 读到参考图会崩 |  | draft | （尚无结构化观测） |
| [R-014-support-box-probe](runs/R-014-support-box-probe.md) | 强行改写参考帧框坐标的影响 |  | completed | （尚无结构化观测） |
| [R-015-query-key-control](runs/R-015-query-key-control.md) | 正面对照：删查询图键是否崩塌 |  | draft | （尚无结构化观测） |
| [R-016-reference-frame-replacement](runs/R-016-reference-frame-replacement.md) | 换掉参考帧图像看影响 |  | completed | （尚无结构化观测） |


## 指标观测（survey-tool 管理）
### R-001-bbox-gradient-initial · bbox梯度绝对贡献（逐head样本均值）
- 值：0.44119940996170043 CE*prob
- 样本数：20
- 不确定性：std_absolute=0.126357；signed>0占比30.0%
- 指标含义：teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据
- 本轮解释：20条先导absolute第1；signed=-0.024392
- 来源/产物：results/R-001-bbox-gradient-initial/summary.json ranking[0] L26H25

### R-001-bbox-gradient-initial · bbox梯度绝对贡献（逐head样本均值）
- 值：0.2949101964011788 CE*prob
- 样本数：20
- 不确定性：std_absolute=0.616294（大于均值，样本波动大）
- 指标含义：teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据
- 本轮解释：20条第2；690条扩展中该head排第3
- 来源/产物：summary.json ranking[1] L21H31

### R-001-bbox-gradient-initial · 平均bbox token CE
- 值：1.2585759192705155 nats
- 样本数：20
- 不确定性：—
- 指标含义：teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率
- 本轮解释：仅loss量级；两轮CE不可作性能升降比较
- 来源/产物：results/R-001-bbox-gradient-initial/summary.json mean_bbox_ce

### R-001-bbox-gradient-initial · 头部排名集合Jaccard
- 值：0.6666666666666666 ratio
- 样本数：20
- 不确定性：Top-10=0.818182
- 指标含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 本轮解释：与690条扩展Top-5交集4/6
- 来源/产物：results/R-001-bbox-gradient-halffull/comparison.json overlaps.5.initial_jaccard

### R-001-bbox-gradient-halffull · bbox梯度绝对贡献（逐head样本均值）
- 值：0.4672896169989869 CE*prob
- 样本数：690
- 不确定性：样本间 std_absolute=0.216616（非均值CI）；signed>0 样本占比39.4%；仅absolute排名
- 指标含义：teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据
- 本轮解释：三个数据集均排第1；signed=-0.031100，方向未通过有限差分校验，不能据此增强
- 来源/产物：results/R-001-bbox-gradient-halffull/summary.json ranking[0] L26H25

### R-001-bbox-gradient-halffull · bbox梯度绝对贡献（逐head样本均值）
- 值：0.34787769309123573 CE*prob
- 样本数：690
- 不确定性：std_absolute=0.221661；signed>0占比53.9%
- 指标含义：teacher-forced bbox token平均CE对指定query->query视觉注意力边的局部敏感度绝对量；只表示当前输入下的敏感度大小，不是因果必要性，也不是增强方向证据
- 本轮解释：LaSOT/GOT10k/TAO 名次 2/2/3；signed=+0.048569
- 来源/产物：results/R-001-bbox-gradient-halffull/summary.json ranking[1] L24H13

### R-001-bbox-gradient-halffull · 平均bbox token CE
- 值：1.3126453584518984 nats
- 样本数：690
- 不确定性：分数据集 LaSOT=1.408200(n300)/GOT10k=1.286599(n90)/TAO=1.224905(n300)
- 指标含义：teacher-forced query bbox片段（含标点）平均交叉熵，仅表示损失量级，不是IoU或定位准确率
- 本轮解释：仅loss量级，不是IoU或定位准确率
- 来源/产物：results/R-001-bbox-gradient-halffull/summary.json mean_bbox_ce

### R-001-bbox-gradient-halffull · 头部排名集合Jaccard
- 值：0.6666666666666666 ratio
- 样本数：690
- 不确定性：Top-10=0.818182；Top-50=0.818182
- 指标含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 本轮解释：20条与690条 Top-5 交集4/6；20条是690子集，属扩样一致性而非独立重复
- 来源/产物：results/R-001-bbox-gradient-halffull/comparison.json overlaps.5.initial_jaccard

### R-001-bbox-gradient-halffull · 头部排名集合Jaccard
- 值：0.8181818181818182 ratio
- 样本数：690
- 不确定性：—
- 指标含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 本轮解释：Top-10 交集9/11
- 来源/产物：comparison.json overlaps.10.initial_jaccard

### R-001-bbox-gradient-halffull · 头部排名集合Jaccard
- 值：0.0 ratio
- 样本数：690
- 不确定性：Top-50 交集=3
- 指标含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 本轮解释：与旧固定5 head（E-011 step1482）的Top-5/Top-10交集为0；只能说头部排序不同，不能说旧head完全无贡献
- 来源/产物：comparison.json overlaps.5/10.old_intersection_count=0

### R-001-bbox-gradient-halffull · 有限差分与反传符号一致
- 值：False bool
- 样本数：1
- 不确定性：—
- 指标含义：首样本指定边±epsilon缩放的中央差分是否与反传signed导数同号；本轮为false，说明梯度方向链路校验未通过
- 本轮解释：central_difference=+0.392975 vs signed=-0.112898，relative_error=1.287289：梯度方向校验未通过，absolute排名仅为未验证观察
- 来源/产物：summary.json checks.finite_difference：L24H25, eps=0.02

### gradient-gated-spatial-frequency-r001-v2 · 头部排名集合Jaccard
- 值：0.17647058823529413 ratio
- 样本数：686
- 不确定性：固定 Top-10 集合；交集3、并集17
- 指标含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 本轮解释：query 空间频率 Top-10 与 R-001 纯梯度 Top-10 的集合重合，仅用于选择差异诊断。
- 来源/产物：R-001-bbox-gradient-halffull Top-10 与本 Run summary.json selected_heads

### reference-gradient-gated-spatial-frequency-r001-v1 · 头部排名集合Jaccard
- 值：0.1111111111111111 ratio
- 样本数：690
- 不确定性：固定 Top-10 集合；交集2、并集18
- 指标含义：不同样本子集或旧固定head集合在固定Top-k上的重合度，用于稳定性观察，不证明因果或泛化提升
- 本轮解释：reference-image 与 query-image 空间频率 Top-10 的集合重合，仅用于视觉角色选择差异诊断。
- 来源/产物：query Run 与本 Run summary.json selected_heads


## 结果摘要（survey-tool 管理）
（待登记）

## 对 Claims 的影响（survey-tool 管理）
（待人工判断；不会自动提升 Claim）

## 局限性（survey-tool 管理）
（待补充）

## 详细审计正文（canonical）
### 登记范围与当前结论（2026-09-11）

本次按用户要求登记 E-012 已有产物，供后续读取；没有发起新计算。主要结果对应 `R-001-bbox-gradient-halffull`（690 条），20 条先导结果对应 `R-001-bbox-gradient-initial`，两者分别保存。原始产物 `summary.status=completed` 仅表示该程序完成输出，不代表梯度校验通过、Run 审批完成或 Claim 获得验证。690 条此前没有独立 Run，本次以实际产物 ID 补充草稿记录；不补造审批、执行授权或运行历史。已有 20 条 Run 的审批状态保持原样。当前无 Solid Run，以下均为用户本轮要求登记的初步观察，不进入 validated Claim 综合。

当前最值得保留的发现：690 条绝对梯度贡献排名首先是 **L26H25、L24H13**；前者在三个数据集均排第 1，后者分别排第 2/2/3。与旧固定五个 head 的 Top-10 交集为 0，但其中三个旧 head 仍位于第 11、29、39，因此只能说“头部排序明显不同”，不能说旧 head 全部没有贡献。**本轮有限差分方向与反向传播 signed 梯度相反，梯度校验尚未通过；这些排名仅作为待复核候选，不能直接决定增强/抑制。**

### 1. 指标、实现口径与解释边界

对每个样本 n，仅对 teacher-forced query bbox token 计算平均 CE：`L_n = mean_i CE(logits[p_i-1], token[p_i])`，包括 bbox 片段的标点 token，不包含完整 assistant 回答的其他 loss。bbox token 位置是 `p_i`，attention 的 prediction row 必须取 `r_i=p_i-1`；列 j 仅为 query image 的视觉 token，不含 reference image。

定义 `g[n,l,h,r,j] = A[n,l,h,r,j] * dL_n/dA[n,l,h,r,j]`；单样本 `C[n,l,h]=sum_(r,j) abs(g)`，总排名分数 `C[l,h]=mean_n C[n,l,h]`。同时保存 `S[l,h]=mean_n sum_(r,j) g`、正贡献和负贡献绝对值，满足 `C=positive+negative_magnitude`、`S=positive-negative_magnitude`（浮点误差内）。不是先把有符号项相加再取绝对值；样本等权，数据集并不等权。没有再除以视觉 token 数，比较时需注意视觉长度、bbox token 数与样本组成差异。

使用实际 post-softmax attention 张量参与 `A @ V` 的前向，再对其求梯度；因此梯度路径包含 V 及下游计算的影响，但这不是直接测量 head 输出向量范数，也不是完整的跨层路径归因。模型参数冻结、不更新；记录 36 层 × 32 个 query heads = 1152 项（不是 8 个 KV heads）。`LxxHyy` 的层/head 索引从 0 开始，rank 从 1 开始。

signed 的理论含义限于同一个样本、同一个计算图内，对指定 query 视觉边作局部乘法缩放、且不重新归一化时的一阶 CE 导数。绝对分数大不等于“应该增强”；signed 正负也不是 head 的固定语义标签。鉴于本次有限差分失败，暂不采用这些方向作干预依据。

### 2. 输入、checkpoint 与可复现定位

- 输入直接复用已有 eval manifest：`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/test_combined_lasot600_gotval_taoval_1shot_focus.json`，可用 1766 条（LaSOT 600、GOT10k 180、TAO 986）。本轮实际只取 690 条，不能称为全量 1766 条测试。
- 本轮 `screening_counts={LaSOT:300,GOT10k:90,TAO:300}`，seed `20260910`；选中索引见本地 `results/R-001-bbox-gradient-halffull/frozen_input.json:selected_indices`，逐样本 bbox 行、视觉跨度、长度与 CE 见 `records.json`。
- 以数据集和视频序列路径为键，依据当前指定训练 manifest `/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-real-focus-data/manifests/train_only_1shot_focus_valid10522.json` 检查 ref/query 序列重叠。冻结审计报告 `selected_train_sequence_overlap=0`。此结论只相对于该文件，不证明预训练未见过，也不追认未提供的历史训练集合。
- 实际 checkpoint：`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-011/20260907T174853785543Z--focus-early-gt-mask-pipeline/checkpoints/samples_00126264_step_001973`，LoRA adapter 与同 checkpoint 的 `adapter_processor`；两轮 adapter 权重 SHA256 一致。旧固定 head 选择在 step 1482，当前梯度探针在 step 1973。
- 运行模型为 Qwen3-VL-8B-Instruct，BF16 base + LoRA，eager attention；不是原训练的 4-bit 路径。score reduction 使用 FP32，跨样本汇总使用 FP64；仅汇总精度提高不等于 BF16 前向数值问题已经解决。
- 1-shot reference/query，focus 协议，坐标尺度 1000，vision patch cap 1024。记录中实际 sequence token 范围 297–675，bbox token 9–19，query visual token 66–252。
- config/启动脚本继续共用 `configs/head_screening/e012_bbox_gradient_initial.py` 与 `tools/run/e012_bbox_gradient_initial.sh`，通过已有配额调整样本数。没有新建 full-eval config。若要使用当前同一 manifest 的全量，配额应为 LaSOT 600 / GOT10k 180 / TAO 986，实际仍以筛选审计为准。
- **历史执行配置以 frozen_input.json 为准**，不要用之后修改的共用 config 回填历史。执行时源代码 commit/hash 在当前冻结产物中未提供；当前代码不能自动视为执行时的精确版本。

### 3. 690 条结果：总体 Top-20

平均 bbox teacher-forced CE = **1.312645358**。这是本轮用于归因的 loss，没有生成 bbox 的 IoU 或准确率含义。下表标准差是样本间 absolute score 的标准差，不是均值置信区间；signed>0 比例也是样本占比。

| Rank | Head | Absolute mean | Signed mean | Absolute std | Signed>0 样本占比 |
|---:|---|---:|---:|---:|---:|
| 1 | L26H25 | 0.467290 | -0.031100 | 0.216616 | 39.4% |
| 2 | L24H13 | 0.347878 | +0.048569 | 0.221661 | 53.9% |
| 3 | L21H31 | 0.283399 | -0.024648 | 0.573157 | 43.3% |
| 4 | L23H30 | 0.261560 | -0.007627 | 0.186714 | 45.9% |
| 5 | L21H11 | 0.259431 | +0.015673 | 0.333822 | 54.3% |
| 6 | L26H20 | 0.248327 | -0.000330 | 0.159522 | 49.7% |
| 7 | L22H02 | 0.244125 | -0.001953 | 0.313753 | 48.8% |
| 8 | L26H24 | 0.237631 | -0.003252 | 0.108472 | 44.9% |
| 9 | L23H28 | 0.220515 | -0.004920 | 0.229634 | 50.3% |
| 10 | L23H13 | 0.198300 | +0.007447 | 0.126774 | 52.5% |
| 11 | L21H18 | 0.195267 | +0.011089 | 0.326666 | 51.6% |
| 12 | L19H12 | 0.183281 | -0.018601 | 0.458850 | 49.7% |
| 13 | L22H00 | 0.180878 | +0.001796 | 0.218744 | 50.1% |
| 14 | L20H16 | 0.175913 | +0.012310 | 0.199147 | 54.2% |
| 15 | L28H19 | 0.159602 | +0.030446 | 0.098671 | 61.9% |
| 16 | L20H28 | 0.155923 | -0.004809 | 0.269454 | 44.5% |
| 17 | L18H14 | 0.151538 | -0.000121 | 0.340826 | 50.9% |
| 18 | L21H08 | 0.150921 | +0.001437 | 0.174567 | 48.8% |
| 19 | L16H23 | 0.150599 | -0.003817 | 0.298501 | 43.3% |
| 20 | L19H13 | 0.143861 | +0.010102 | 0.302405 | 51.6% |

特别注意 L21H31 的 absolute std 大于均值，表明样本间波动较大。L26H20 等 head 的平均 signed 接近 0，可由正负抵消造成，不能据此判定不重要。

### 4. 三数据集分层观察

| 数据集 | 样本数 | 总分权重 | 平均 bbox CE | Top-5 |
|---|---:|---:|---:|---|
| GOT10k | 90 | 13.04% | 1.286599 | L26H25, L24H13, L26H20, L23H30, L26H24 |
| LaSOT | 300 | 43.48% | 1.408200 | L26H25, L24H13, L23H30, L26H20, L21H31 |
| TAO | 300 | 43.48% | 1.224905 | L26H25, L21H31, L24H13, L21H11, L22H02 |

L26H25 在三组中均排第 1，L24H13 也一致靠前；其余头部成员存在数据集差异。这为后续选候选提供线索，但这里使用的 eval 已参与 head discovery，不能再作为独立泛化验证集。尚未进行不同 seed、bootstrap 置信区间或留出数据复验。

### 5. 与 20 条先导和旧固定 head 的比较

20 条为 LaSOT 7 / GOT10k 7 / TAO 6，mean bbox CE `1.258575919`，Top-10：L26H25, L21H31, L24H13, L23H30, L22H02, L21H11, L26H20, L21H18, L26H24, L23H28。

两轮 Top-5 交集 4 个（Jaccard 4/6），Top-10 交集 9 个（Jaccard 9/11）。20 条样本全部包含在 690 条内（20/20），且数据集比例从 35%/35%/30% 改为 43.48%/13.04%/43.48%。所以这仅支持“扩样后头部候选大致一致”，不是独立重复实验，也不能把差异归因于样本数单一因素。两轮 CE 不能作为性能升降比较。

旧固定集合来自用户指定 E-011 checkpoint run 下 `pipeline/fixed/step_001482/selection.json`，只读取该明确参照的集合与元数据，不扩展其它实验结果。

| 旧 head | 20 条排名 | 690 条排名 |
|---|---:|---:|
| L21H10 | 24 | 29 |
| L20H15 | 252 | 135 |
| L21H18 | 8 | 11 |
| L17H04 | 46 | 39 |
| L20H18 | 289 | 199 |

旧五个 head 与本轮 Top-5 / Top-10 的交集均为 0，与 Top-50 的交集为 3。旧集合的选择阶段、权重 step、数据与本轮评价口径没有控制为一致，故不能从“不重合”直接推出新方法更好，或旧 head 无效。需要在同 checkpoint、同输入、同干预预算下进行对照才有因果含义。

### 6. 必须保留的校验失败

首次样本 dataset index 0、sample_id `0-1`、LaSOT `basketball-1`，baseline bbox CE `0.7353028655`。有限差分选取的是该首样本绝对 signed sum 最大的 **L24H25**，不是总体 Top-2 的 L24H13；L24H25 在总体排名第 128。

| 检查项 | 原始值 |
|---|---:|
| hook 与 baseline 前向最大 logits 差 | 0.0 |
| epsilon（post-softmax 指定边乘 1±epsilon，不重归一化） | 0.02 |
| loss_minus | 0.716220796108 |
| loss_plus | 0.731939792633 |
| 反传 signed derivative | -0.112897530198 |
| 中心差分 (loss_plus-loss_minus)/(2 epsilon) | +0.392974913120 |
| sign_agreement | **False** |
| relative_error | 1.287289408124（约 128.7%） |

相对误差的分母为 `max(abs(central_difference),abs(signed_derivative),1e-8)`。前向 parity=0 只证明该首样本的未扰动输出一致，不能证明梯度链路与有限扰动一致。当前实现把有限差分作为 diagnostic，不把失败作为输出 completed 的阻断条件，所以文件写 completed 与此项失败可以同时存在。

20 条先导的首样本检查对象为 L25H10，符号一致但相对误差约 41.6%；它与 690 条的检查不是同一个样本/head，不能用来覆盖当前失败。原因尚未定位：可能涉及 BF16 数值、有限步长、扰动路径或实现问题，现有证据不能选定其中一种解释。**在复核前，signed 方向不可用于增强/抑制决策，absolute 排名也仅保留为未验证观察。**

### 7. 本次登记的检查与未完成事项

本地核对通过：690 records / 690 唯一索引 / frozen indices 一致；36×32 head 覆盖；每条记录 prediction_rows=p_i-1；数据集计数；逐样本 CE 均值；排名单调；absolute/signed 与正负分量分解；20/690 adapter 哈希一致；中心差分算术；五份远端证据镜像 SHA256 一致。机器可读结果见 `comparison.json`。这些是记录完整性检查，**不替代梯度有效性验证**。

未做生成 IoU/Acc 测试、head 因果干预、高排名对随机/旧 head 对照、独立泛化评估。本次没有重跑 GPU 或重新汇总远端每个 npz；逐样本数组仍在远端，records 保留路径。没有推进 Claim、Solid、审批或执行授权。

建议后续先固定这个首样本和 L24H25，复现 baseline、正/负扰动与反向结果；再检查计算图和扰动对象，使用 FP32 与多个 epsilon、多个候选 head/样本验证导数。通过后再比较 L26H25/L24H13、其他候选、旧固定集合及随机集合，并在未参与筛查的样本上测定位指标。以上是待开展工作，本次未执行。

### 8. 后续读取入口与证据哈希

先读本节及 Run 的结果摘要，随后按需读 `results/R-001-bbox-gradient-halffull/comparison.json`（重合度和检查）、`summary.json`（总体/分数据集完整排名）、`frozen_input.json`（实际输入与 checkpoint）、`records.json`（逐样本定位）、`provenance.json`（来源与哈希）。`ranking.csv` 便于表格分析。原始远端根目录：`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-012/R-001-bbox-gradient-halffull`。

| 本地证据文件 | SHA256 |
|---|---|
| summary.json | `00cf37ece39f9bb126a65802e2a150983d53321b031d151464933df66941c73b` |
| ranking.csv | `6be84c53839f157309ed768d40ce8c2eb35de423a6db1edc0a5a4f59c28af4d6` |
| frozen_input.json | `df4771e68875722ed962e96240f2c9ffe2ead71e64976908b4459c797ffebf0d` |
| runtime.json | `a7d5ca705749b590669a20eab93a41ce57d6ee9cb76ef9ef61d1192110569dc0` |
| records.json | `34bbeca91e2767c9692632bbadf9def6d322e0d1e646a4d6712814b4890ae62f` |

本地20条对照：`results/R-001-bbox-gradient-initial/summary.json`、`frozen_input.json`；旧集合：`results/reference-fixed-heads/selection.json`。其哈希也在 provenance.json。输入 eval manifest、训练 manifest、adapter/config 的哈希均已随冻结输入与 provenance 保存。

证据状态：无 Solid ID；本次新增与更新内容均是可追溯的初筛记录。以后自动上下文若只允许 Solid，不能因为这里有详细结果就自动扩大证据权限；需由用户显式引用相应 Run 后读取。
