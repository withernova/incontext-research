# 网页对话模型审阅入口

本仓库是科研工作台的**工具源码**，不是某个研究项目的事实库。审阅时请先读：

1. `README.md`：用户流程与运行入口；
2. `DATA_CONTRACT.md`：canonical Markdown、运行时 JSON 与研究诚信边界；
3. `server.py`：Python stdlib HTTP/API、项目发现、持久化和执行配置；
4. `static/app.js`：浏览器端状态与交互；
5. `surveyctl.py`：terminal pi 对 Experiment/Run 的稳定写回桥；
6. `skills/research-survey/SKILL.md`：文献与 Claim 的反幻觉工作流；
7. `extensions/experiment-steward/index.ts`：单实验监控与受控多任务队列。

旧 `/watchdog` 与旧工具名仅是 deprecated aliases。审阅时以 Steward v2 配置、严格 completion AND 合同、人类确认 remediation、manifest_reference 归档和重启暂停语义为准。

Research Explorer 的网页入口只能生成/复制给 live terminal pi 的 `/explore start` 协调指令，不得把 HTTP 响应描述为已启动。审阅其产物时，final/Run 都只是 proposal/draft；Claim、正式 synthesis、审核授权和执行 gate 不变。

## 系统边界

- 研究事实的单一来源：项目的 `kernel/`、`shell/`、`state.md`。
- `.survey-tool/`：UI、兼容状态、缓存和执行元数据，不是事实真值。
- `.publish/`：供 GitHub/网页模型读取的生成快照，不是第二个可编辑项目。
- terminal pi 必须通过 `surveyctl.py` 更新 Experiment/Run，不能直接编辑 `.survey-tool/*.json`。
- steward queue 只能执行用户批准的任务，不得自行扩展队列或绕过正式 Run 授权。

## 建议审阅维度

请不要只做表面 UI review。按以下维度逐项给出：严重度、文件/函数证据、失败场景、最小修复和长期重构方案。

1. 数据一致性、事务性写入、并发修改和崩溃恢复；
2. canonical Markdown 与 JSON 双向同步是否可能产生双重真值；
3. API 路由、路径穿越、命令注入、SSH/GitHub token 与隐私风险；
4. Run ID、artifact directory、rekey 和历史迁移完整性；
5. Experiment 授权状态机是否存在越权、smoke-loop 或假完成路径；
6. steward queue 的依赖、重试、恢复、并发和验收证据是否可靠；
7. GPT prompt/import 是否可能越界写入、错误归属或污染相邻字段；
8. Markdown/LaTeX parser 的误修复、XSS 和渲染一致性；
9. 文献、引用、Claim promotion 与结果结论边界是否满足科研诚信；
10. 可测试性、模块化、可移植性、可观测性和升级迁移。

## 输出协议

建议输出以下结构，便于人工审阅后实施：

```markdown
## Executive summary
## P0 — data loss / authorization / security
### ISSUE-001
- evidence: `path:line` / function
- reproducible scenario:
- impact:
- minimal fix:
- architectural fix:
- tests:
## P1 — correctness
## P2 — maintainability / UX
## Proposed staged roadmap
## Questions requiring human decision
```

不要声称运行过未实际运行的测试。无法访问某个项目、SSH、Zotero、MinerU 或私有 snapshot 时，明确标记 `REPOSITORY_NOT_ACCESSIBLE` 或 `[UNVERIFIED]`。
