# E-002 · 实验结果

> 同步原则：本文件的 Run ID 与远端 run-centric 目录 **一一对应**，即
> `/home/featurize/work/mechanism/explog/E-002/runs/<Run ID>/`。
> `.survey-tool/runs.json` 中 E-002 也使用同一 Run ID，避免再次出现本地登记号与远端目录错位。

## 运行总览

| Run | 性质 | 状态 | 审核重点 | 结论级别 |
|---|---|---|---|---|
| R-001-smoke-local-lasot-iplocid-n2 | 工程冒烟 | completed | IPLoc-ID + local LaSOT manifest + 输出解析是否可跑 | 不作科学结论 |
| R-001b-lasot-local-n20-compare | sanity baseline | completed | IPLoc-ID 是否有 negative rejection；IPLoc localization-only 是否高 FP | sanity only |
| R-002a-hard-patch-pilot-autoloop | image/patch proxy | completed | patch 内部 shuffle 是否影响 mIoU / FPR；仅用于 pilot | proxy only |
| R-003-token-hook-inspection | 工程前置 | completed | 是否找到 Qwen3-VL visual-token intervention 插入点 | 工程证据 |
| R-004-qwen3vl-token-hook-smoke | hook 冒烟 | completed | hook 是否实际改变输出 | 工程证据 |
| R-005-qwen3vl-full-visual-token-intervention-n10 | token destructive control | completed | 全视觉 token shuffle/zero 是否破坏 POIL negative rejection | 初步机制对照 |
| R-006-qwen3vl-object-token-shuffle-n10 | object-token order probe | completed | object footprint token shuffle 是否影响 POIL 决策 | 初步机制证据 |
| R-007-qwen3vl-object-token-ablation-n10 | object-token content probe | completed | object footprint token zero 是否影响 POIL 决策 | 初步机制证据，需 mean ablation 复核 |
| R-008-persistent-orchestrator-and-summary | 运维/汇总 | running | watchdog heartbeat + cross-run summary | 不作科学结论 |
| R-009-data-rehydrate | 数据再水化 | completed | 服务器恢复后派生数据是否重建且 missing=0 | 数据准备 |

## Run 详情

### R-001-smoke-local-lasot-iplocid-n2
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-001-smoke-local-lasot-iplocid-n2/`
- **目的/必要性**：最小 n=2 冒烟，确认 IPLoc-ID、local LaSOT manifest、role 语义、输出解析链路可用。
- **审核方式**：看 log 是否无 traceback；检查输出是否包含 reference / inclass negative / positive 以及 TP/TN/FP/FN 解析。
- **结论**：只证明链路可跑，不进入机制论证。

### R-001b-lasot-local-n20-compare
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-001b-lasot-local-n20-compare/`
- **目的/必要性**：普通 local LaSOT n=20 sanity，对比 IPLoc-ID 与 localization-only IPLoc 的 negative rejection。
- **指标**：
  - IPLoc-ID：TP=20, TN=19, FP=1, FN=0, F1=0.9756, negative_FPR=0.05
  - IPLoc：TP=20, TN=0, FP=20, FN=0, F1=0.6667, negative_FPR=1.0
- **解释**：说明 IPLoc-ID 协议适合后续 positive/negative POIL；IPLoc localization-only 只能作 sanity，不是主机制模型。
- **局限**：普通样本，不是 hard-token 机制实验。

### R-002a-hard-patch-pilot-autoloop
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-002a-hard-patch-pilot-autoloop/`
- **目的/必要性**：用图像 patch-level bbox 内 shuffle 快速 pilot hard subset 与聚合流程；**不是 token 机制主证据**。
- **数据/模式**：hard LaSOT；baseline/ref_shuffle/pos_shuffle/ref_pos_shuffle/all_obj_shuffle。
- **指标**：

| mode | mIoU | TP | TN | FP | FN | F1 | neg_FPR |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 0.561 | 30 | 29 | 1 | 0 | 0.984 | 0.033 |
| ref_shuffle | 0.481 | 28 | 29 | 1 | 2 | 0.949 | 0.033 |
| pos_shuffle | 0.272 | 30 | 29 | 1 | 0 | 0.984 | 0.033 |
| ref_pos_shuffle | 0.350 | 29 | 29 | 1 | 1 | 0.967 | 0.033 |
| all_obj_shuffle | 0.380 | 29 | 29 | 1 | 1 | 0.967 | 0.033 |

- **解释**：patch shuffle 明显影响 localization mIoU，但 negative_FPR 基本不变。
- **局限**：输入像素扰动会引入 artifact；不能替代 LLM-input visual-token intervention。

### R-003-token-hook-inspection
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-003-token-hook-inspection/`
- **目的/必要性**：机制实验前必须确认干预点，否则后续 token 结果不可审计。
- **确认插入点**：
  ```python
  image_embeds = image_outputs.pooler_output
  inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds)
  ```
