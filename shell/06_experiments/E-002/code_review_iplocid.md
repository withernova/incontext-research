# E-002 · IPLoc-ID 官方代码初步检查记录

> 检查对象：远程 `/home/featurize/work/mechanism/iplocid`  
> 检查时间：2026-07-13  
> 目的：在用户下载/准备数据集前，确认官方代码结构、数据格式、推理入口、评估输出与潜在坑点。

## 1. 仓库结构

远程已存在：

```text
/home/featurize/work/mechanism/iplocid
```

主要文件：

```text
README.md
iplocid/code_inference.py
iplocid/code_results_summary.py
iplocid/code_results_visualization.py
iplocid/data/*.json
iplocid/extract_dataset.sh
iplocid/inference.sh
iplocid/loc_dataset.py
iplocid/shell_build_data-json.sh
iplocid/shell_build_dataset_LASOT.sh
iplocid/shell_build_dataset_VastTrack.sh
iplocid/shell_build_dataset_got10k.sh
iplocid/shell_build_dataset_pdm.sh
iplocid/tool_build_dataset_json_*.py
iplocid/tool_extract_dataset_from_json.py
iplocid/vlm_build_messages.py
iplocid/vlm_coord_utils.py
iplocid/vlm_external_query_set.py
iplocid/vlm_loader.py
```

当前 git 状态：`main...origin/main`，最近提交包括 README 更新。

## 2. README 给出的数据路径假设

README 默认要求原始数据放在：

```text
/ssd1/dataset/ICL_tracking/video
├── LASOT/<class>/<subclass>
├── burst/annotations + burst/frames
├── got10k/val/<class>
└── VastTrack/<class>/<subclass>
```

并导出最小图像集合到：

```text
/ssd1/dataset/ICL_tracking_minimized
```

注意：这些路径在脚本里硬编码较多。若用户把数据下载到其他路径，需要：

1. 建 symlink 到 `/ssd1/dataset/ICL_tracking`；或
2. 修改各 build/extract 脚本中的 root；或
3. 用已有 JSON 后处理替换路径。

## 3. 官方 JSON 数据格式

官方已附带 `iplocid/data/*.json`。它们是 manifest，而不是图像本体。

示例：`LASOT_1shot_T2_classwise-split_test.json` 第一条：

```json
{
  "element": "airplane",
  "image_path": [
    "/ssd1/dataset/ICL_tracking_minimized/video/LASOT/airplane/airplane-20/img/00000001.jpg",
    "/ssd1/dataset/ICL_tracking_minimized/video/LASOT/airplane/airplane-3/img/00001476.jpg",
    "/ssd1/dataset/ICL_tracking_minimized/video/LASOT/airplane/airplane-20/img/00005951.jpg"
  ],
  "bbox": [
    "[261, 345, 604, 512]",
    "[515, 208, 912, 387]",
    "[576, 494, 729, 600]"
  ],
  "image_id": [0, 1, 2],
  "role": ["reference", "inclass-image", "positive-image"]
}
```

语义：

- `reference`：support/reference frame；
- `positive-image`：同一 instance 的 positive query；
- `inclass-image`：同类不同 instance 的 negative query；
- `outclass-image`：不同类别 negative query。

数据规模与论文一致：

| JSON | len | negative type |
|---|---:|---|
| `LASOT_1shot_T2_classwise-split_test.json` | 140 | in-class |
| `VastTrack_test_1shot_T2.json` | 391 | in-class |
| `pdm_1shot_T2.json` | 745 | out-of-class |
| `got10k-val_1shot_T2.json` | 180 | out-of-class |

## 4. 推理入口

README 推荐：

```bash
cd /home/featurize/work/mechanism/iplocid/iplocid
bash inference.sh
```

`inference.sh` 默认：

```bash
data_path=./data/LASOT_1shot_T2_classwise-split_test.json

CUDA_VISIBLE_DEVICES=0 python code_inference.py \
  --data_path $data_path \
  --model_id Qwen/Qwen3-VL-8B-Instruct \
  --name Qwen3-VL-8B-iplocid \
  --lora_weights_path ../pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid &

CUDA_VISIBLE_DEVICES=1 python code_inference.py \
  --data_path $data_path \
  --model_id Qwen/Qwen3-VL-8B-Instruct \
  --name Qwen3-VL-8B-iploc \
  --lora_weights_path ../pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iploc &
```

注意：这默认同时占两张 GPU；我们远程当前常见配置是单 3090，因此不能直接跑原 `inference.sh`，需要改成单进程、小样本、单模型。

建议 E-002 首次 smoke：

```bash
cd /home/featurize/work/mechanism/iplocid/iplocid
PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES=0 python code_inference.py \
  --data_path ./data/LASOT_1shot_T2_classwise-split_test.json \
  --model_id Qwen/Qwen3-VL-8B-Instruct \
  --name smoke_Qwen3VL8B_iplocid \
  --lora_weights_path ../pretrained_weights/Qwen3-VL-8B-Instruct_1shot_iplocid \
  --num_samples 2 \
  --max_side 640 \
  --overwrite
```

前提：数据图像和 LoRA 权重都已就位。

## 5. 模型加载

`vlm_loader.py` 支持：

- Qwen2-VL
- Qwen2.5-VL
- Qwen3-VL
- Gemma3
- Qwen Omni variants
- LLaVA HF variants

Qwen3-VL 使用：

```python
AutoProcessor.from_pretrained(model_name)
Qwen3VLForConditionalGeneration.from_pretrained(..., dtype=torch.bfloat16, device_map="auto")
```

