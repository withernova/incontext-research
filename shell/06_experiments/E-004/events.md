
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

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E004-R-000-qwen3vl-head-hook-audit
- message: Run registry 已从 R-012 迁移为 canonical ID E004-R-000-qwen3vl-head-hook-audit

legacy_registry_id=R-012

## 2026-07-20T17:35:56+08:00 · run_rekey
- run: E004-R-001-synthetic-double-instance-behavior-n4
- message: Run registry 已从 R-013 迁移为 canonical ID E004-R-001-synthetic-double-instance-behavior-n4

legacy_registry_id=R-013

## 2026-07-20T22:30:50+08:00 · run_created
- run: E004-R-006-qwen3vl-head-hook-correctness-smoke
- message: Agent 创建 canonical Run E004-R-006-qwen3vl-head-hook-correctness-smoke · E004-R-006-qwen3vl-head-hook-correctness-smoke

## 2026-07-20T22:30:50+08:00 · run_created
- run: E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4
- message: Agent 创建 canonical Run E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4 · E004-R-007-qwen3vl-layer-output-ablation-synthetic-n4

## 2026-07-20T22:30:50+08:00 · run_created
- run: E004-R-008-source-base-object-removal-proxy-gate-n4
- message: Agent 创建 canonical Run E004-R-008-source-base-object-removal-proxy-gate-n4 · E004-R-008-source-base-object-removal-proxy-gate-n4

## 2026-07-20T22:30:51+08:00 · run_created
- run: E004-R-009-layer-cma-recoverability-proxy-strict-n6
- message: Agent 创建 canonical Run E004-R-009-layer-cma-recoverability-proxy-strict-n6 · E004-R-009-layer-cma-recoverability-proxy-strict-n6

## 2026-07-20T22:30:51+08:00 · run_created
- run: E004-R-010-single-head-activation-patching-correctness-smoke
- message: Agent 创建 canonical Run E004-R-010-single-head-activation-patching-correctness-smoke · E004-R-010-single-head-activation-patching-correctness-smoke

## 2026-07-20T22:30:51+08:00 · run_created
- run: E004-R-011-official-lama-code-acquisition
- message: Agent 创建 canonical Run E004-R-011-official-lama-code-acquisition · E004-R-011-official-lama-code-acquisition