- **模块证据**：包含 `base_model.model.model.visual`、`visual.merger`、`visual.deepstack_merger_list`。
- **输出**：`analysis/qwen3vl_module_inspection.json`
- **结论**：后续 R-004~R-007 的 hook 位置与 Mechanisms paper 的 “multimodal projection 后、LLM positional/autoregressive 前” 对齐。

### R-004-qwen3vl-token-hook-smoke
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-004-qwen3vl-token-hook-smoke/`
- **目的/必要性**：验证 hook 不是空操作。
- **模式**：baseline / visual_shuffle / visual_zero。
- **结果**：visual-token perturbation 改变 generated output / decision。
- **输出**：`analysis/hook_smoke_outputs.json`
- **结论**：hook 功能可用；n=1 冒烟不作机制结论。

### R-005-qwen3vl-full-visual-token-intervention-n10
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-005-qwen3vl-full-visual-token-intervention-n10/`
- **目的/必要性**：破坏性 control。若全视觉 token 干预都不影响模型，则 object-token 局部干预无解释力。
- **数据/模式**：hard LaSOT n=10；baseline / visual_shuffle / visual_zero。
- **指标**：

| mode | TP | TN | FP | FN | F1 | neg_FPR |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 10 | 8 | 2 | 0 | 0.909 | 0.20 |
| visual_shuffle | 10 | 0 | 10 | 0 | 0.667 | 1.00 |
| visual_zero | 10 | 0 | 10 | 0 | 0.667 | 1.00 |

- **解释**：全视觉 token shuffle/zero 使 negative rejection 崩溃，说明 POIL 决策确实依赖 visual embeddings。
- **局限**：destructive control，不单独说明 object-internal token 使用情况。

### R-006-qwen3vl-object-token-shuffle-n10
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-006-qwen3vl-object-token-shuffle-n10/`
- **目的/必要性**：核心 order probe。只打乱 bbox object-footprint token 顺序，测试模型是否依赖对象内部 token 空间顺序。
- **数据/模式**：hard LaSOT n=10；baseline / ref_obj_shuffle / query_obj_shuffle / ref_query_obj_shuffle / full_visual_shuffle。
- **干预细节**：visual-token-level；hook 点为 `image_outputs.pooler_output -> masked_scatter(inputs_embeds)` 前；footprint 是 **GT bbox_full approximation**，不是 instance mask，也不是 bbox center crop。bbox 映射到 Qwen3-VL merged visual grid，`gh=image_grid_h//2`, `gw=image_grid_w//2`，token cell 与 bbox 任意 overlap 即选中。shuffle 是选中 token values 内部 permutation，位置集合不变；ref/query/ref+query seeds 为 `1000+i`，full visual shuffle seed 为 `20260713`。selected token counts 保存在 `analysis/summary.json` 的 `hook_records_head.object_counts`。
- **当前不能回答的问题**：因为 R-006 用的是 bbox_full，所以不能回答“只 shuffle 物体最中心 bbox 区域是否更关键”。需要后续 `bbox_center_50` / `bbox_center_25` 扩大实验。
- **指标**：

| mode | TP | TN | FP | FN | F1 | neg_FPR |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 10 | 10 | 0 | 0 | 1.000 | 0.0 |
| ref_obj_shuffle | 10 | 10 | 0 | 0 | 1.000 | 0.0 |
| query_obj_shuffle | 10 | 10 | 0 | 0 | 1.000 | 0.0 |
| ref_query_obj_shuffle | 10 | 9 | 1 | 0 | 0.952 | 0.1 |
| full_visual_shuffle | 10 | 1 | 9 | 0 | 0.690 | 0.9 |

- **解释**：object-footprint token shuffle 基本不影响决策；full visual shuffle 强烈破坏 negative rejection。初步支持模型对 object-internal token order 使用不足。
- **局限**：n=10；LaSOT 用 bbox footprint 而非 segmentation mask；需扩大样本并加入 token-feature hard mining。

