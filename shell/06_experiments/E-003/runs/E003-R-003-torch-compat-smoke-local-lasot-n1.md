# E003-R-003-torch-compat-smoke-local-lasot-n1

- 状态：completed / passed
- 性质：environment compatibility smoke；不得作为科学结论。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-003-torch-compat-smoke-local-lasot-n1/`
- 必要性：E003-R-002 因缺失 `torch.compiler.is_compiling` 得到零记录。
- 数据：本地 deterministic LaSOT manifest 前1 sample；1 positive + 1 same-class negative。
- 模型：Qwen3-VL-8B-Instruct + IPLoc-ID 1-shot LoRA；本地 HF snapshot。
- 兼容改动：缺失时注入 `torch.compiler.is_compiling=lambda:False`；`VLM_LOCAL_MODEL_PATH` 只覆盖加载路径并保持 canonical family dispatch。
- 结果：2 records；TP=1、TN=1；smoke status=passed。positive 个例 IoU=0.0798，仅为链路案例。
- 支持：processor、GPU generation、LoRA、Yes/No、bbox 与 IoU 解析链路可运行。
- 审核：`config/run.md`、`logs/run.log`、`analysis/smoke_summary.json`、generated texts、metrics。
