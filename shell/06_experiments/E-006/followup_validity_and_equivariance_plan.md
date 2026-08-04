# E-006 后续 Run 规划 v2：按用户审核重排

- status: revised_after_human_review / not started
- revised: 2026-08-03
- parent_run: `E006-R-005-simple-top50-support-components-positive-extremes-n111-640`
- execution note: 本文件只做重新规划；即使某个 Run 已批准/授权，本轮也不自动执行。

## 1. 用户审核后的变更

| 原 Run | 审核意见 | v2 决定 |
|---|---|---|
| R-006 | approved + authorized | 保留，不改变科学范围；仍只做 n=10 row/alignment 工程 gate |
| R-007 | COCO 已完整下载；询问 unique-image 是否来自原文 | 改为只读取服务器现有 COCO；纠正为“1220 RefCOCO expression samples，按 COCO image 分组防泄漏”，不是 1220 unique images |
| R-008 | 后续只研究 Qwen，不做 LLaVA | 取消，不执行，不再作为 R-009/R-010 依赖 |
| R-009 | 目的不清楚 | 简化为可选的 Qwen-only RefCOCO 外部正对照；明确它不验证 IPLoc-ID identity/Q→R |
| R-010 | approved + authorized；要求 correct/error/correct-error-mix、reference/query head 变化的图表与可视化 | 扩充为三组 × 多角色全 head discovery，增加固定图表和样本可视化；因范围有实质更新，先重新审核，不消费旧执行授权 |

## 2. 关于 `unique-image` 的准确回答

`unique-image` **不是公开 LocalizationHeads README 明示的原论文采样要求**。公开仓库只写：

```text
1,000 data samples from the RefCOCO training set
10 trials with a set consisting of 1,000 samples
```

它没有公开精确 sample IDs，也没有说明 1,000 的单位是否必须是 1,000 个不同 COCO images。RefCOCO 中，同一 COCO image 可以对应多个 object annotations / referring expressions。

之前提出 `1220 unique images` 是我们为避免 discovery/confirmation 发生同图泄漏而添加的更严格本地设计，不应冒充原论文规则。v2 改为：

```text
采样单位：RefCOCO referring-expression sample
规模：20 pilot + 1000 discovery + 200 confirmation = 1220 samples
分区约束：按底层 COCO image_id group split
结果：三个split之间image_id不重叠；split内部允许一个image只抽一个或多个expression，规则预先固定
```

为了让统计单位简单、避免同图重复权重，主 manifest 优先每个 image 抽一个合法 expression；如果可用 image 数不足，再允许 split 内多个 expressions，但必须：

```text
记录每图expression数
统计/重采样按image_id聚类
绝不跨split复用image_id
```

这叫 **本地 anti-leakage 设计**，不是 exact-paper subset replication。

---

# 3. v2 执行主链

```text
Core A：row定义
  R-006 exact last-token / first-step / bbox p-1 alignment gate

Optional external Qwen control：
  R-007 existing-COCO + RefCOCO expression manifest
  R-009 Qwen-only RefCOCO last-token spatial positive control

Core B：当前IPL oc-ID行为组是否换head
  R-010 correct / error / balanced-mix × reference/query all-head discovery
  R-011 fresh sequence-disjoint confirmation

Core C：Q→R是否只是query坐标复制
  R-012 transform geometry manifest
  R-013 natural behavior gate
  R-014 reference-tracking vs query-coordinate-copy attention audit
  R-015 visual-content vs prompt-bbox mismatch（仅条件触发）
```

关键变化：

- R-008 已取消；
- R-009 不再阻塞 R-010；
- Core 主线保持同一个 Qwen3-VL + IPLoc-ID checkpoint；
- RefCOCO 只是 Qwen-only external sanity/transfer control，不承担 identity-binding 证明。

---

# R-006 · Exact last-token alignment gate（保留已批准设计）

Run：

```text
E006-R-006-exact-last-token-bbox-row-alignment-gate-n10-640
```

同一 5 correct + 5 error 样本审计：

```text
A. forward最后一个非padding输入token row
B. generate第一个生成step row
C. natural bbox各坐标token的p-1 rows
```

输出必须包括：

```text
完整chat template
last input token id/string/position及是否结构token/newline
first generated token id/string
A/B attention max-abs difference
bbox连续精确token match及所有p-1 rows
reference/query spans、grid、finite gate
同样本 last-token→R/Q 与 bbox-row→R/Q 可视化
```

