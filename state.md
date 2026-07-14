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
last_updated: 2026-07-13T00:00:00+08:00

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
