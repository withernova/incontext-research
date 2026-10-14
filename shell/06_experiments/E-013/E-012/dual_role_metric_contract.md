# E-012：Query / Reference Head 指标与实现合同

> contract: `e012.dual-role-head-metrics/v1`
>
> 适用 Run：R-004–R-010。本文是指标的唯一详细定义；Run 页面负责说明研究问题和该 Run 使用哪些指标。任何实现若不能满足本文，应在运行前停止并修订设计，不能自行猜测。
>
> 当前所有阈值、样本数量、随机种子和容差中尚未由人类确认的值，必须作为 required config 留空并 fail closed；不得在代码里采用隐式默认值，更不得看结果后填写。

## 1. 固定索引与损失

### 1.1 样本单位

- `n`：一条完整的 Query+Reference 输入及一个 Query bbox 标注。
- 统计单位是样本；同一 sequence 或共享任一图像的 connected component 是 bootstrap cluster。
- Query 和 Reference 的图像身份、视觉 span、merged token grid、原始像素尺寸和 GT xyxy 都必须逐样本保存。

### 1.2 bbox 坐标 token 行

主分析不使用“bbox 字符串中的所有 token”，而只使用四个数值坐标字段 `x1,y1,x2,y2` 对应的 assistant target token：

```text
P_n = P_n,x1 ∪ P_n,y1 ∪ P_n,x2 ∪ P_n,y2
```

如果一个坐标被 tokenizer 切成多个 token，该字段的全部 token 都属于 `P_n,k`。括号、逗号、空格、EOS 和解释文本不属于 `P_n`。实现必须通过“序列化 bbox 字符串的字符区间→token 区间”或等价的前缀差分方法建立对齐，并保存每个字段的字符值、token IDs、target positions 与 prediction rows；禁止假定每个坐标恰好一个 token。

对 target token 位置 `i∈P_n`，读取 logits 行 `i-1`。若任何 `i-1<0`、label 不等于该 target token、四个字段缺失或字段间 token 重叠，样本完整性失败。

### 1.3 主损失

```text
L_coord(n) = (1/|P_n|) Σ_{i∈P_n} CE(logits_n[i-1], token_n[i])
```

单位：nats/token；越低越好。梯度全部对每条样本自己的 `L_coord(n)` 求导。由于损失已经除以 `|P_n|`，后续对 prediction rows 求和时不再除一次。

格式 token 的 CE 另记为 `L_format(n)`，只能作退化诊断，不能进入主选头指标。

## 2. Attention、Value 与 GT mask

- `l∈[0,L-1]`：文本 self-attention 层，零基编号。
- `h∈[0,H_q-1]`：query head，零基编号；不得写成 KV-head 编号。
- `\bar P_n={i-1 | i∈P_n}`：坐标 token prediction rows；以下所有 `Σ_p` 默认 `p∈\bar P_n`。
- `r∈{Q,R}`：Query 或 Reference 图像。
- `V_nr`：角色 `r` 的全部视觉 key token 索引。
- `A_nlhpj`：eval 模式下，softmax 和 attention dropout 后、与 V 相乘前的实际 attention probability。
- `v_nlhj`：按模型真实 GQA 映射展开到 query head `h` 后的 value vector。
- `z_nlhp=Σ_j A_nlhpj v_nlhj`：o_proj 前的单 query-head A@V 输出。

对图像角色 `r` 的 token `j`，定义 fractional GT occupancy：

```text
g_nrj = area(token_cell_nrj ∩ GT_box_nr) / area(token_cell_nrj),  0≤g≤1
```

使用模型实际 merged token grid。不得只用 token 中心点命中，也不得把边界 token 强行二值化。必须满足：GT 正面积、token cell 正面积、`Σ_j g_nrj>0`；否则样本在 split 冻结前标记 invalid 并显式计数。

## 3. 一阶 visual contribution

### 3.1 逐边 signed 与 absolute contribution

```text
e_nlhpj = A_nlhpj · ∂L_coord(n)/∂A_nlhpj
c_nlhpj = |e_nlhpj|
```

等价链式计算：

```text
e_value_nlhpj = <∂L_coord(n)/∂z_nlhp, A_nlhpj v_nlhj>
```

