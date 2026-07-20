# E004-R-000-qwen3vl-head-hook-audit

- 状态：completed
- 性质：implementation/module audit；无科学行为指标。
- 远端目录：`/home/featurize/work/mechanism/explog/E-004/runs/E004-R-000-qwen3vl-head-hook-audit/`
- Qwen3-VL text decoder：36 layers、32 query heads、8 KV heads、head_dim=128、hidden=4096。
- hook candidate：`model.language_model.layers.{L}.self_attn.o_proj` forward pre-hook；o_proj 输入的4096维可按32个128维 query-head slices干预。
- 必要性：head output 在 o_proj 前仍可分离；o_proj 后已经混合，不能直接声称某 slice 对应单 head。
- 下一 gate：no-op equality、all-head-zero equivalence、single-head deterministic repeat。
- 审核：`config/run.md`、`analysis/module_audit.json`。
