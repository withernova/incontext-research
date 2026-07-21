# E-003 优先实验细化协议

## 总目标

把当前“identification-only F1 与 joint correctness 解耦”的观察拆成三个可检验问题：

1. **评测有效性**：低 IoU 是否由坐标、解析或 annotation 异常造成？
2. **候选依赖性**：最终 Yes/No 是否随固定 candidate region 改变？
3. **统计稳定性**：Joint F1 gap 是否跨重采样、类别和 IoU threshold 稳定？

严格边界：数据是本地 deterministic LaSOT reconstruction，不是官方 IPLoc-ID split。

---

## 历史协议：E003-R-005b · Prefix-conditioned forced-candidate pilot（已废弃，不再作为当前优先实验）

### 研究问题

同一 reference/query pair 不变时，只改变附加在 query 后的 bbox prefix，verifier continuation 的 Yes/No 是否系统响应 candidate 内容与位置？

### 数据与规模

- manifest：`LASOT_local_1shot_T2_n140_v2.json` 前20 samples；
- 20 positive + 20 same-class negative target cases；
- 每个 target 6 modes，完整性门槛为240 records；
- 模型与 LoRA 同 E003-R-004b。

### Candidate modes（历史记录，不得用于下一主实验）

旧设计包含`generated/annotated/shifted/background/contracted/expanded`等区域敏感性条件。经设计复核，这些条件不能替代reference identity switch，尤其`background_matched_size`对核心双向identity-binding问题无必要，已从后续科学实验完全删除。历史failed/aborted run只作审计保留，不得沿用为主设计。

### 当前唯一主设计

获得真实双实例、双reference数据后，仅运行：

```text
reference A + query(A,B) + candidate A → Yes
reference A + query(A,B) + candidate B → No
reference B + query(A,B) + candidate A → No
reference B + query(A,B) + candidate B → Yes
```

固定同一query pixels和candidate A/B，只切换reference identity。主指标为all-four-correct、双向binding gap和固定candidate下的reference-switch flip。不加入背景candidate。

### 实现

通过 `build_messages(..., query_box_text=<pixel xyxy>)` 使用仓库原坐标函数转换到模型0–1000格式，再只生成 verifier continuation。主生成长度48 tokens。

### 指标

- `YesRate(role, mode)`；
- target-level candidate-dependence rate：同一 target 的6个条件中是否同时出现 Yes 与 No；
- positive：`YesRate(GT)-YesRate(background)`、`YesRate(GT)-YesRate(shifted)`；
- negative：`YesRate(distractor)` 及其相对 background/shifted 的变化；
- per-sample response pattern 和 parser failure count。

### 成功门槛

- 240 records；每个 role/mode恰好20条；
- 无 traceback/processor skip；
- 输出均可解析 Yes/No；否则 run 标为 incomplete/failed，而不是补零。

### 解释

- GT 高、background/shifted 低：支持 verifier 对 candidate region 敏感；当前 joint gap 更可能包含 proposal/localization failure。
- 各 candidate 的回答近似不变：支持 localization-verification decoupling 假设。
- 仅对 scale 响应：提示 geometry/size sensitivity，而非充分 identity verification。
- negative distractor 持续 No、但 negative background 转 Yes：说明反应存在，但不一定遵循 identity semantics。

### 必须保留的 caveat

这是 **prefix-conditioned verifier probe**。训练时 bbox prefix 通常来自自然 autoregressive history；外部强制 prefix 有 exposure shift，不能单独证明自然生成 verifier 完全忽略 candidate。

---

## E003-R-006 · Rejection-linked low-IoU bbox audit（已完成）

### 输入集合

E003-R-004b 全部140个positive/negative pairs，同时预注册分层：

```text
all positive
identification TP
identification TP && IoU<0.5
identification TP && IoU<0.1
```

低IoU数量由outputs重算，不硬编码。最终为44与35例。

### 自动检查