R-004 要求 `e` 与 `e_value` 在 FP32 汇总下满足预冻结误差容差。`e` 的符号只表示对该 post-softmax edge 做不重归一化乘法缩放时的一阶方向；R-004 通过前，signed 值不得用于排序、增强或抑制。

### 3.2 角色贡献与角色份额

先在单样本内求和：

```text
C_role(n,l,h,r) = Σ_{p∈\bar P_n} Σ_{j∈V_nr} c_nlhpj
C_all(n,l,h)    = Σ_{p} Σ_{all valid keys j} c_nlhpj
RoleShare(n,l,h,r) = C_role(n,l,h,r)/(C_all(n,l,h)+eps)
```

然后样本等权平均：

```text
RoleVisualAbsContrib(l,h,r) = mean_n C_role(n,l,h,r)
RoleVisualContribShare(l,h,r) = mean_n RoleShare(n,l,h,r)
```

`C_role` 越高表示当前输入附近的局部敏感度越大，不表示因果必要性。不能先把所有样本的边混在一起再求比例。

`eps` 只防止除零，必须按 dtype 在 config 中冻结并保存；若分母为 0，同时保存 `denominator_zero=true`，不能只靠 eps 隐藏。

## 4. 目标区域贡献

每个样本、head、角色先计算：

```text
C_target(n,l,h,r) = Σ_p Σ_{j∈V_nr} g_nrj c_nlhpj
C_bg(n,l,h,r)     = Σ_p Σ_{j∈V_nr} (1-g_nrj)c_nlhpj
G_target(n,r)     = Σ_{j∈V_nr} g_nrj
G_bg(n,r)         = Σ_{j∈V_nr} (1-g_nrj)
```

### 4.1 目标贡献比例

```text
TCR(n,l,h,r) = C_target/(C_target+C_bg+eps)
TCR_mean(l,h,r) = mean_n TCR(n,l,h,r)
```

范围理论上为 `[0,1]`，越高表示该角色视觉贡献中落在 GT 的比例越高。它会受目标面积影响，不能单独用于入选。

### 4.2 单位面积目标 enrichment

```text
D_target = C_target/(G_target+eps)
D_bg     = C_bg/(G_bg+eps)
logTCE(n,l,h,r) = log((D_target+eps)/(D_bg+eps))
TCE_geomean(l,h,r) = exp(mean_n logTCE)
```

`logTCE>0` / `TCE>1` 表示单位 token 面积的目标贡献高于背景。跨样本必须平均 `logTCE` 后再指数化，禁止直接对重尾 ratio 做算术均值。若 `G_bg=0` 或角色贡献分母为 0，保存 invalid reason；不得静默补值。

### 4.3 空间 null 对照

每个样本和角色在看模型输出前，由冻结 seed/算法生成 `K_null` 个 mask `q_nrkj∈[0,1]`：

- GT 面积匹配的非重叠平移框；
- token 数/连通形状尽量匹配的背景；
- GT 邻近但不含 GT 的环带；
- 另一角色 GT 的归一化坐标投影。

每种 null 类型和数量必须单独固定，禁止根据 head map 选择最差背景。定义：

```text
D_null(k) = [Σ_p Σ_j q_nrkj c_nlhpj] / [Σ_j q_nrkj+eps]
NullMeanDensity = mean_k D_null(k)
TargetVsNullLog(n,l,h,r) = log((D_target+eps)/(NullMeanDensity+eps))
TargetVsNullLogMean(l,h,r) = mean_n TargetVsNullLog
```

方向：越高越好；`>0` 表示目标单位面积贡献高于该样本预冻结 null 的均值。不同 null 类型还要分别报告，不能只给混合均值。

## 5. Discovery 与 Confirmation 聚合

### 5.1 Discovery（R-005/R-006）

Query 和 Reference 使用同一算法但分别选头：

