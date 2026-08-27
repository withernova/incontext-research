# E010-R-006 · 已选结果记录：T-003 阈值 GT-IoU 奖励

- recorded_at: 2026-08-27
- selected_by: 用户明确选择 T-003
- record_kind: 本地结果索引与解释记录；不改变 Survey Tool Run、审批、Claim 或授权状态
- source_status: 远端 T-003 计算产物已完成；原 campaign 的 Survey Tool completion contract 另有环境解析失败，不能据此把 campaign 标为正式 completed

## 选定方案

冻结 discovery 评分：

\[
-H_{norm} + 2\max(0, \mathrm{S50\text{-}fIoU}-0.1)
\]

- GT 只用于 discovery ranking。
- 输入固定为自然生成 Query bbox token 的 prediction rows 到 Reference image-token span 的 `q_to_r` attention。
- held-out 固定为 70 条、sequence-disjoint；禁止 head 重选。
- 选择 Frozen Top-5 作为主 readout：`L18H05, L12H00, L20H12, L7H25, L20H15`。

## 依据与结果

| 方法 / Top-5 | held-out pointing | fixed − layer-matched random | 95% bootstrap CI |
|---|---:|---:|---|
| **T-003 thresholded IoU（选定）** | **0.6143 (43/70)** | **+0.4946** | **[+0.3916, +0.5953]** |
| R-006 Base GT-frequency | 0.6000 (42/70) | +0.4631 | [+0.3594, +0.5661] |
| T-002 multiplicative IoU | 0.5714 (40/70) | +0.5076 | [+0.3986, +0.6164] |
| C-002 multiplicative IoU + max-token hit | 0.5429 (38/70) | +0.4193 | [+0.3187, +0.5194] |
| T-001 linear IoU | 0.0000 (0/70) | −0.0481 | [−0.0661, −0.0334] |

T-003 Frozen Top-3 为 `L18H05, L12H00, L20H12`：pointing=0.6000，fixed−random=+0.4853，CI=[+0.3837,+0.5857]。

### 选择理由

T-003 在已比较方案中给出最高的 Frozen Top-5 absolute held-out pointing（0.6143），相对随机的增益 CI 不跨 0；同时避免线性 IoU 方案的 Top-5 崩坏。T-002 的相对随机 margin 略大，但 absolute Top-5 pointing 较低；因此其保留为敏感性对照，不作为主方案。

## 可追溯来源（远端只读产物）

```text
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/
E010-R-006-gt-supervised-reference-head-stability-heldout-audit/
trials/T-003/analysis/summary.json
sha256: 992464304533990ce27b851c4a6e9ef1f07b80fb6932222d1d45e283e7f48152

/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/
E010-R-006-gt-supervised-reference-head-stability-heldout-audit/
trials/T-003/metrics.json
sha256: ed2d12128d0247da3e29c007d7c539754acee66b96c85d4c143901b1c8604704

R-006 Base source:
.../analysis/summary.json
sha256: 672da234a641c44582134a22beceee3cbf7ee7844b51b38821ff51b5e49f79ba
```

对应的 Base-vs-Trial 可视化：

```text
/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-010/
E010-R-006-gt-supervised-reference-head-stability-heldout-audit/
visualizations/gt_iou_reward_vs_r006/
```

## 结论边界

这是冻结 R-003 natural `q_to_r` attention artifacts 上的 **GT-supervised offline diagnostic readout**。它不支持无 GT selector 可部署、模型使用 GT、identity binding、head 因果必要性或训练外泛化。70/70 是 selection-held-out sequence split，训练暴露未知。
