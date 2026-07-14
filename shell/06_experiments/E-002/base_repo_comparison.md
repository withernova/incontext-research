# E-002 · Base repo 选择比较：Rex-Omni vs IPLoc vs IPLoc-ID

> 目的：当前仍处于“发现现象/验证问题是否真实存在”的阶段，因此 base repo 应优先支持快速、可信地观察 POIL/POL 现象，而不是一开始就追求工程统一或机制干预。

## 1. 已检查仓库

### Rex-Omni
远程路径：

```text
/home/featurize/work/mechanism/Rex-Omni
```

E-001 已完成 vLLM-native token intervention 与 COCO visual-prompt 实验。优点是我们熟悉，且已有 token-level intervention hook。缺点是它不是 IPLoc/POIL 官方协议，zero-shot instance/configuration verification 已显示明显 task-interface mismatch。

### IPLoc 官方仓库
远程路径：

```text
/home/featurize/work/mechanism/IPLoc
```

主要文件：

```text
Loc_Qwen2VL7B.py
loc_dataset.py
utils_qwen.py
data/test_LASOT_{1,2,4,8}_shot.json
data/{1,2}_shots_pdm.json
data/{1,2,3,4}_shots_perseg.json
```

任务：POL / personalized localization。只有 positive query，不含 negative rejection。

### IPLoc-ID 官方仓库
远程路径：

```text
/home/featurize/work/mechanism/iplocid
```

主要文件：

```text
iplocid/code_inference.py
iplocid/loc_dataset.py
iplocid/vlm_build_messages.py
iplocid/vlm_loader.py
iplocid/vlm_external_query_set.py
iplocid/data/*T2*.json
```

任务：POIL / personalized object identification and localization。包含 positive query 与 negative query，支持 in-class/out-of-class negatives。

## 2. 论文层面对比

### IPLoc / teaching2024
目标：给 reference images + label + bbox，在 query image 中定位同一 object type/instance。

关键设定：
- 从 tracking datasets 构造同一 object 跨帧的 in-context localization conversations；
- 用 pseudo-name regularization 降低 category prior，迫使模型看 visual context；
- 主要指标是 mIoU；
- 额外提出 IoU-excluding 观察 copying from context；
- 不处理 negative query rejection。

适合回答：
- 模型是否能通过 in-context examples 做 personalized localization？
- fine-tuning / pseudo-name 是否让模型更依赖 reference context？
- 模型是否只是 copy reference bbox？

不适合直接回答：
- query 不含 reference instance 时，模型能否拒绝？
- in-class distractor 上 false positive 是否严重？

### IPLoc-ID / personal2026
目标：把 POL 扩展为 POIL。query 可以是 positive，也可以是 negative；模型需要定位同一 reference instance，或拒绝负例。

关键设定：
- 每个 sample 共享 reference，但含 positive query 和 negative query；
- negative 可以是 in-class 或 out-of-class；
- 评估 mIoU + F1；
- localization-only 方法在 balanced positive/negative 下若总是输出 bbox，F1 理论基线约 0.667；
- IPLoc-ID 通过 bbox candidate + self-posed query + Yes/No answer 做 identification。

适合回答：
- ICOL/POL 是否只是 localization-only positive generator？
- in-class negative 上是否有高 false positive？
- 加 identification objective/self-posed query 是否减少 false positives？

## 3. 代码层面对比

| 维度 | Rex-Omni | IPLoc | IPLoc-ID |
|---|---|---|---|
| 官方性 | Rex-Omni 官方路径，但非 POIL/POL 官方协议 | IPLoc 论文官方 | IPLoc-ID 论文官方 |
| 任务 | visual prompt detection / open-vocab detection | POL positive-only | POIL positive + negative |
| 模型 | Rex-Omni/Qwen2.5-VL/vLLM | Qwen2-VL HF + LoRA | Qwen2/Qwen2.5/Qwen3/Gemma HF + LoRA |
| 数据 | COCO visual prompt / 自构造 | PDM/PerSeg/LaSOT positive-only | LaSOT/PDM/GOT/VastTrack positive+negative |
| 指标 | mIoU/recall/FP 等需自定义 | mIoU | mIoU + TP/TN/FP/FN，F1 可算 |
| 现象发现 | 对 containerization 已够用 | 适合 POL localization/copying | 最适合 POIL false-positive/rejection |
| 代码成熟度 | 我们已大量 patch | 很小、简单，但功能窄 | 更完整，但依赖更新、路径硬编码 |
| 风险 | task mismatch，zero-shot verifier 不稳定 | 没有 negative query | Qwen3/LoRA/数据路径依赖较重 |

