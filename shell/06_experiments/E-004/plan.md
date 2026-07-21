# E-004 Plan

## 重启恢复 Gate（2026-07-20）

服务器重启后必须先检查并恢复三类非持久化资源：

1. `/home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json`：从持久化 `LaSOTTesting` 用确定性脚本重建，强制 `140 samples / 70 classes / missing=0 / invalid_bbox=0`；
2. Python user-site：恢复并锁定 `transformers==4.57.3 / peft==0.18.0 / accelerate==1.12.0 / qwen-vl-utils`；
3. Qwen3-VL snapshot：缓存到持久化 `/home/featurize/work/.hf_cache`，后续使用 local/offline mode，避免再次依赖 ephemeral `/home/featurize/.cache`。

任何恢复 run 都是 environment/data audit，不得作为科学结果。

## Gate 0：实现审计
- Qwen3-VL text model：36 layers、32 query heads、8 KV heads、head_dim=128、hidden=4096。
- head-output ablation hook：`language_model.layers[L].self_attn.o_proj` 的 **forward pre-hook**；其输入最后一维4096是32个 query-head slices，置零 `[h*128:(h+1)*128]`。
- 必须做 no-op hook equality、all-head≈layer-attention-output-zero、单-head deterministic repeat。

## R-001：synthetic 2×2 behavioral sanity
- 从同类别不同 LaSOT sequences 取 A/B object crops；放到统一双面板 query。
- reference A/B 保持各自原图与 bbox。
- candidate A/B 是 composite 上两个实例框。
- 检查 `M(A,A), M(A,B), M(B,A), M(B,B)`。
- 首个 n=4 pilot 的 hard gate（至少1组四条件全对）未通过，因此不把后续结果命名为已验证的 identity circuit。
- 用户要求完整尝试后，允许继续做 **diagnostic head scan**，但必须：
  - 同时报告所有 quartet，不只挑成功样本；
  - 将结论限定为 synthetic prefix-conditioned causal diagnostic；
  - 明确弱 behavioral substrate 与 exposure/composite shift；
  - 在可视化中显示四条件 margin，防止仅凭 attention 图过度解释。

## R-002：layer ablation smoke（仅工程漏斗，非论文式 CMA）
- 对全部 synthetic quartets 扫36层，记录 clean margin 与整层 attention-output zero-ablation 后的 margin delta。
- control：no-op hook；记录显存、模型模块名、LoRA状态、token IDs。
- **边界：**该方法只能发现影响 Yes/No 极性的层，不能据此选择“身份信息中介 head”，也不能替代 [[mechanisms2026]] §3.3.2 的 source→base activation patching。
- 2026-07-20 已完成的 R-007 应永久标记为 `layer-output ablation diagnostic`；不得将其排名称作 CMA/MF head ranking。

## R-003：论文对齐的 source→base causal mediation analysis（主 head 发现方法）
### R-003a：source/base 构造与行为 Gate
- 参照 [[mechanisms2026]] §2.2、§3.3.2：source 保留相关候选物体；base 在**同一图像、同一尺寸、同一 prompt 与同一 candidate box**下移除该物体。
- 论文主方法使用 diffusion-based inpainting；若当前仅能使用 synthetic neutral-canvas removal/非生成式填补，必须命名为 `controlled object-removal proxy`，不得声称与论文 inpainting 完全等价。
- 只允许满足以下条件的 pair 进入主 CMA：source 对 gold answer 正确且有预注册最小 margin；base 对 gold answer 失败，或 teacher-forced gold NLL 明显恶化；`input_ids`、attention mask、序列长度、`image_grid_thw` 与 image-token spans 可对齐。
- 所有未通过 pair 必须保留并报告，不得静默丢弃；discovery/evaluation split 必须分离。

### R-003b：逐 head activation patching 与 Mediation Fraction
- 对每个 `(layer, head)`：缓存 source run 的 `self_attn.o_proj` pre-input head slice，并移植到 base run 的严格对齐 prompt positions，得到 patched run。
- Qwen3-VL 单 head slice 为 `[h*128:(h+1)*128]`；该操作命名为 **head-output activation patching**，不冒充 attention-edge patching。
- 主要 score 采用 teacher-forced gold-token NLL/perplexity，并按论文定义：
  \[
  MF_h=\frac{P_{base}-P_{patched,h}}{P_{base}-P_{src}}.
  \]
  固定模板 token 不进入 score；binary verifier 只计 gold `Yes`/`No` token。Yes−No margin MF 仅作配套诊断。
- 必须保存 `P_src/P_base/P_patched`、分母、MF、patch token positions/count、source/base token-alignment hash、layer/head、pair id；分母过小的 pair 标记 undefined，不得用 epsilon 制造 MF。
- 正式 head 排名按跨 pair mean/median MF、bootstrap CI、positive-MF rate 与方向一致性；**不按 R-007 的 zero-ablation `|ΔM|` 排名**。

### R-003c：reference-switch CMA（E-004 身份绑定扩展）
- 保持 query 与 candidate 完全相同，仅切换 Reference A/B；双向执行 `A→B` 与 `B→A` activation patching。
- 同时报告四条件，不允许只选能恢复 Yes 的方向；排除统一 Yes/No polarity head。
- 只有 patching effect 随 reference identity 双向切换、跨 quartet 一致，且通过 held-out pair 验证，才可称 identity-routing candidate；否则仍是 `synthetic prefix-conditioned causal diagnostic`。

### R-003d：必要性复核
- 按 CMA mean MF 排名做 cumulative head-output ablation；比较 equal-count low-MF、random heads 与 polarity-matched controls，参照 [[mechanisms2026]] §3.3.3。
- discovery 用于排序、held-out evaluation 用于曲线；不得在同一小样本上选择并宣称泛化。

## R-004：token-group causal routing
- 划分 reference object/background、query A/B/background、category/instruction/bbox。
- 对 top heads 做 group-specific attention/value masking；若当前 attention backend 不支持精确 source-token knockout，则先做 **head-output × token-group activation patching**，并明确它不等价于 attention-edge knockout。
- 指标：reference-conditioned routing shift、target-over-distractor、causal grounding selectivity。
- Qwen3-VL 两张图像的视觉 token spans 必须由 `input_ids==image_token_id` 与 `image_grid_thw` 联合核验；query A/B token cells 根据 composite bbox→merged grid overlap映射。
- raw attention 仅作为可视化辅助；正式排序仍以 margin causal effect 为准。

## R-005：bbox circuit comparison
- teacher-force自然 positive 的 bbox coordinate tokens，以 coordinate token NLL 为 localization score；不得把整段 bbox 当单 token。
- 重复 layer/head ranking并计算 top-k Jaccard、rank correlation与matched random-head controls。
- 若 coordinate tokenization/归一化无法一一对齐，run 标记 incomplete，而不是用替代的最终 Yes/No margin 冒充 localization circuit。

## 可视化审核包

至少输出：

1. 每个 synthetic quartet：reference A/B、query composite、candidate A/B boxes、四条件 margin/prediction；
2. 36层 causal-effect heatmap；
3. top layers 的 layer×head effect heatmap；
4. top-head cumulative ablation curve，对照 equal-count low-effect/random heads；
5. token-group causal-effect matrix；
6. localization vs identification head overlap matrix/UpSet-style列表；
7. `visualizations/manifest.json`，记录每张图对应样本、条件、run与源JSON。

PNG 必须保存完整画布；优先用 matplotlib直接导出，若从SVG导出则使用 headless Chrome。