1. 按 `RoleVisualAbsContrib(l,h,r)` 形成 Top-`M` relevance pool；
2. pool 内逐 head 检查 `TargetVsNullLogMean`、`mean(logTCE)` 和 cluster-bootstrap CI；
3. 对 sequence/shared-image component 做 bootstrap，记录每个 head 再次通过上述固定 gate 的比例 `SelectionFrequency`；
4. 达标 head 依次按 `SelectionFrequency`、`TargetVsNullLogMean`、`RoleVisualAbsContrib` 降序，最后按 `(layer,head)` 升序打破完全平分；
5. 最多取 `K_head`，允许少选或零选，禁止补满。

`M`、`K_head`、bootstrap seed/次数、每个 gate 阈值必须是 required config。R-005 和 R-006 必须相同。

### 5.2 Confirmation（R-007）

对冻结 candidate set `H_r`，每样本先对 heads 等权平均：

```text
SetTargetVsNull(n,r) = mean_{(l,h)∈H_r} TargetVsNullLog(n,l,h,r)
```

对每个同层、同数量随机 control set `H_r^ctrl,s` 使用同式：

```text
ControlSetTargetVsNull(n,r,s)
CandidateMinusControl(n,r) = SetTargetVsNull(n,r) - mean_s ControlSetTargetVsNull(n,r,s)
```

主汇总：样本等权 mean/median、按 connected component cluster-bootstrap 的 95% CI、正值样本比例。候选集合通过必须同时满足：

- `mean_n SetTargetVsNull > 0` 且其预注册 95% CI 下界 `>0`；
- `mean_n CandidateMinusControl >0` 且其 95% CI 下界 `>0`；
- 完整性 gate 通过。

Query 与 Reference 分别判定。逐 head p-value 只作次要分析并使用 BH-FDR；不得代替集合主检验。

## 6. 目标区域对背景的因果消融（R-008）

### 6.1 干预定义

对冻结候选集合中的所有 heads 联合干预；仅作用于 `p∈P_n-1` 和指定角色 `V_nr`，位置在 softmax/dropout 后、A@V 前。

目标条件：

```text
A_target'_nlhpj = A_nlhpj · (1-g_nrj),  j∈V_nr
```

因此边界 token 按 occupancy 比例移除。逐 head、逐 prediction row 的实际移除质量：

```text
M_target(n,l,h,p,r)=Σ_{j∈V_nr} A_nlhpj g_nrj
```

背景条件使用 `b_nlhprsj∈[0,1]`，其中 `s` 是背景重复编号。**mask 按 sample×layer×head×prediction-row×role 单独构造**；这是为了逐 head、逐行精确匹配目标 removed mass，不得擅自改成“整个候选集合只匹配一个总质量”：

```text
A_bg'_nlhpj = A_nlhpj · (1-b_nlhprsj)
M_bg(n,l,h,p,r,s)=Σ_j A_nlhpj b_nlhprsj
```

背景 token 的候选顺序由运行前冻结的空间区域生成算法与 seed 决定；看到 clean attention 后只允许沿该顺序取到目标质量，不能按损害或梯度挑背景。matcher 必须对每个 `n,l,h,p,r,s` 满足：

```text
|M_bg-M_target| ≤ atol + rtol·|M_target|
```

`atol/rtol`、背景区域生成算法、数量 `K_bg` 和 seed 在运行前冻结。最后一个背景 token 可 fractional removal 以精确匹配；若全部背景质量不足，记录 `mass_match_infeasible`，该配对不进入 matched-effect 均值，但必须计入总样本数并报告不可行率。主干预不重归一化。

### 6.2 CE 效应

每样本先计算：

```text
DeltaCE_target(n,r) = L_coord_target_remove(n,r)-L_coord_baseline(n)
DeltaCE_bg(n,r,s)   = L_coord_bg_remove(n,r,s)-L_coord_baseline(n)
TargetSpecificDamage(n,r) = DeltaCE_target(n,r)-mean_s DeltaCE_bg(n,r,s)
```

方向：`TargetSpecificDamage>0` 支持“目标移除比等质量背景更伤 bbox”。

对同层、同数量 control head set 完全重复，定义：

```text
TargetSpecificDamage_ctrl(n,r,t)
DamageDID(n,r)=TargetSpecificDamage_candidate(n,r)
              -mean_t TargetSpecificDamage_ctrl(n,r,t)
```

方向：`DamageDID>0` 表示候选的目标特异损害强于随机 controls。