LoRA 加载在 `code_inference.py`：

```python
model = PeftModel.from_pretrained(model, args.lora_weights_path)
```

## 6. Prompt / message 构造

`vlm_build_messages.py` 构造 IPLoc-style prompt：

1. 第一个 reference image + `<ref>{element}</ref>`；
2. reference bbox 文本；
3. 下一个 reference 或 target image + `<ref>{element}</ref>`；
4. 让模型生成目标 bbox / bbox+answer。

bbox 会被归一化到 Qwen 风格 `[x1,y1,x2,y2]`，坐标范围 0-1000。

## 7. 输出与评估

`code_inference.py` 输出：

```text
./results/<data_name>/metrics/<safe_label>.json
./results/<data_name>/generated_texts/<safe_label>.json
```

metrics 里有：

```json
{
  "mIoU": "mean IoU over TP positives only",
  "mIoU_full_for_all_targets": "all positive targets, missing/invalid bbox counted as 0",
  "TP": 0,
  "TN": 0,
  "FP": 0,
  "FN": 0
}
```

重要：代码没有直接写 F1，需要我们自己由 TP/FP/FN 算：

```text
precision = TP / (TP + FP)
recall    = TP / (TP + FN)
F1        = 2TP / (2TP + FP + FN)
```

## 8. Positive/negative 解释器

`PN_interpreter(gen)` 规则：

1. 输出含 `yes` → positive；
2. 输出含 `no` → negative；
3. 命中 `different/not found/not present/no match` → negative；
4. 能抽出非零 bbox → 默认 positive；
5. 否则 negative。

因此 localization-only 模型只要输出 bbox，negative query 上就会计为 FP。这与论文中“localization-only all-positive F1 ≈ 0.667”的逻辑一致。

## 9. 已发现的代码/文档坑点

### 9.1 README 提到 evaluation.sh，但仓库中没看到
README 写：

```bash
bash iplocid/evaluation.sh
```

但当前文件列表没有 `evaluation.sh`。实际 summary 入口是：

```bash
python3 code_results_summary.py ./results/<dataset_name> --no-plot
```

### 9.2 build 脚本引用缺失文件 `tool_inspect_dataset_json.py`
`shell_build_dataset_LASOT.sh` 中引用：

```bash
python3 tool_inspect_dataset_json.py --json_path ...
```

但当前仓库没有该文件。若从 scratch build LASOT JSON，主 JSON 生成可能已经完成，但最后 inspect 步骤会失败。解决方案：

- 临时注释 inspect 调用；或
- 自己补一个简易 `tool_inspect_dataset_json.py`；或
- 直接使用官方已给的 `data/*.json`，只用 `extract_dataset.sh` 抽图。

### 9.3 路径硬编码为 `/ssd1/dataset/...`
所有官方 JSON 与脚本默认 `/ssd1/dataset/ICL_tracking_minimized`。若数据不在该路径，需要 symlink 或重写 JSON 路径。

### 9.4 `inference.sh` 默认双 GPU 并发
会同时跑 IPLoc-ID 与 reproduced IPLoc。单卡 3090 上不要直接跑。

### 9.5 `external_query` 不是严格 IPLoc-ID 自回归 self-posed query
`--external_query` 是把 instruction 注入 system message，而论文 IPLoc-ID 是模型先生成 bbox，再生成 fixed self-posed query，再生成 answer。两者不是完全等价。E-002 R-003 若做 prompt-only baseline，应标注为“zero-shot prompt diagnostic”，不能当作官方 IPLoc-ID。

### 9.6 Qwen3-VL-8B 依赖较新 transformers
README 要求从 GitHub 安装最新版 transformers。远程现有 Rex-Omni 环境未必兼容，需要单独检查 `iplocid` 环境，避免污染 Rex-Omni/vLLM 环境。

## 10. 对用户下载数据的建议

如果目标是最快跑通官方 JSON：

1. 下载数据后尽量放成或 symlink 成：
   ```text
   /ssd1/dataset/ICL_tracking/video/...
   ```
2. 然后运行：
   ```bash
   cd /home/featurize/work/mechanism/iplocid/iplocid
   bash extract_dataset.sh
   ```
   它会读取 `./data/*.json`，从 full dataset 抽取官方 manifest 需要的最小图像集合到：
   ```text
   /ssd1/dataset/ICL_tracking_minimized
   ```
3. 如果 `/ssd1` 不方便，建议建 symlink，而不是大改所有 JSON：
   ```bash
   sudo mkdir -p /ssd1/dataset  # 如无 sudo 则换用户可写路径并后处理 JSON
   ln -s <真实数据根>/ICL_tracking /ssd1/dataset/ICL_tracking
   ```

## 11. E-002 下一步建议

### 先做数据检查，不跑模型
等用户数据下载完成后，先检查：

```bash
cd /home/featurize/work/mechanism/iplocid/iplocid
python - <<'PY'
import json, os
fn='data/LASOT_1shot_T2_classwise-split_test.json'
data=json.load(open(fn))
missing=0
for s in data:
    for p in s['image_path']:
        missing += int(not os.path.exists(p))
print(fn, 'samples', len(data), 'missing_images', missing)
print(data[0])
PY
```

### 然后跑 2-sample smoke
只跑一个模型、一个 JSON、2 个 sample，确认：

- 模型能加载；
- processor 能处理多图 prompt；
- 输出 JSON 结构正常；
- TP/TN/FP/FN 能计算；
- 可视化脚本能跑。