R-006 仅证明实现对齐，不选 head、不比较组显著性。

---

# R-007 · 使用服务器现有 COCO 的 RefCOCO manifest gate（已修订）

Run ID 保留：

```text
E006-R-007-refcoco-coco-frozen-manifest-integrity-gate-n1220
```

## 目的

不再下载 COCO。先定位并审计 `/home/featurize/data` 下用户已下载的完整 COCO，再把 RefCOCO metadata 映射到本地图片。

## 数据单位与分区

```text
pilot：20 RefCOCO expression samples
discovery：1000 samples
confirmation：200 samples
split grouping key：COCO image_id
seed：20260724
```

这里的 `n1220` 是 expression samples，不等于论文规定的 1220 unique images。

## 实施步骤

1. 只读扫描服务器 COCO 根目录，记录实际路径、train/val 年份、图片数和 annotation 文件；不猜路径；
2. 定位 RefCOCO UNC train metadata，记录来源/revision/hash；
3. 将 expression/object bbox/image_id 映射到本地 COCO 文件；
4. 按 image_id group split，再在组内以冻结规则抽 expression；
5. 输出 manifest、split summary、重复 image/expression audit、缺失清单。

## Hard gates

```text
1220/1220 expression records合法
所有引用图像在本地可解码
bbox合法、尺寸匹配、expression非空
pilot/discovery/confirmation image_id overlap=0
sample_id/ref_id/ann_id唯一规则明确
0 silent missing
```

若完整 COCO 与 RefCOCO 所需年份/目录不匹配，明确报告缺口，不启动 R-009，也不自动联网下载。

## Claim boundary

这是本地 anti-leakage manifest，不是 LocalizationHeads 作者未公开的精确 1000-sample subset。

---

# R-008 · 取消

Run：

```text
E006-R-008-upstream-llava-last-token-refcoco-positive-control-n1000-200
```

状态改为：

```text
cancelled_by_user_qwen_only_scope
```

不加载 LLaVA、不下载 LLaVA 权重、不产生科学结果。取消原因：后续研究限定为 Qwen；上游 LLaVA 复现的成本不能直接服务当前 checkpoint。

因此，后续不能再声称：

```text
“我们复现了LocalizationHeads原模型结果”
```

只能说：

```text
“我们在Qwen上实现/测试了其公开last-token head-selection思路”
```

---

# R-009 · Qwen-only RefCOCO 外部空间正对照（已简化）

Run ID 保留：

```text
E006-R-009-qwen-last-token-bbox-row-refcoco-transfer-n1000-200
```

## 一句话目的

> 在标准单图 RefCOCO grounding 数据上，检查 Qwen 的 exact last-token 方法能否找到在未见 confirmation 图像上靠近 GT object 的 heads。

它不是为了验证 IPLoc-ID 的 Q→R，也不测试个体身份。它只回答：

```text
Qwen + last-token attention-head discovery
在外部标准grounding数据上是否具有基本空间有效性？
```

## 为什么仍可能有价值

如果 exact last-token 在 RefCOCO 上都找不到 GT-localizing heads，则当前方法迁移到 Qwen 的一般有效性值得怀疑；如果能找到，则说明实现和 Qwen 架构上存在外部 spatial positive control，但不能推导双图 identity binding。

## 模型与条件

Primary：

```text
base Qwen3-VL-8B-Instruct
单图RefCOCO prompt
exact forward last-token
```

不再运行 LLaVA。IPLoc-ID LoRA 不是单图 RefCOCO 原生 checkpoint，默认不放入 primary；若用户后续明确要求，只能新列 task-shift diagnostic。

## 简化流程

```text
pilot20：prompt、bbox输出/attention工程gate
discovery1000：按公开repo-style attention sum + spatial entropy统计全1152 heads
confirmation200：冻结Top5后评估GT overlap，不重选
```

bbox p-1 不再作为主变量；仅在模型可以稳定生成/teacher-force RefCOCO bbox 时作为附录 row comparator，避免把一个简单正对照膨胀成三套大实验。

## 指标

```text
Top5 head IDs与selection frequency
confirmation GT conditional mass
S50 H/M/L
all-head percentile
layer-matched random heads（10 frozen seeds）
固定20张heatmaps
```

## Claim boundary

