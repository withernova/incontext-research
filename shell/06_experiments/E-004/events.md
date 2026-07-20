
## 2026-07-20T17:15:06+08:00 · experiment_created
- run: -
- message: Agent 创建实验初稿 E-004 · Reference-conditioned causal token routing

## 2026-07-20T17:16:20+08:00 · run_created
- run: R-012
- message: Agent 创建 R-012 · E004-R-000-qwen3vl-head-hook-audit

## 2026-07-20T17:16:20+08:00 · run_update
- run: R-012
- message: 同步Qwen3-VL head-hook模块审计。

## 2026-07-20T17:16:20+08:00 · run_created
- run: R-013
- message: Agent 创建 R-013 · E004-R-001-synthetic-double-instance-behavior-n4

## 2026-07-20T17:16:20+08:00 · run_update
- run: R-013
- message: 同步synthetic 2x2 sanity，并明确behavioral gate failed。

## 2026-07-20T17:17:34+08:00 · registry_sync
- run: -
- message: E-004 已创建并同步 module audit 与 synthetic behavioral gate。

工具自动ID映射：R-012→E004-R-000-qwen3vl-head-hook-audit；R-013→E004-R-001-synthetic-double-instance-behavior-n4。R-001状态为completed_gate_failed，不进入科学head scan。