### R-007-qwen3vl-object-token-ablation-n10
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-007-qwen3vl-object-token-ablation-n10/`
- **目的/必要性**：核心 content probe。只消融 bbox object-footprint token，测试模型是否依赖对象内部 token 内容。
- **数据/模式**：hard LaSOT n=10；baseline / ref_obj_zero / query_obj_zero / ref_query_obj_zero / full_visual_zero / full_visual_shuffle。
- **干预细节**：visual-token-level；hook 点同 R-006；footprint 是 **GT bbox_full approximation**，不是 instance mask，也不是 bbox center crop。bbox 映射到 Qwen3-VL merged visual grid，`gh=image_grid_h//2`, `gw=image_grid_w//2`，token cell 与 bbox 任意 overlap 即选中。object zero 是把选中 token embeddings 置零；full_visual_zero 是全 visual token 置零；full_visual_shuffle seed 为 `20260713`。selected token counts 保存在 `analysis/summary.json` 的 `hook_records_head.object_counts`。
- **当前不能回答的问题**：R-007 是 bbox_full zero，不是中心区域 ablation；且 zero 不是 global/dataset mean replacement。需要后续 `bbox_center_*` 与 mean replacement 复核。
- **指标**：

| mode | TP | TN | FP | FN | F1 | neg_FPR |
|---|---:|---:|---:|---:|---:|---:|
| baseline | 10 | 10 | 0 | 0 | 1.000 | 0.0 |
| ref_obj_zero | 10 | 9 | 1 | 0 | 0.952 | 0.1 |
| query_obj_zero | 10 | 10 | 0 | 0 | 1.000 | 0.0 |
| ref_query_obj_zero | 10 | 10 | 0 | 0 | 1.000 | 0.0 |
| full_visual_zero | 10 | 0 | 10 | 0 | 0.667 | 1.0 |
| full_visual_shuffle | 10 | 0 | 10 | 0 | 0.667 | 1.0 |

- **解释**：object-footprint zero 基本不影响决策；full visual zero/shuffle 使 negative rejection 崩溃。初步支持 object-internal token content 低利用。
- **局限**：zero ablation 不是 Mechanisms paper 的 global/dataset mean embedding replacement；下一步必须做 mean ablation 复核。

### R-008-persistent-orchestrator-and-summary
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-008-persistent-orchestrator-and-summary/`
- **目的/必要性**：运维 run。保持 tmux heartbeat，避免 watchdog 把短实验正常结束误报为失败；汇总 R-005/R-006/R-007。
- **输出**：`analysis/e002_token_intervention_crossrun_summary.json`
- **状态**：running；tmux session `e002_autoloop`。
- **结论**：不产生新科学证据。

### R-009-data-rehydrate
- **远端目录**：`/home/featurize/work/mechanism/explog/E-002/runs/R-009-data-rehydrate/`
- **目的/必要性**：租用服务器恢复后，重建派生数据，保证后续 run 可复现。
- **结果**：
  - LaSOT sequence symlinks: 280
  - local POIL manifest: 140 samples, 420 images, missing=0
  - hard manifest: 50 samples, 150 images, missing=0
  - perturb variants: ref_shuffle / pos_shuffle / ref_pos_shuffle / all_obj_shuffle
- **路径**：
  - `/home/featurize/data/ICL_tracking/video/LASOT`
  - `/home/featurize/data/iplocid_manifests/LASOTTesting_1shot_T2_local.json`
  - `/home/featurize/data/e002_manifests/LASOT_hard_1shot_T2_n50.json`
  - `/home/featurize/data/e002_perturbed`
- **结论**：数据准备完成；不跑模型，不产生科学结论。

## 当前综合判断（谨慎）

R-005/R-006/R-007 的组合比单个 run 更有审核价值：

1. R-005 证明全视觉 token 干预会摧毁 negative rejection，排除“hook 无效/模型不看视觉”的解释。
2. R-006 显示只打乱 object-footprint token 顺序几乎不影响决策。
3. R-007 显示只置零 object-footprint token 也几乎不影响决策。

因此，当前 **初步** 支持：Qwen3-VL/IPLoc-ID 在该 hard LaSOT POIL 设置中，对 object-internal visual-token order/detail 的使用弱于对全图/非局部 visual structure 的使用。

但还不能写成强结论，因为：
- n=10 太小；
- object footprint 来自 bbox，不是 instance mask；
- R-007 用 zero，不是 global/dataset mean visual embedding；
- hard subset 还没有用 token-feature similarity 重新挖掘；
- 尚缺 copy-padding/container extension 与 token replacement/identity transfer。

## 下一步审核优先级

1. **R-010 planned**：object-token mean ablation，替代 zero ablation。
2. **R-011 planned**：object copy-padding/container extension，观察 bbox/decision 是否随 token footprint 扩张。
3. **R-012 planned**：token-feature hard mining，输出 unordered-similar / order-different hard negatives。
4. **R-013 planned**：token replacement / identity transfer。
