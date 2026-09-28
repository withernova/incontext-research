# iploc-szy

轻量 MMDetection/MMEngine 风格的 Qwen3-VL IPLoc SFT 框架。核心是 Config → Registry/Builder → Dataset/Collator → Model → Runner/Hooks → Evaluator。

```bash
pip install -e .
python tools/inspect_dataset.py configs/sft/qwen3vl_8b_lora_smoke.py
CUDA_VISIBLE_DEVICES=2,3 python tools/train.py configs/sft/qwen3vl_8b_lora_smoke.py
python tools/infer.py configs/sft/qwen3vl_8b_iploc.py --adapter work_dirs/qwen3vl_8b_iploc/adapter
```

正式 IPLoc 训练前复制 `configs/sft/qwen3vl_8b_iploc.py`，填写 manifest，冻结数据身份、seed、prompt 和指标。当前 batch size 固定为 1，可用梯度累积扩展；尚未加入 DeepSpeed/FSDP、resume 和正式 train/val split。

详见 `MODULE_MAP.md`。
