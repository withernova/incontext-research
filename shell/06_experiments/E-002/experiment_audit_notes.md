# E-002 project-specific audit notes

> 本文件记录 E-002 的项目内细节。跨项目通用填表规则见 `ledger_filling_skill.md`。

## 1. 当前核心问题

E-002 不是普通 POIL benchmark，而是验证：Qwen3-VL/IPLoc-ID 在 reference-conditioned instance identification/localization 中，是否没有充分利用 object-internal visual-token detail/order。

## 2. 当前 token hook 点

Qwen3-VL/IPLoc-ID 的 visual-token-level 干预点：

```python
image_embeds = image_outputs.pooler_output
inputs_embeds = inputs_embeds.masked_scatter(image_mask, image_embeds)
```

干预发生在 visual encoder / projector 后，visual embeddings scatter/merge 进 LLM input embeddings 前。

## 3. R-006 / R-007 已知干预细节

### R-006 object-token shuffle
- Run: `R-006-qwen3vl-object-token-shuffle-n10`
- 层级：visual-token-level。
- footprint：GT `bbox_full` approximation。
- 不是 segmentation mask。
- 不是 bbox center region。
- grid：Qwen3-VL `image_grid_thw`，merged grid 近似为 `gh=h//2`, `gw=w//2`。
- token 选择：token cell 与 bbox 任意 overlap 即选中。
- shuffle：选中 token values 内部 permutation，位置集合不变。
- modes：baseline, ref_obj_shuffle, query_obj_shuffle, ref_query_obj_shuffle, full_visual_shuffle。
- selected token counts 在 `analysis/summary.json` 的 `hook_records_head.object_counts`。

因此，R-006 不能回答“只 shuffle 物体最中心 bbox 区域是否影响更明显”。

### R-007 object-token zero ablation
- Run: `R-007-qwen3vl-object-token-ablation-n10`
- 层级：visual-token-level。
- footprint：GT `bbox_full` approximation。
- ablation：zero。
- 不是 global/dataset mean visual embedding replacement。
- 不是 bbox center ablation。

因此，R-007 需要后续 mean replacement 与 center-region ablation 复核。

## 4. 后续扩大实验必须包含的对照

下一批推荐：

1. `bbox_full` vs `bbox_center_50` vs `bbox_center_25` object-token shuffle。
2. object-token zero vs dataset/global mean replacement。
3. full visual shuffle / full visual mean replacement 作为 destructive controls。
4. n 从 10 扩大到至少 50；若时间足够，扩到 100/140。
5. 每个 run 必须保存 per-sample outputs、summary、selected token counts、mode metadata。

## 5. Token scale audit（2026-07-14）

R-010 可视化暴露一个关键混杂：当前 Qwen3-VL/IPLoc-ID hook 位于 `pooler_output` / merged visual tokens，LLM-input visual token 的空间 cell 约为 32×32 resized pixels，而不是 16×16。16px 更接近 merger 前 grid；我们的干预发生在 merger 后，因此实际被 shuffle 的 token 更粗。

对 `LASOT_hard_1shot_T2_n50` 现场诊断，使用 `max_side=640`、Qwen3-VL processor：
- merged token cell：median `32.0 × 32.7` resized pixels；
- bbox width：median 65.5 px，p25 28.6 px，min 10 px；
- bbox height：median 50.0 px，p25 25.0 px，min 8.5 px；
- bbox_full selected tokens：median 9，p25 4，70/200 prompt image instances ≤4 tokens，6/200 ≤1 token；
- bbox_center25 selected tokens：median 2，56/200 ≤1 token。

因此，许多小目标上的 object-token shuffle 很可能是弱干预甚至 no-op：1 个 token 无法 shuffle，2 个 token 也很弱。R-006/R-010 若不按 token footprint size 分层，不能直接解释为“内部顺序不重要”。后续必须：
1. 报告每个样本 selected token counts；
2. 按 token footprint size 分层看结果；
3. 构造 large-token-footprint subset，例如 full≥9/16 tokens、center50≥4 tokens；
4. 或提高 `max_side` 后复核，以增加小目标覆盖 token 数；
5. center25 若大量 ≤1 token，不应作为有效 shuffle 干预结论。

诊断输出：`/home/featurize/work/mechanism/explog/E-002/runs/R-010-qwen3vl-object-token-shuffle-n50-full-vs-center-vis/analysis/token_scale_diagnostic_live.json`。

## 6. 目前结论边界

可以谨慎说：
- R-005/R-006/R-007 初步显示 full visual token 扰动会破坏 negative rejection，而 bbox_full object-token shuffle/zero 影响较小。

不能说：
- 物体中心 token 不重要；因为 center-region 目前大量样本可能只有 1–2 个 merged tokens。
- segmentation mask object token 不重要；因为 LaSOT 当前用 bbox approximation。
- mean ablation 下也不重要；因为 R-007 用 zero。
- 已经证明机制；因为 n=10 且还缺 token-footprint-size 分层、large-object subset、copy-padding / identity transfer / hard-token mining。

## 7. R-010–R-015 补归档边界（2026-07-16）

- Exact run notes 已新增到 `shell/06_experiments/E-002/runs/`，文件名与远端目录一一对应。
- R-012 只称 replacement/stamping/contamination pilot，不称干净 identity transfer。
- R-014/R-014b/R-014c 的 p25/p50/p75/p100 定义不同：原版、deterministic center-out、sampled-bin center-out 不可混为同一剂量实现。
- R-014c 未记录 exact source→destination pairs；decision/FPR 与 box area 可用，exact box-follow 与旧 `actual_fraction` 不可作正式结果。
- `full_visual_shuffle` 是 concatenated support+query 全视觉 token stream 的 global permutation，可跨 image boundary；不是 query-only full-image shuffle。
- 当前 interventions 主要修改 `pooler_output`，deepstack features 可能保留未修改视觉信息。
- R-014/R-015 等 run 的 aggregate 指标相同或相近不等于 per-sample 行为相同；baseline 和 seed/path 也有波动。
