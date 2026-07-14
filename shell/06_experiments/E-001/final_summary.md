# E-001 阶段总结：Rex-Omni / Qwen2.5-VL 上的 containerization 行为验证

> 状态：阶段性收束；不再继续投入 R-007 自造配置数据集。后续转向 E-002：使用 `personal2026` / POIL 数据集与协议。

## 1. 原始目标
E-001 的目标是把 Mechanisms of Object Localization 论文中的 containerization 干预思想迁移到 Rex-Omni / Qwen2.5-VL 的实际推理路径上，观察：

1. support/reference object 内部 token 顺序扰动是否显著影响 visual-prompt localization；
2. full-image token shuffle 是否作为破坏性对照显著降级；
3. query-side object token footprint 扩大是否会让预测框呈现 container-like 扩张；
4. Rex-Omni 是否真正进行 instance/configuration-level matching，还是更接近 category/container-level matching。

## 2. 工程成果

### 2.1 远程环境与仓库
- 远程：`featurize`
- 远程仓库：`/home/featurize/work/mechanism/Rex-Omni`
- 本地 checkpoint：`/home/featurize/work/mechanism/checkpoints/Rex-Omni`
- COCO 数据：`/home/featurize/data/COCO2017`
- 重要运行约束：`PYTHONNOUSERSITE=1`
- 按用户要求，远程 Rex-Omni 仓库已重置为无 remote 的私有本地 git 仓库。

### 2.2 vLLM-native token intervention 路径
完成了 vLLM 官方推理路径上的本地子类 patch，而不是改 site-packages 或走 HF generate：

- `rex_omni/vllm_e001_qwen25vl.py`
- `rex_omni/token_interventions.py`
- `evaluation/inference_visual_prompt_vllm_token_intervention.py`

核心 patch 点：

```python
Qwen2_5_VLForConditionalGeneration._process_image_input(...)
```

干预位置位于：

```text
pixel_values -> self.visual(...) -> image_embeds -> split/merge into LLM inputs
```

这使我们可以在 Qwen2.5-VL visual embeddings 被 scatter/merge 到 LLM input embeddings 前做 token-level shuffle / padding / replacement。

### 2.3 数据与评测脚本
构造了 formal mixed60 multi-target COCO visual-prompt 数据：

```text
/home/featurize/work/mechanism/explog/E-001/coco_visual_prompt_mixed_h10_n20_e30_multi_nocrowd.jsonl
```

特点：
- hard 10 / normal 20 / easy 30；
- `iscrowd == 0`；
- easy 样本也要求同类别多实例，避免 support/query 退化为唯一目标；
- token region 从 bbox footprint 升级为 COCO instance mask footprint。

新增/使用的主要脚本包括：
- `evaluation/build_coco_visual_prompt_jsonl.py`
- `evaluation/evaluate_e001_miou.py`
- `evaluation/visualize_e001_predictions.py`
- `evaluation/visualize_e001_token_intervention.py`
- `evaluation/evaluate_e001_box_shift.py`
- `evaluation/evaluate_e001_candidate_identity.py`
- `evaluation/build_e001_granularity_probe.py`
- `evaluation/inference_e001_granularity_probe_box.py`
- `evaluation/build_e001_internal_token_pairs.py`
- `evaluation/inference_e001_internal_token_replacement.py`

## 3. 主要实验结果

### 3.1 R-001：vLLM patched baseline / no intervention
输出目录：

```text
/home/featurize/work/mechanism/explog/E-001/R-001-vllm-patched-mixed60-multi
```

指标：

```json
{
  "num_samples": 60,
  "total_gt": 296,
  "total_pred": 491,
  "mIoU_gt_best": 0.6185839183091179,
  "mIoU_pred_best": 0.39337641887887187,
  "recall_at_0.5": 0.6655405405405406,
  "pred_match_rate_at_0.5": 0.39918533604887985
}
```

意义：建立 Rex-Omni/vLLM 官方路径的可用 baseline。

### 3.2 R-002：support-only within-object mask token shuffle
输出目录：

```text
/home/featurize/work/mechanism/explog/E-001/R-002-vllm-token-support-mask-mixed60-multi
```

指标：

```json
{
  "num_samples": 60,
  "total_gt": 296,
  "total_pred": 500,
  "mIoU_gt_best": 0.6006270789920304,
  "mIoU_pred_best": 0.382737617825999,
  "recall_at_0.5": 0.6621621621621622,
  "pred_match_rate_at_0.5": 0.398
}
```

相对 R-001：
- `mIoU_gt_best` 约下降 `0.018`；
- recall 几乎不变；
- 表明 support-side 内部 token 顺序扰动只造成小幅降级。

谨慎解释：这支持“Rex-Omni 对 support-side 内部 token 排列较鲁棒”，但不能证明模型完全忽略内部结构。

### 3.3 R-003：full image-token shuffle
输出目录：

```text
/home/featurize/work/mechanism/explog/E-001/R-003-vllm-token-full-mixed60-multi
```

指标：

```json
{
  "num_samples": 60,
  "total_gt": 296,
  "total_pred": 1800,
  "mIoU_gt_best": 0.2640872132444594,
  "mIoU_pred_best": 0.09128431211423715,
  "recall_at_0.5": 0.28040540540540543,
  "pred_match_rate_at_0.5": 0.04555555555555556
}
```

意义：全局视觉 token 结构被破坏后性能显著崩塌，说明模型仍依赖整体视觉 token 结构；R-002 的鲁棒性不是因为干预机制无效。

### 3.4 R-004 / R-004b / R-004c：padding 系列

