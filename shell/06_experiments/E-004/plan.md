# E-004 Plan

## Gate 0：实现审计
- Qwen3-VL text model：36 layers、32 query heads、8 KV heads、head_dim=128、hidden=4096。
- head-output ablation hook：`language_model.layers[L].self_attn.o_proj` 的 **forward pre-hook**；其输入最后一维4096是32个 query-head slices，置零 `[h*128:(h+1)*128]`。
- 必须做 no-op hook equality、all-head≈layer-attention-output-zero、单-head deterministic repeat。

## R-001：synthetic 2×2 behavioral sanity
- 从同类别不同 LaSOT sequences 取 A/B object crops；放到统一双面板 query。
- reference A/B 保持各自原图与 bbox。
- candidate A/B 是 composite 上两个实例框。
- 检查 `M(A,A), M(A,B), M(B,A), M(B,B)`；若 matched 不优于 mismatched，不进入大规模 head scan。

## R-002：layer ablation smoke
- 对通过 behavioral gate 的1–4个 quartet，扫36层。
- score：clean margin 与 layer attention-output ablation 后 margin delta。
- control：no-op hook；记录显存、模型模块名、LoRA状态、token IDs。

## R-003：top-layer per-head scan
- 只在 R-002 top layers 内扫32 heads；先选 top-20 decision heads。
- equal-count low-effect heads 作为 control；做 cumulative ablation 验证 ranking necessity。

## R-004：token-group causal routing
- 划分 reference object/background、query A/B/background、category/instruction/bbox。
- 对 top heads 做 group-specific attention knockout/value contribution ablation。
- 指标：reference-conditioned routing shift、target-over-distractor、causal grounding selectivity。

## R-005：bbox circuit comparison
- teacher-force bbox coordinate tokens，以 coordinate NLL 为 localization score。
- 重复 ranking 并计算 top-k Jaccard/rank correlation。