主汇总均为样本等权 mean/median、cluster-bootstrap 95% CI、正值比例和有效/总样本数。R-008 某角色通过必须同时满足 `TargetSpecificDamage` 与 `DamageDID` 的 mean 之 95% CI 下界 `>0`，且 mass-match/empty-hook/完整性 gate 通过。

## 7. 自由生成指标（R-009，可选）

### 7.1 bbox 解析与 IoU

- 从原始生成文本按运行前冻结的唯一 parser 提取一个 0–1000 `xyxy` bbox；不裁剪、不修复、不从多个框中事后挑最好者。
- 恰好一个合法框且 `x2>x1,y2>y1` 为 valid；否则 invalid。
- GT 来自原 annotation 到 0–1000 的预冻结变换，不从目标文本反解析。
- invalid prediction 的 IoU 固定记 0，同时单独计入 invalid rate；所有样本保留在主分母。

```text
DeltaIoU_condition(n)=IoU_condition(n)-IoU_baseline(n)
GenerationTargetSpecificDamage(n,r)
 = DeltaIoU_bg_mean(n,r)-DeltaIoU_target(n,r)
```

方向：越高表示目标移除造成的 IoU 下降比背景移除更大。另报 bbox changed、normalized coordinate L1、invalid/multi-box/truncation/text-changed rate，分母均为全部预冻结样本。

## 8. 跨层路径指标（R-010，可选）

令 clean、上游目标扰动 `corrupt`、向 corrupt 回填 clean 下游输出 `rescue`、向 clean 注入 corrupt 下游输出 `transfer`：

```text
UpstreamDamage(n)=L_corrupt-L_clean
RescueEffect(n)=L_corrupt-L_rescue
RescueFraction(n)=RescueEffect/UpstreamDamage，仅当 UpstreamDamage>damage_floor
TransferEffect(n)=L_transfer-L_clean
DownstreamRelativeChange(n)=||D_corrupt-D_clean||_2/max(||D_clean||_2,norm_floor)
```

`damage_floor/norm_floor` 必须预冻结。主报告不筛选样本的 `UpstreamDamage/RescueEffect/TransferEffect`；`RescueFraction` 只作有正损害样本的辅助量。目标路径还必须相对 mass-matched background corruption 和同层 U/D controls 计算配对差。只有 rescue 与 transfer 都是预期方向且优于两类 controls，才称固定路径中介线索。

## 9. 统一统计、方向与缺失值

1. 所有主指标先逐样本计算，再样本等权汇总；禁止 token 多的样本获得更大样本权重。
2. bootstrap 重采样单位是 sequence/shared-image connected component，而不是单条 record；同一 cluster 的记录一同抽入。
3. bootstrap seed、次数、CI 方法必须冻结并写入 resolved config；无默认值。
4. 同时报告 mean、median、95% CI、正方向比例、`n_total/n_valid/n_invalid`。
5. 分数据集结果是异质性报告；总体结论不能只由某一个数据集的正结果替代。
6. NaN/Inf、零分母、invalid GT、mass-match infeasible、parser invalid 都要有枚举 reason；不得静默删除或当 0（R-009 明确定义 invalid IoU=0 除外）。
7. 随机 background masks、control head sets 和 bootstrap replicates 不是独立样本，不能扩大统计 n。
8. signed gradient 方向只在 R-004 gate 通过后使用；absolute contribution 始终只表示局部敏感度大小。

## 10. 最低产物合同

每个计算 Run 至少保存：

```text
resolved_config.json
input_manifest.json + sha256
records.jsonl
summary.json
integrity.json
```

Discovery 另存：

```text
all_heads.parquet 或等价无损表
query_candidates.json / reference_candidates.json
bootstrap_results.*
```

每条 record 必须包含：sample/cluster/dataset identity、Q/R image identity、四坐标字段及 token positions、prediction rows、Q/R spans/grids、GT occupancy、layer/head 零基编号、指标所有分子分母、invalid reason。干预 Run 还必须保存每条件实际 removed mass、matcher error、hook firing 和原始 loss/output。

`summary.json` 只能由 records 离线重算；已有 output directory 拒绝覆盖；完整性失败不得写 scientific `status=completed`。
