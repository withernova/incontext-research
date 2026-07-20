# E-003 优先实验细化协议

## 总目标

把当前“identification-only F1 与 joint correctness 解耦”的观察拆成三个可检验问题：

1. **评测有效性**：低 IoU 是否由坐标、解析或 annotation 异常造成？
2. **候选依赖性**：最终 Yes/No 是否随固定 candidate region 改变？
3. **统计稳定性**：Joint F1 gap 是否跨重采样、类别和 IoU threshold 稳定？

严格边界：数据是本地 deterministic LaSOT reconstruction，不是官方 IPLoc-ID split。

---

## E003-R-005b · Prefix-conditioned forced-candidate pilot（当前优先运行）

### 研究问题

同一 reference/query pair 不变时，只改变附加在 query 后的 bbox prefix，verifier continuation 的 Yes/No 是否系统响应 candidate 内容与位置？

### 数据与规模

- manifest：`LASOT_local_1shot_T2_n140_v2.json` 前20 samples；
- 20 positive + 20 same-class negative target cases；
- 每个 target 6 modes，完整性门槛为240 records；
- 模型与 LoRA 同 E003-R-004b。

### Candidate modes

1. `generated_candidate`：E003-R-004b 自然生成框；
2. `annotated_target` / `annotated_distractor`：该 query annotation；
3. `shifted_annotated`：与 annotation IoU<0.1 的等尺寸偏移框；
4. `background_matched_size`：四角中与 annotation IoU 最低的等尺寸框；
5. `contracted_annotated_50pct`：中心不变，宽高各缩为50%；
6. `expanded_annotated_150pct`：中心不变，宽高各放大为150%，并裁剪到图像。

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

## E003-R-006 · Low-IoU identification-TP audit（R-005b 后立即执行）

### 输入集合

E003-R-004b 中：

```text
role=positive-image
pn_label=positive
full_iou_for_all_targets < 0.1
```

预期35例。完整性检查必须重新由 outputs 计算，不硬编码35作为成功结果。

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

### 输出

```text
analysis/low_iou_audit.json
analysis/low_iou_audit.md
visualizations/*.png
visualizations/manifest.json
```

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