```text
支持：Qwen last-token attention在RefCOCO上的空间正对照
不支持：IPLoc-ID个体识别、Q→R reference binding、因果机制
```

R-009 是可选 external control；不阻塞 R-010。

---

# R-010 · correct/error/balanced-mix × reference/query 全 head discovery（重点修订）

Run：

```text
E006-R-010-outcome-stratified-allhead-discovery-sequence-split
```

由于用户新增了正式可视化和三组/双角色要求，虽然旧版已批准和授权，本版视为实质范围更新：**不直接消费旧授权，需重新审核后执行。**

## 目的

回答两个清楚的问题：

1. correct 与 error 时，负责 reference/query 空间处理的 head IDs 或排名是否变化？
2. 若用 correct+error 混合数据发现 heads，是否会掩盖组特异 heads？

## 三个 discovery strata

```text
C：localization-correct（natural Yes, IoU>=.7）
E：localization-error（natural Yes, IoU<.1）
M：correct-error balanced mix
```

`M` 不是直接把样本按原比例混在一起。为防 correct 数量更多主导排名，M 使用：

```text
组等权：每个sequence先聚合，correct/error各贡献50%
或在冻结seed下对较大组下采样到相同sequence数
```

主方案固定为组等权；下采样只作可审计敏感性，不按结果选择。

middle/rejected 不进入 C/E/M 主 discovery，另报样本计数。

## Reference/query 角色必须分开

### Reference grounding：G→R

```text
rows：reference bbox token p-1
keys：reference image span
```

回答 prompt reference object 的 grounding heads 是否随最终行为组变化。

### Query-stage reference use：Q→R

```text
rows：当前自然query bbox token p-1
keys：reference image span
```

回答 bbox 生成阶段回看 reference 的 heads 是否随行为组变化。

### Query localization：Q→Q

```text
rows：当前自然query bbox token p-1
keys：query image span
```

回答 query 自身 localization heads 是否随行为组变化。

### Repo-style terminal row：T→R / T→Q

```text
rows：R-006确认的exact last-input-token
keys：reference / query image spans
```

这是对“原文 last-token 定义”的平行审计，不能与 bbox-stage roles 合并排名。

## Head discovery 与 GT evaluation 分开

为避免用 GT 选 head 后再用 GT 证明自己，每个 `stratum × role` 先使用不依赖 GT 的 repo-compatible统计发现 heads：

```text
full-sequence target-image budget
image内空间entropy/component结构
per-sample selection frequency
```

冻结 Top5 及完整1152-head ranking。然后才独立报告：

```text
conditional GT mass
S50 H/M/C/CG/L
all-head percentile
```

术语固定：

```text
activation/budget：完整序列attention分给目标image span的质量
alignment：进入image后与GT的空间重合
```

不得把 GT hit 直接称为 activation。

## 数据与 split

优先使用已有 sequence-aware natural outputs，并在 attention 前按 sequence 冻结 discovery/confirmation：

```text
同一sequence的frames不能跨split
所有统计/bootstraps按sequence
先给出C/E每组sequence数与frame数
任一组sequence不足则停止并扩数据，不改阈值
```

R-010 只使用 discovery split；R-011 使用 confirmation split。

## 必交图表

### 1. Head identity / rank 是否变化

每个角色分别生成：

```text
C/E/M Top5 head表：layer-head、frequency、budget、entropy、GT mass、H/L
3-set UpSet图：C vs E vs M Top5/Top10 overlap
3×3 Jaccard heatmap：C/E/M
rank-rank scatter：correct rank vs error rank，标注Top heads
layer×head heatmap：correct-error selection-frequency difference
layer histogram：C/E/M top heads所在层
```

### 2. Reference 与 query 角色是否变化

生成：

```text
role × stratum head-ID matrix
G→R、Q→R、Q→Q、T→R、T→Q两两Jaccard heatmap
同一head在reference budget与query budget的scatter
head-role alluvial仅表示集合重叠，不使用“head发生因果转变”措辞
```

### 3. 固定样本 attention 可视化

冻结样本，不挑最好图：

```text
6 correct + 6 error
按sequence hash取固定样本
```

每个样本至少包含：

```text
Reference clean + GT
G→R C/E/M-discovered aggregate maps
Q→R C/E/M-discovered aggregate maps
Query clean + GT + natural prediction
Q→Q C/E/M-discovered aggregate maps
last-token T→R/T→Q附页
```