#### R-004 原始 support-side padding
原 R-004 只扩展 support/reference prompt box。用户澄清后，该设计对“query-container claim”无效。

已写明无效说明：

```text
/home/featurize/work/mechanism/Rex-Omni/tmp/e001/R4_INVALID_SUPPORT_PADDING.md
```

#### R-004b expanded-GT post-hoc diagnostic
R-004b 在评估端扩展 query GT box，只是诊断 baseline 预测是否更接近“过大 container”，不是 causal intervention。

#### R-004c true query-object token padding / copy-ring
输出目录：

```text
/home/featurize/work/mechanism/explog/E-001/R-004c-query-token-padding-mixed60-multi
```

mIoU：

```json
{
  "num_samples": 60,
  "total_gt": 296,
  "total_pred": 611,
  "mIoU_gt_best": 0.5353971067495498,
  "mIoU_pred_best": 0.2971213592465801,
  "recall_at_0.5": 0.6013513513513513,
  "pred_match_rate_at_0.5": 0.3011456628477905
}
```

box-shift：

```json
{
  "num_matched_gt": 296,
  "mean_area_ratio_intervention_over_baseline": 1.222334420009315,
  "mean_area_delta_over_gt": 0.12673292925578494,
  "fraction_area_increased": 0.5912162162162162,
  "mean_iou_delta": -0.08318681155956781
}
```

解释：query object token footprint 扩张会让预测区域有变大的趋势，但同时 IoU 降级、预测数增加。因此这是“query-side object visual embeddings 影响预测框”的 causal 证据，但不是纯粹证明 containerization 的充分证据。

### 3.5 R-005 / R-005b / R-005c：identity / granularity probes

R-005b synthetic RGB marker probe 暴露出 zero-shot candidate-ID 输出格式不稳定，模型强烈保持 detection-output prior，因此不能作为干净 verifier 证据。

R-005c 改成 box-output granularity probe 后，减少了接口错配。关键结果：

```text
category          F1 0.439, exact 0.300
natural_instance  F1 0.117, exact 0.050
pattern           F1 0.340, exact 0.000
configuration     F1 0.417, exact 0.050
configuration selects a*: 0.850
configuration selects a†: 0.900
```

解释：Rex-Omni 可以输出框，但在 configuration-level 区分上很弱；尤其 arrangement-defined condition 下同时高频选择 a* 与 swapped a†，更像 component/category/container-level matching。

### 3.6 R-006 / R-006b：cross-image same-category internal-token replacement

R-006：same-category donor token replacement：

```json
{
  "num_samples": 20,
  "total_gt": 55,
  "total_pred": 50,
  "mIoU_gt_best": 0.1683,
  "mIoU_pred_best": 0.1770,
  "recall_at_0.5": 0.0364,
  "pred_match_rate_at_0.5": 0.0400
}
```

R-006b：same 20 pairs no-intervention baseline：

```json
{
  "num_samples": 20,
  "total_gt": 55,
  "total_pred": 51,
  "mIoU_gt_best": 0.7933,
  "mIoU_pred_best": 0.8485,
  "recall_at_0.5": 0.8727,
  "pred_match_rate_at_0.5": 0.9412
}
```

解释：query-side object visual embeddings 作为整体对预测高度关键。但当前 R-006 是 donor-visible two-image fast implementation，混入了 texture/color/boundary/context 破坏，不能隔离“内部排列顺序”。

## 4. 阶段性科学结论

### 可以保留的结论
1. Rex-Omni / Qwen2.5-VL 官方 vLLM 路径上，token-level intervention 工程链路已打通。
2. Support-side object mask token shuffle 只造成小幅性能下降，说明模型对 support/reference 内部 token 顺序扰动相对鲁棒。
3. Full-image token shuffle 显著破坏性能，说明模型仍依赖全局视觉结构。
4. Query-side object visual embeddings 对定位预测具有强 causal 影响；query token padding 使预测区域有扩大趋势，token replacement 会导致性能崩塌。
5. Zero-shot Rex-Omni 不可靠地执行 instance/configuration-level matching，更像 category/container-level visual-prompt detection。

### 不应声称的结论
1. 不能声称“模型越关注内部 token 排列顺序会更好”。
2. 不能声称 E-001 已证明原论文 Mechanisms 的内部机制在 Qwen2.5-VL/Rex-Omni 上完全成立。
3. 不能把 R-004 原始 support prompt 扩展当作 query-container causal evidence。
4. 不能把 R-006 当作纯内部 order replacement 证据。
5. 不能把 R-005b 的失败解释为“模型一定忽略内部细节”；它首先是 zero-shot verifier/task-interface mismatch。

## 5. 为什么停止 R-007
曾计划构造 configuration-defined category synthetic probe：例如 A=[red,blue] 与 A†=[blue,red]。但该方向可能离真实 ICOL / POIL 任务较远，且“类别由内部部件顺序定义”的设定不一定合理。为避免继续在可解释性玩具任务上过拟合，当前决定停止 R-007，转向更贴近 ICOL 最新论文的 POIL 数据集与协议。

## 6. 对 E-002 的启发
E-001 的主要价值不是证明一个强机制命题，而是明确了下一步应转向更任务真实的 instance-level positive/negative protocol：

- 当前 Rex-Omni 更容易做 category/container-level matching；
- POIL 的 in-class negative query rejection 正好能检验“是否真的识别 reference instance”；
- Personalize / IPLoc-ID 论文提供了更合理的数据与评测协议：positive query + negative query，mIoU + F1；
- E-002 应避免继续只看 localization mIoU，而要同时衡量 false positive suppression / instance identification。
