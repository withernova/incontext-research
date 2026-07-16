# state.md

state: E002_PLANNING
iteration: 1
budget:
  max_iterations: 3
  max_wall_seconds: 600
blockers:
  - E-002 需要确认 `iplocid` 官方仓库、数据构造脚本与最小模型是否可访问。
next_actions:
  - 阅读并核验 `personal2026` 的官方代码/数据链接。
  - 参考 `shell/06_experiments/E-002/base_repo_comparison.md` 选择 E-002 主 base repo。
  - 创建 E-002 远程目录：`/home/featurize/work/mechanism/explog/E-002` 与 `/home/featurize/work/mechanism/Rex-Omni/tmp/e002`。
  - 先做 R-001 POIL dataset acquisition / format inspection，不立即训练或跑大规模推理。
  - 基于 POIL manifest 再运行 R-002 localization-only baseline 与 R-003 prompt-only self-posed identification baseline。
last_updated: 2026-07-16T15:00:00+08:00

## 阶段历史（append-only）
- 2026-07-09T15:31:09 | AWAIT_INTAKE | 创建项目骨架
- 2026-07-09T15:31:09 | MATERIALIZE | INTAKE 解析 -> context/idea/AGENTS 已写入
- 2026-07-13T00:00:00 | E001_SUMMARY | E-001 containerization 阶段性收束，写入 `shell/06_experiments/E-001/final_summary.md`
- 2026-07-13T00:00:00 | E002_PLANNING | 新建 E-002：使用 Personalize / POIL 数据集与协议
## 2026-07-13 E-002 mechanism clarification
- User clarified: E-002 aims to test whether IPLoc/MLLM bottleneck is insufficient use of object-internal visual-token detail/order, not merely POIL rejection.
- Patch-level perturbation is only a proxy; token-level visual-embedding intervention is the mechanism-critical experiment and must be distinguished.
- Added plan: `shell/06_experiments/E-002/internal_token_mechanism_plan.md`.
- Hard samples should be mined using model visual-layer object-token similarity: same category, similar silhouette, high unordered internal-token similarity, but different identity/order-aware structure.
- 2026-07-13 | E002_MECHANISM_PROTOCOL | Read Mechanisms of Object Localization paper. Token interventions should follow: mask-to-token-grid by any overlap, LLM-input intervention after multimodal projection, global-average embedding ablation, object-token shuffle vs full shuffle, copy-padding/container extension, and global/local view separation when applicable.
- 2026-07-16 | E003_CREATED | 将 Joint F1@IoU 与 forced-candidate verifier 从 E-002 独立为 E-003。E-002 保留 hidden-token/container mechanism；E-003 检验 identification-only F1 是否与 localization correctness 解耦并高估 joint task success。
- 2026-07-16 | E003_R001 | 重建本地 LaSOT POIL manifest：140 samples / 70 classes / 140 positive + 140 same-class negative，missing=0、invalid bbox=0；非官方 split。
- 2026-07-16 | E003_R002_FAILED | 首次 Joint F1 n140 因 Torch/Transformers 不兼容导致所有 processor 调用失败，零有效记录；run 保留为 failed audit，不得引用。
- 2026-07-16 | ARCHIVE_RECENT_RUNS | 按 ledger_filling_skill 审计归档 E-002 R-010–R-015（含 R-014b/R-014c）与 E-003 R-001–R-004b；明确记录 failed/aborted/smoke/main 状态、exact remote paths、R-014c geometry caveat 与 E003 Joint F1 结论边界。
