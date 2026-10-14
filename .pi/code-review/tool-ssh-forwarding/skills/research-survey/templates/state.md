# state.md

state: BOOTSTRAP
iteration: 0
budget:
  max_iterations: 3
  max_wall_seconds: 600
blockers: []
next_actions:
  - 摄取种子论文（scripts/papers/ingest.py；自动探测 MinerU .md，见 C2）
  - 运行 repo_map.py
  - 把想法分解为原子声明（DECOMPOSE）
last_updated: <写入时的 ISO 时间戳>

## 阶段历史（append-only）
- <iso> | BOOTSTRAP | 创建项目骨架