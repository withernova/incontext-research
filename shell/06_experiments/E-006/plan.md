# E-006 · 简洁的 attention-on-GT 与联通子图审计

- status: running
- kind: attention_spatial_support_audit
- source_ref: E005-R-033
- claim_refs:
- priority: high
- created: 2026-07-28T23:21:49
- updated: 2026-07-28T23:23:00

## 实验目标

用一个固定、可视化且逐 head 的规则，比较 localization-error 与 localization-correct：

```text
1. 每个head的主要attention区域有没有碰到GT？
2. 整个image-span attention是否有超过一半落在GT？
3. 主要attention区域有多少个4邻域联通子图？
4. 其中多少个联通子图碰到GT？
```

同时审计：

```text
G→R：reference grounding heads → reference GT
Q→R：query localization heads → reference GT
Q→Q：query localization heads → query GT
```

## 数据

仅使用 E003-R-004b positive natural-Yes 的两个端点：

```text
localization-error：IoU<0.1，n=35
localization-correct：IoU>=0.7，n=76
```

不混入 partial、FN、negative。

## 冻结 heads

```text
G→R：L15H13,L16H23,L18H15
Q→R：L18H15,L19H03,L22H00,L20H08
Q→Q：L18H15,L19H03,L22H00,L20H08
```

主统计逐 head 报告，不先池化 heads。

## 唯一 support-mask 规则

对每个 head、每个目标 image span：

1. 在对应 bbox token 的全部 `p-1` rows 上取均值；
2. 仅在目标 image span 内将非负 attention 归一化为总和 1；
3. 从高到低取最少 token，直到累计 attention `>=50%`；
4. 这些 token 构成 `top50 attention support`；
5. 在 merged-token grid 上按 **4-neighbor** 计算联通子图。

固定 50%，不扫描阈值，不选择最显著 cutoff。

## 指标

```text
support-hit：top50 support至少一个token与GT有fractional overlap

majority-on-GT：整个image-span attention的fractional GT mass >50%

components：top50 support的4-neighbor联通子图数

GT-components：其中碰到GT的联通子图数

largest-component-hit：最大联通子图是否碰到GT
```

同时记录：

```text
selected-token-count
top50-selected-mass
GT-token-coverage
image grid
```

GT overlap 使用 bbox 对 merged-token cell 的 fractional occupancy，不是 pixel segmentation。

## 统计

每个 role × head × group：

```text
n
support-hit count/rate + Wilson 95% CI
majority-on-GT count/rate + Wilson 95% CI
largest-component-hit count/rate + Wilson 95% CI
components median [Q1,Q3]
GT-components median [Q1,Q3]
selected-token-count median [Q1,Q3]
correct-error difference + bootstrap 95% CI
```

每个样本输出 11 个逐-head support overlays：

```text
G→R 3 heads on reference
Q→R 4 heads on reference
Q→Q 4 heads on query
```

橙色格=`top50 support`，绿色框=GT。标题：

```text
H=support hit
M=majority on GT
C=component count
CG=GT component count
L=largest component hit
```

## 成功与失败标准

- 成功：脚本对全部111样本、11个head-maps输出完整，定义/rows/span/grid hard gate通过。
- 科学结果不预设必须有组差；零结果照实报告。
- 不用单个阈值显著性决定成功，不重选head。

## 运行设置

```text
Qwen3-VL-8B-Instruct + IPLoc-ID LoRA
max_side=640（公开代码默认；非论文明确设置）
bf16
HF eager attention
双RTX4090，22GiB/GPU上限
teacher replay archived natural bbox
```

## 结论边界

- attention support 是相关性描述，不是 causal influence。
- Q→Q 与自然预测正确性紧密耦合，主要作为 sanity check。
- `majority-on-GT` 很严格，低频时不事后放宽。
- 单bbox与非穷尽LaSOT标注不能确认wrong-instance。
- split为本地确定性重建，不是官方IPLoc-ID split。

## R-005 后续 validity 修复链（2026-08-03 用户审核后 v2）

R-005 完成后识别出四个必须解决的问题：

```text
1. R-005用bbox p-1 rows，而公开LocalizationHeads使用last input token；
2. 缺少Qwen在RefCOCO上的外部空间正对照；
3. correct/error可能使用不同active/aligned heads，pooled mix可能掩盖差异；
4. Q→R可能复制query坐标，而非跟随reference object。
```

完整修订协议：

```text
shell/06_experiments/E-006/followup_validity_and_equivariance_plan.md
```

审核后的顺序：

```text
R-006 exact last-token alignment gate（已批准/授权，尚未执行）
R-007 使用服务器现有COCO构建RefCOCO expression manifest；按image_id防跨split泄漏
R-008 cancelled：用户限定Qwen，不运行LLaVA
R-009 可选Qwen-only RefCOCO last-token空间正对照
R-010 旧批准稿保留但不执行
R-010b C/E/balanced-mix × G→R/Q→R/Q→Q/T→R/T→Q全head发现与可视化
R-011 fresh 3×2 cross-evaluation
R-012 transform geometric separability
R-013 natural behavior transform gate
R-014 reference-vs-query coordinate equivariance
R-015 visual-content vs prompt-bbox mismatch（条件触发）
```

`unique-image`不是公开LocalizationHeads原文规定；公开README只写RefCOCO train的1000 data samples。v2中的`image_id` group split是本地anti-leakage设计，`n=1220`指expression samples。
