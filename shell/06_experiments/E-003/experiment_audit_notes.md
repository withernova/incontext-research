# E-003 · 项目特定实验登记与审核约束

> 跨项目通用约束见 `ledger_filling_skill.md`；本文件只记录 E-003 特定定义。任何 agent 在创建、更新、总结 E-003 run 前必须同时读取两者。

## 1. Canonical IDs 与根目录

```text
local notes:  shell/06_experiments/E-003/runs/<CANONICAL_RUN_ID>.md
remote root:  /home/featurize/work/mechanism/explog/E-003/runs/<CANONICAL_RUN_ID>/
```

Registry 主键、note 文件名、远端目录末级名称必须一致。历史自动 `R-xxx` 已通过 `surveyctl run rekey` 迁移；不得重新建立旁路 mapping。

Legacy remote mappings 仅有：

```text
E-002/R-016-data-rehydrate-joint-verifier
→ E003-R-001-data-rehydrate-local-lasot-n140

E-002/R-017-qwen3vl-joint-f1-iou-local-lasot-n140
→ E003-R-002-joint-f1-n140-failed-env
```

## 2. 数据身份标签（每条主结果必须重复）

Manifest：

```text
/home/featurize/data/e002_manifests/LASOT_local_1shot_T2_n140_v2.json
```

身份：

```text
local deterministic LaSOT POIL reconstruction
not the official IPLoc-ID split
```

构造：

```text
reference = target sequence first frame
positive  = same target sequence last frame
negative  = another same-class sequence middle frame
```

规模：140 samples / 70 classes / 140 positive / 140 same-class negative。

禁止把它简写成“官方 LaSOT test set”或“复现论文 Table 8”。

## 3. 模型与环境身份

主模型：

```text
Qwen/Qwen3-VL-8B-Instruct
LoRA=/home/featurize/work/mechanism/iplocid/pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid
```

主环境：torch 2.2.2+cu121、transformers 4.57.3、peft 0.18.0、accelerate 1.12.0。

兼容 shim：

```python
if not hasattr(torch.compiler, "is_compiling"):
    torch.compiler.is_compiling = lambda: False
```

该 shim 只修复版本API缺失，不改变模型、权重、prompt或指标。主 run 必须离线加载完整 snapshot，避免网络超时改变运行状态。

## 4. Identification decision 与 parser 约束

自然生成主评测应保留 raw generated text、parsed bbox、parsed Yes/No 和 parser rule。

不得：

- 把缺少 decision 的 truncated text 自动计成 No；
- 把歧义文本如 `1. Yes. 2. No.` 映射为任一标签；
- 在 forced-candidate probe 中使用 repository `PN_interpreter` 的 arbitrary-nonzero-bbox positive fallback；
- 把 processor skip 后的空列表汇总成零性能。

## 5. Joint F1 定义

Positive：

```text
Yes && IoU>=tau -> TP
No              -> FN
Yes && IoU<tau  -> FN
```

Negative：

```text
Yes -> FP
No  -> TN
```

阈值固定报告：`tau={0.3,0.5,0.7}`。同时报告 identification confusion matrix、positive Yes recall、negative FPR、positive IoU distribution。

禁止直接做：

```text
identification F1 - mIoU
```

并将其解释为错误比例。可以报告 `Identification F1 - Joint F1@tau`，但必须说明这是同一 records 上两个 F1 定义的 paired metric gap，并由 cluster bootstrap 给出区间。

## 6. 主 run 完整性 gates

### Joint main run

```text
records=280
positive=140
negative=140
processor failures=0
traceback=0
final decision present/valid for every record
```

### Forced-candidate n20（历史审计规范；后续主实验已废弃该设计）

```text
records=240
20 positive targets + 20 negative targets
6 modes per target
12 actual role/mode cells ×20
all required logits finite
traceback=0
formal analysis summary exists
```

Role-specific modes：

```text
positive-image: generated_candidate, annotated_target, shifted_annotated,
                background_matched_size, contracted_annotated_50pct,
                expanded_annotated_150pct

inclass-image: generated_candidate, annotated_distractor, shifted_annotated,
               background_matched_size, contracted_annotated_50pct,
               expanded_annotated_150pct
```

不得要求 positive 出现 `annotated_distractor`，也不得要求 negative 出现 `annotated_target`。

## 7. Forced candidate 定义

旧n20/R-010设计中的`generated/annotated/shifted/background/contracted/expanded`仅作为历史失败链审计保留。经用户与agent复核，`background_matched_size`已从所有后续主实验删除，不再注册、运行或解释。

后续正式candidate intervention只有真实双向四格中的`candidate A`与`candidate B`；它们必须对应同一query中由独立identity annotation确认的两个实例，并分别拥有真实reference A/B。candidate 与 verifier question 必须进入 assistant autoregressive history。主 decision 是 single-token `Yes` vs `No` next-token logit margin：

\[
M=\ell(Yes)-\ell(No).
\]

`yes_pair_probability` 只在两个选定 tokens 间归一化，不是 calibrated probability。每次运行必须现场记录 tokenizer IDs。

## 8. 结论强度分层

### 可由 Joint F1 支持

- identification-only F1 不等于 joint POIL success；
- 在当前本地 split 上，它高估同时 identification+localization 成功的比例。

### 需要 low-IoU audit 后支持

- 低-IoU TP 的主要几何/语义失败类型；
- 排除坐标、frame、annotation、bbox-format bug。

### 需要 forced candidate 后支持

- final verifier 对 candidate region 敏感或不敏感；
- 仍必须称为 prefix-conditioned verifier probe。

### E-003 不能单独支持

- background/category/color/container shortcut；
- verifier 完全忽略 candidate；
- hidden-token identity-detail mechanism；
- 官方论文所有 split 上具体数值均有相同 gap；
- 论文造假或 F1“虚假”。

## 9. 统计与可视化

Bootstrap 以 sample 为 cluster，positive+negative pairing 一起重采样；不能把280 records当独立样本。建议10,000 replicates并保存 seed、replicates摘要/hash。

低-IoU可视化必须包含 reference GT、query GT、prediction、原始文本/IoU sidebar；不得文字覆盖图像。自动 geometry tags 与人工 semantic labels 分开保存。

## 10. 每次同步工具时的 notes 最低内容

```text
canonical run ID
artifact_dir
run nature
manifest identity
model/checkpoint
record counts + integrity gate
metric formulas/version
observed results
supported / unsupported conclusions
known confounds
config/log/summary/outputs/visualizations paths
supersedes/superseded_by（若适用）
```
