# E003-R-002-joint-f1-n140-failed-env

- remote_dir: `/home/featurize/work/mechanism/explog/E-003/runs/E003-R-002-joint-f1-n140-failed-env/`
- legacy_mapping: `/home/featurize/work/mechanism/explog/E-002/runs/R-017-qwen3vl-joint-f1-iou-local-lasot-n140/`
- 性质：failed main diagnostic attempt / environment audit。
- 状态：failed。
- 错误：`module 'torch.compiler' has no attribute 'is_compiling'`。
- 影响：processor 对所有 target 失败并被脚本跳过，零有效 prediction；随后 post-analysis `ZeroDivisionError`。
- 结论：不得引用该 run 的 metrics、outputs 或科学结果。