颜色/框保持 E-005/E-006 约定：

```text
turbo blue-low/red-high
green=GT
red=natural prediction
```

每panel min-max只用于空间展示；跨组/跨head正式比较用 raw attention。

### 4. 三种结论模板

```text
shared-head / strength-change：C/E/M IDs高度重合，只是budget/alignment强度变化
outcome-specific routing signature：C与E heads不同，M只保留共享或多数组heads
no-stable-change：discovery差异不能在R-011 confirmation复现
```

R-010 只发现候选；不能单独采用第二种强解释，必须等 R-011。

---

# R-011 · Fresh confirmation：三组 head sets 的跨组/跨角色验证（同步修订）

Run：

```text
E006-R-011-outcome-headsets-fresh-cross-evaluation
```

## 冻结输入

R-010 对每个 role 冻结：

```text
C-discovered Top5
E-discovered Top5
M-discovered Top5
完整ranking
```

## Confirmation matrix

每个 role 分别在 fresh correct/error sequences 上做：

| Frozen head set | Evaluate correct | Evaluate error |
|---|---:|---:|
| C-discovered | ✓ | ✓ |
| E-discovered | ✓ | ✓ |
| M-discovered | ✓ | ✓ |

Controls：

```text
E-006 historical main heads
same-size random heads ×10 frozen seeds
layer-matched random heads ×10 frozen seeds
all-head percentile
```

## 必交图表

```text
每角色3×2 performance heatmap
C/E/M head-set Jaccard与rank stability discovery→confirmation
correct-error effect forest plot（sequence bootstrap B=10000）
固定confirmation样本contact sheets
```

## 判定

- C/E sets 不同且各自在对应 held-out outcome 优于另一set：支持 outcome-dependent attention-routing signature；
- IDs重合、仅budget/alignment不同：支持 shared-head strength change；
- discovery差异在confirmation消失：判 discovery noise；
- M 若遗漏稳定E-specific heads，可说明 pooled discovery 会掩盖少数组特征；仍非因果。

只有 R-011 稳定 heads 才进入 R-014 primary analysis。

---

# R-012–R-015 · 几何干预链（核心逻辑保留）

## R-012：offline geometric separability

```text
identity / HFlip / VFlip / R180
REF-only / QUERY-only / BOTH
R_t = 当前reference GT
R_0 = 原reference GT
Q_t→R = 当前query GT归一化投影到reference
```

主 gate 在看 attention 前冻结：

```text
IoU(R_t,Q_t→R)<=.1
merged-grid centroid distance>=2 cells
候选区域token coverage合法
```

90°/270°不进入 primary，避免交换W/H与改变grid/token length。

## R-013：natural behavior gate

每个 eligible pair 的 identity 与 9 个 transform 条件重新自然生成：

```text
Yes保持率
parse率
natural bbox IoU
Joint F1
bbox equivariance
```

behavior-stable 和 behavior-changed 分开；不复用 identity archived bbox 冒充 transform natural output。

## R-014：attention-first 的 reference tracking vs query-map/coordinate copy

> 2026-08-03 用户澄清：R-012 的几何框图不是目标交付。目标是与 E-005/E-006 相同风格的 **真实 attention heatmap**，直接查看 query heads 在 query 图上的 Q→Q map 是否按归一化坐标被迁移到 reference 上形成 Q→R map。

Primary 先固定历史 query main4：

```text
L18H15, L19H03, L22H00, L20H08
```

不得在 transform 结果上重选。若 R-011 后续得到 held-out 稳定 heads，只能作为另行预注册 secondary。

固定 6 correct + 6 error sequences；每个 condition 先做真实 natural generation，再用该 condition 的自然 bbox 做 exact teacher replay。**同一个 replay forward、同一组 bbox p-1 rows、同一个 head** 同时提取：

```text
Q→R：query bbox p-1 rows → current reference image span
Q→Q：query bbox p-1 rows → current query image span
projected Q→Q：把Q→Q按归一化token-grid坐标投影到reference grid
```

Primary conditions：

```text
identity
REF-only × HFlip/VFlip/R180
QUERY-only × HFlip/VFlip/R180
```

BOTH × H/V/R180 仅作附录等变性 control。

每个 sample×condition 的必交 E-005/E-006 风格 panel：

