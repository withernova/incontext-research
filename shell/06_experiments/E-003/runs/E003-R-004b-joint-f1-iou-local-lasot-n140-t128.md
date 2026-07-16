# E003-R-004b-joint-f1-iou-local-lasot-n140-t128

- 状态：completed
- 性质：main evaluation diagnostic；无 token intervention。
- 远端目录：`/home/featurize/work/mechanism/explog/E-003/runs/E003-R-004b-joint-f1-iou-local-lasot-n140-t128/`
- 目的：审计 identification-only F1 与 joint identification-localization correctness 的耦合。
- 数据：本地 deterministic LaSOT POIL manifest；140 samples/70 classes；140 positive + 140 same-class negative；非官方 IPLoc-ID split。
- 模型/环境：Qwen3-VL-8B-Instruct + IPLoc-ID LoRA；max_side=640；max_new_tokens=128；torch 2.2.2、transformers 4.57.3、peft 0.18.0；本地 snapshot；同 R-003 最小兼容补丁。
- 完整性：280 records=140 positive+140 negative；无 processor failure/traceback。
- Identification：TP=133、TN=136、FP=4、FN=7、F1=0.9603；negative FPR=2.86%。
- Joint@0.3：TP=97、FP=4、FN=43、F1=0.8050、positive joint recall=.6929。
- Joint@0.5：TP=89、FP=4、FN=51、F1=0.7639、positive joint recall=.6357。
- Joint@0.7：TP=76、FP=4、FN=64、F1=0.6909、positive joint recall=.5429。
- Positive IoU：mean=.5745、median=.7414；identification TP mean=.5880/median=.7441；Yes-positive bins：<.1=35、.1-.3=1、.3-.5=8、.5-.7=13、≥.7=76。
- 支持：identification-only F1 不等于 joint task success，并在此 split 上高估 joint correctness。
- 不支持：不能外推论文官方 split；不能单独证明 background/category/container shortcut 或 verifier 完全忽略候选框。
- 审核：`config/run.md`、`logs/run.log`、`analysis/joint_f1_iou.{json,md}`、generated texts、metrics。
