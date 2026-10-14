# ADR-0004：1.x 写入入口分阶段下线计划

- 状态：Proposed
- 日期：2026-08-16
- 决策范围：1.x 写 API（`/api/p/<proj>/...` 的 POST/PUT）与 `surveyctl.py` 写回桥

## 背景

2.0 已建立独立 SQLite 运行状态库与 React 工作区。当前状态：

- 2.0 读取路径仍以只读方式复用 1.x canonical / registry；
- Identity Index（Question/Experiment）与 Content Index（paper/comparison/finding/claim）已写入 v2 SQLite，正文与 authority 未变；
- 1.x 写入口仍是创建/编辑论文、七问、comparison、finding、claim、experiment、run 的 authority；
- 一次性切走写入口有数据丢失与绕过治理的风险（claim 双门禁、Run review 与执行授权）。

## 决策

采用**分阶段、有验收门槛的下线**。只有上一阶段验收通过后才进入下一阶段；每一阶段可回退，不做破坏性删除。

```text
Phase 1  只读读穿 + 原生索引（当前已完成）
Phase 2  staged acquisition 验收（下一步）
Phase 3  v2 工作区改读 native 对象
Phase 4  低风险对象双写
Phase 5  冻结指定 1.x 写入口
Phase 6  全部写入切换 + 1.x 只读兜底
```

## 各阶段

### Phase 1 — 只读读穿 + 原生索引（已完成）

- 2.0 读 1.x canonical/registry；v2 SQLite 只存 identity 与关系。
- 不改任何 1.x 写入口。

### Phase 2 — staged acquisition 验收（下一步）

- 在**测试候选**上人工运行 staged Worker（PDF 下载 → MinerU）与 canonical ingest（`INGEST <citekey>`）。
- 验收标准：download 与 MinerU 均成功；ingest 写入 canonical PDF 与 `kernel/citations.md` 且带 SHA-256；已存在 canonical 文件/citekey 时拒绝覆盖；失败可回滚。

### Phase 3 — v2 工作区改读 native 对象

- Question / Comparison / Paper 工作区改为读 v2 native 对象（store 未初始化时回退 legacy 读穿）。
- 验收标准：计数与 legacy 读穿一致；关系可见；authority 不变；页面刷新可恢复。

### Phase 4 — 低风险对象双写

- 新增 v2 写路径与 1.x 写入口并行：paper candidate 登记、comparison/finding 结构索引、question reference 更新。
- 1.x 写入口仍保持 active；不做任何冻结。

### Phase 5 — 冻结指定 1.x 写入口

- 对 v2 等价能力已验证的写入口返回 409 或迁移提示（例如 comparison/finding 结构、论文 note）。
- 保留读路径；Experiment / Run 治理继续经 `surveyctl.py` 与 1.x 写入口。

### Phase 6 — 全部写入切换 + 1.x 只读兜底

- 所有写入路由到 v2；1.x 写端点返回迁移重定向。
- `surveyctl.py` 写回桥在 Run 治理迁移后被替代。
- 1.x 读端点保留到 1.x UI 下线。

## 守卫

- claim 门禁（`kernel/claims.md` + R2 + 人工 approved + content hash）永不被绕过；
- Experiment / Run review 与执行授权在迁移期间永不被绕过；
- 每次冻结可逆；不提供硬删除；
- migration_records 与 dry-run 始终可复核；
- 正文与 authority 在 Phase 1–3 保持 Markdown / kernel / legacy JSON 不变。