```text
reference current image + green R_t + magenta Q_t→R
4个per-head Q→R turbo overlays
main4 aggregate Q→R
query current image + green Q_t + red natural prediction
4个相同head的Q→Q turbo overlays
main4 aggregate Q→Q
projected-Q→Q-on-reference turbo overlay
Q→R minus projected-Q→Q difference map
```

正式 raw metrics（panel min-max仅显示）：

```text
P_QR(R_t), P_QR(R_0), P_QR(Q_t→R)
Δ_ref-copy = P_QR(R_t)-P_QR(Q_t→R)
S50 H/L against R_t, R_0, Q_t→R
Q→R vs projected Q→Q:
  Pearson / Spearman / JSD
  center-of-mass distance
  peak displacement
```

关键预测：

```text
coordinate/query-map copy signature：
  QUERY-only时Q→R随Q→Q或Q_t→R移动；
  REF-only时Q→R不跟R_t；
  Q→R与projected Q→Q保持高相似。

reference-tracking signature：
  REF-only时Q→R跟R_t；
  QUERY-only时Q→R留在R_0/current reference object；
  Q→R与projected Q→Q分离。
```

完整报告 H/V/R180，sequence-paired bootstrap B=10000，不挑最好 transform。该实验仍是 attention-derived spatial signature：即使支持 tracking，也不证明 identity understanding；即使 map 相似，也必须结合独立 transform 位移才能称 coordinate-copy signature，不能把 map correlation 单独解释为信息被字面复制。

## R-015：条件触发的 prompt-bbox mismatch

仅当 R-014 无法区分视觉内容与显式 reference bbox cue 时运行：

```text
consistent：image+bbox一起变
image-only：只变图像
bbox-only：只变prompt bbox
```

后两者是有意 OOD mismatch，只作诊断，不进入自然性能或正常机制结论。

---

# 4. 新的依赖与停止规则

```text
R-006：已批准/授权，但本轮不自动执行
R-007：需用户重新批准；只读现有COCO，不下载
R-008：取消
R-009：需用户确认是否保留该可选Qwen外部正对照
R-010：因新增C/E/M×roles与可视化，需按新范围重新批准
R-011：R-010完成且冻结head sets后再审核
R-012–R-015：依次审核，不提前执行
```

停止规则：

1. R-006 row 对齐失败：修复后新 attempt，不启动依赖 row 的科学 run；
2. R-007 本地 COCO 缺少 RefCOCO 所需图片：报告缺口，不自动下载；
3. R-009 失败不阻塞当前 IPLoc-ID Core B/C，但不能声称 Qwen external positive control；
4. R-010 任一 outcome 的 sequence 数不足：扩数据，不放宽 IoU 阈值；
5. R-011 不复现 outcome-specific heads：R-014 不使用它们作 primary；
6. R-013 变换后行为大规模失败：R-014 降级为 OOD diagnostic；
7. 不因结果不显著而重选 head、组定义、transform 或 top50 阈值。

# 5. 最终 Claim 边界

即使所有 run 通过，最多支持：

```text
Qwen last-token方法在RefCOCO上有/无外部空间正对照；
IPLoc-ID correct/error可能共享heads、强度不同，或存在held-out稳定的outcome-specific attention routing；
Q→R spatial signature更符合reference tracking或query-coordinate copying。
```

仍不支持：

```text
causal head
identity-selective head
模型“理解”了reference
训练目标一定有效
```

这些仍需 E-004 causal patching、identity-switch 数据与自然行为改善实验。

## R-016：ICOL/LaSOT last-token row-stage 反证（待审核）

目标不是继续假定“last token 不定位”，而是用相同 query 图像做 prompt/task 与生成阶段分解：

```text
A 原始 IPLoc 双图 prompt
B 单图显式类别定位 prompt（Qwen 空间正对照）
C 双图 reference-conditioned 短定位指令
×
L last-input row / bbox各token p-1 rows / closing bracket / decision row
```

冻结 49/21 sequence discovery/evaluation；发现阶段仅用非GT budget×(1-entropy)，held-out 才用GT mass/S50/pointing；natural/gold replay分栏。必须明确：last-input row与first-generated-token预测row是同一row，不作为两个独立样本。四种解释输出为：premise falsified / prompt-specific / generation-emergent / unresolved（允许mixed）。Canonical run：

```text
shell/06_experiments/E-006/runs/
E006-R-016-icol-last-token-row-stage-falsification.md
```

当前 `pending_review`，未执行。