- 原图尺寸、GT/pred xyxy 合法性与边界；
- raw model 0–1000 bbox → pixel bbox 的重新转换；
- 与保存的 `pred_bbox_pixel_format` 一致性；
- xyxy/xywh alternative interpretation 只作 bug diagnostic，不选择性替换结果；
- GT 是否匹配 manifest path/frame/annotation line；
- pred/GT 面积比、中心距离、边界裁剪、IoU。

### 可视化

每例一张 PNG：reference image+reference GT；query image+query GT（绿）+prediction（红）；blank sidebar 写 sample、class、sequence、IoU、raw text。不得让文字覆盖图像。

### 分类

自动 geometry tags + 人工审核列：

```text
wrong_instance / object_part / oversized_container / background_region /
coordinate_or_parser_suspect / annotation_suspect / uncertain
```

自动规则不能冒充人工语义判断。

### 配对拒绝框关联

每个sample登记`positive GT/prediction + paired negative annotation/prediction`。各框独立映射至本图的`[0,1]^2`单位画布，主距离是normalized xyxy corner RMSE；对照是同类别另一sample的negative box，并做10,000次类内permutation与sample bootstrap。

结果未支持“paired rejected bbox更近”：

```text
IoU<0.1 TP, n=35
posPred→paired negPred RMSE=0.2880
posPred→same-class control=0.2527
delta=+0.0353, paired-closer=0.400, p_lower=0.9180

posPred→paired negGT RMSE=0.2924
posPred→same-class control=0.2772
delta=+0.0152, paired-closer=0.429, p_lower=0.6637
```

辅助发现：83/140 negative generated candidates达到自身distractor annotation IoU≥0.5，其中82个最终回答No。这表明模型经常可以定位同类distractor后执行identity rejection；与sequential design相容，不能写成论文缺陷。

### 输出

```text
analysis/summary.json
analysis/summary.md
results/per_sample_geometry.json
visualizations/*.png
visualizations/manifest.json
manifests/provenance.json
```

解释补充：`runs/E003-R-006-rejection-linked-bbox-audit-n140.interpretation.md`。

### 下一审计

contact sheets提示部分positive错误框可能落在**同一positive图像内的另一个同类实例**。这是非正式观察。下一run应补多实例annotation/人工taxonomy，直接计算target GT与non-target same-class boxes，而不是把跨图像归一化geometry误当成identity overlap。

---

## E003-R-007 · Paired bootstrap + group audit（离线）

### 重采样单位

以 sample 为 cluster，每个 sample 的 positive 与 negative 一起重采样；禁止把280 records当完全独立样本。

### 指标

- identification F1；Joint F1@0.3/0.5/0.7；
- paired difference `Identification F1 - Joint F1@τ` 的95% percentile CI；
- positive Yes recall、negative FPR；
- class-level和 sequence-level distribution；
- worst-decile group结果仅作 exploratory，标注小组样本不稳定。

建议10,000 bootstrap replicates，固定 seed 并保存 replicate summaries/hash。

---

## E003-R-008 · Forced-candidate expansion

只有 R-005b 满足完整性且 parser failure 可控后执行。

- 扩到 n=140；
- 保持 candidate definitions 不变；
- 预注册主要比较为 positive GT vs matched background、GT vs shifted；
- 报 paired bootstrap CI；
- 可补 generation first-token Yes/No logits，但 logits 是辅助诊断，不替代文本 decision。

---

## 执行顺序

```text
R-005（失败：缺 PYTHONPATH，保留审计）
→ R-005b（中止：bbox fallback parser 不适用）
→ R-005c（中止：candidate 被放在 user turn，未形成 assistant prefix）
→ R-005d（中止：assistant-prefix 自由生成仍有歧义文本）
→ R-005e forced-candidate Yes-vs-No next-token logit n20（运行中）
→ R-006 low-IoU audit
→ R-007 paired bootstrap
→ 根据 R-005b gate 决定是否运行 R-008 n140
```