## 4. IPLoc 官方仓库检查摘要

`IPLoc` 仓库非常小，核心就是 `Loc_Qwen2VL7B.py`：

- 固定加载 `Qwen/Qwen2-VL-7B-Instruct`；
- 可加载 LoRA：`--lora_weights_path`；
- 输入 JSON 没有 `role` 字段，默认前 n-1 张是 reference，最后一张是 query；
- 输出只计算 localization mIoU；
- 没有 negative query、没有 F1、没有 rejection interpreter。

示例数据：

```text
data/test_LASOT_1_shot.json len=144
role: implicit, [reference, positive query]

data/1_shots_pdm.json len=976
role: implicit, [reference, positive query]

data/1_shots_perseg.json len=40
role: implicit, [reference, positive query]
```

这说明 IPLoc repo 适合作为 POL localization baseline，但如果我们要发现“模型是否只是同类 object false-positive”，需要自己扩展 negative query。

## 5. IPLoc-ID 官方仓库检查摘要

`iplocid` 仓库更适合 E-002：

- 已有 `role` 字段；
- `inclass-image` / `outclass-image` 与 `positive-image` 同时存在；
- `code_inference.py` 已有 PN interpreter 与 TP/TN/FP/FN；
- `vlm_loader.py` 支持 Qwen2/Qwen2.5/Qwen3/Gemma；
- 直接对应 personal2026 的 POIL 问题定义。

主要坑：

- README 提到 `evaluation.sh`，但当前仓库没有；
- build 脚本引用缺失的 `tool_inspect_dataset_json.py`；
- 默认路径硬编码 `/ssd1/dataset/ICL_tracking(_minimized)`；
- `inference.sh` 默认双 GPU 并发；
- `external_query` 只是 system instruction，不等价于官方 IPLoc-ID 的 learned autoregressive self-posed query。

## 6. 推荐 base repo 策略

### 结论
如果目标是“发现现象”，建议主 base 用：

```text
/home/featurize/work/mechanism/iplocid
```

而不是 Rex-Omni 或原 IPLoc。

理由：

1. 我们现在真正需要观察的现象是 instance-level positive/negative discrimination，尤其 in-class negative false positives；
2. IPLoc-ID 已经把该现象形式化为 POIL，并提供 manifest、roles、metrics 与 interpreter；
3. 原 IPLoc 只能测 positive localization，不能直接测 rejection；
4. Rex-Omni 虽有我们已有干预 hook，但和 POIL 官方协议不一致，容易再次陷入 task-interface mismatch；
5. 处于现象发现阶段，应优先使用最贴近问题定义的数据与评估协议。

### 推荐执行顺序

#### Phase A：用 IPLoc-ID repo 复现/验证现象
1. 数据到位后，先检查官方 manifest 图像路径 missing 数；
2. 跑 official IPLoc-ID / IPLoc minimal model 的 2-sample smoke；
3. 跑小规模 LaSOT in-class negative：比较 `iploc` vs `iplocid`；
4. 报 mIoU、TP/TN/FP/FN、F1、negative false-positive rate。

#### Phase B：把 IPLoc 原仓库作为 sanity baseline
1. 跑原 IPLoc positive-only JSON，确认 POL localization mIoU；
2. 用它辅助理解 personal2026 中 “IPLoc has no rejection mechanism” 的 baseline；
3. 不建议作为 E-002 主工程 base。

#### Phase C：再把 Rex-Omni 接入 POIL manifest
1. 把 IPLoc-ID manifest 转成 Rex-Omni visual prompt input；
2. 测 Rex-Omni localization-only 在 in-class negative 上的 false positives；
3. 如果现象明确，再考虑用 Rex-Omni/vLLM hook 做机制干预。

## 7. 当前阶段不建议做什么

- 不建议马上在 Rex-Omni 上继续写复杂 POIL adapter；
- 不建议马上训练 LoRA；
- 不建议继续 synthetic A/A† configuration probe；
- 不建议把 `--external_query` 的 prompt-only 结果当作 IPLoc-ID 官方方法。

## 8. 一句话建议

当前应该以 `iplocid` 作为 E-002 主 base，因为它最直接服务于“发现 ICOL/POL 是否存在 instance-level false-positive/rejection 问题”这个阶段目标；`IPLoc` 作为 positive-only baseline 与历史对照；`Rex-Omni` 暂时作为后续迁移/机制分析对象，而不是第一阶段 base。
