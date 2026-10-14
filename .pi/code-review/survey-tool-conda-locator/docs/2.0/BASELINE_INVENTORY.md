# Survey Tool 2.0 基线盘点

> 状态：Phase 0 基线
> 日期：2026-08-15
> Git 分支：`rebuild/survey-tool-2.0`
> 基线提交：`2bf46ba feat: redesign runs around the research lifecycle`

## 1. 备份与工作区

代码仓库已在创建 2.0 分支前完整归档：

- 归档：`/home/zhengyuesong/Tools/backups/survey-tool-before-2.0-20260815-152341.tar.gz`
- SHA-256：`02ae0926c02fd957f66ff8011a09969d8e6d0d3da6b78ba723dec5b21c3f599f`
- 校验文件：同路径追加 `.sha256`

创建 2.0 分支时存在一处用户本地修改：

- `start.sh`：浏览器启动失败时降级为打印访问地址。

该修改不是本轮产生，Phase 0 不覆盖、不还原，也不纳入 2.0 基线提交。

原分支 `rebuild/simple-gpt-pipeline` 相对远端 ahead 11；2.0 分支由当前本地 HEAD 创建，因此包含这 11 个本地提交。

## 2. 当前规模

| 文件 | 行数 | 字节数 | 观察 |
|---|---:|---:|---|
| `server.py` | 4,453 | 317,282 | HTTP、领域逻辑、存储和集成高度集中 |
| `static/app.js` | 2,112 | 266,008 | 单文件 SPA，功能耦合明显 |
| `static/style.css` | 349 | 43,108 | 全局样式文件 |
| `surveyctl.py` | 208 | 25,010 | Agent 与终端的稳定桥接入口 |

`server.py` AST 中约有 292 个函数和 3 个类。当前规模已经超过继续在单文件中安全扩展 2.0 功能的合理边界。

## 3. 当前架构

```text
Browser / static app
        ↓ JSON API
server.py
  ├─ 项目发现和配置
  ├─ Markdown / JSON 持久化
  ├─ Paper / Seven-Q / Claim / Idea
  ├─ Question / Comparison / Finding
  ├─ Experiment / Run
  ├─ Execution Outbox / Governance
  ├─ Research Explorer
  ├─ Zotero / Web Search / MinerU
  ├─ pi session binding
  └─ GitHub / Obsidian integration
        ↕
surveyctl.py
        ↕
pi skills / Herdr / Experiment Steward
```

已经开始拆出的纯领域模块：

- `survey_tool/execution/contracts.py`
- `survey_tool/execution/reconciliation.py`
- `survey_tool/execution/route_health.py`
- `survey_tool/run_lifecycle/contracts.py`
- `survey_tool/run_lifecycle/architecture.py`

这说明渐进拆分是可行的，不需要立即进行高风险的全量重写。

## 4. 当前数据边界

### 4.1 Canonical 研究内容

主要位于研究项目目录：

- `kernel/`
- `shell/`
- `state.md`
- `INTAKE.md`
- `AGENTS.md`

优点：

- 人类可读；
- pi 可直接读取；
- 易于 Git、Obsidian 和文件级审计；
- 与 `research-survey` 的反幻觉流程一致。

风险：

- Markdown 并不适合承载复杂并发状态机；
- 多对象关系和全局查询成本高；
- 任意文本编辑与结构化字段之间可能产生漂移。

### 4.2 工具运行状态

主要位于 `.survey-tool/*.json` 和 `.pi/*.json`：

- Experiment / Run registry；
- execution outbox；
- governance tasks；
- agent routing；
- pi binding；
- research exploration registry；
- steward / explorer scheduler state。

现有实现已经具备项目级锁、临时文件、`fsync + os.replace` 和损坏隔离，是 2.0 迁移时应保留的可靠性基线。

## 5. 已有功能资产

### 5.1 论文与研究

- Zotero collection 浏览与同步；
- Web 论文搜索和导入；
- PDF / MinerU 产物定位与解析任务；
- 七问和图片标注；
- Claim / Idea；
- Comparison / Finding；
- Question；
- Obsidian MOC；
- GPT 指令生成、响应解析和预览导入。

### 5.2 实验治理

- Experiment / Run registry；
- Run group 与指标定义；
- Workspace environment policy；
- Run 人工审核和独立执行授权；
- 自动评分和受控预授权；
- Execution Outbox、lease、防重复执行；
- Run 科研生命周期 v2；
- Agent routing 与 route health；
- Governance microtask；
- Experiment Steward v2。

### 5.3 Agent 集成

- pi live / persisted session binding；
- 项目级 session 恢复；
- `surveyctl.py` 稳定写回桥；
- Research Explorer extension / skill；
- Experiment Steward extension。

2.0 应复用这些治理合同，不应把已有的授权、lease、完整性和反幻觉门禁退化为简单 UI 状态。

## 6. 测试基线

Phase 0 执行结果：

- Python：61 tests，全部通过；
- JavaScript：5 个测试文件，全部通过。

执行命令：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
for f in tests/test_*.js; do node "$f"; done
```

现有测试重点覆盖：

- Execution Outbox；
- reconciliation；
- Experiment / Run 合同；
- pi binding；
- Research Explorer；
- Run lifecycle；
- Run organization；
- 前端 pipeline、steward 和导入逻辑。

明显缺口：

- Paper Candidate 生命周期；
- 下载与 MinerU 持久任务恢复；
- Seven-Q / Comparison / Question 的统一草稿审核；
- Herdr session binding；
- Automation 总状态机；
- 数据 migration dry-run；
- 浏览器级端到端测试。

## 7. 主要技术风险

### R1：后端单体继续膨胀

`server.py` 同时承担 API、领域、存储和外部集成。2.0 若直接追加功能，会使状态机、权限和异常处理更难验证。

**处理**：保留旧 API wrapper，按垂直切片把纯合同、repository 和 service 迁到包内。

### R2：前端单文件难以支持新信息架构

`static/app.js` 已超过 2,000 行，2.0 需要 Inbox、对象中心、异步任务和多阶段编辑。

**处理**：新 UI 使用 TypeScript 组件化应用；旧 UI 在迁移阶段保持可用。

### R3：Markdown 与复杂状态的职责混淆

科研正文适合 Markdown，队列、lease、关系和任务不适合。

**处理**：明确“科研正文 canonical”和“运行状态 canonical”是两个不同真相域，禁止同一字段双主写。

### R4：长任务只依赖进程内状态

MinerU 当前有进程内 job 状态；服务重启后可观察性和恢复能力不足。

**处理**：引入持久 Job registry，所有下载、解析、Herdr 和自动化任务使用统一状态合同。

### R5：自动化扩大权限

调研、代码修改和远程执行的风险等级不同。

**处理**：Automation 分阶段授权；调研完成不自动等价于执行许可；复用 Run 审核、Workspace gate 和 Outbox。

### R6：旧数据迁移误判

旧项目格式跨度大，部分 registry 和 Markdown 互为兼容层。

**处理**：迁移先 inventory 和 dry-run；不确定映射进入人工队列；原数据只读保留。

## 8. Phase 0 结论

1. 当前代码具有良好的实验治理资产和测试基线，可以渐进演进。
2. `server.py` 与 `static/app.js` 不适合继续作为 2.0 的唯一扩展点。
3. 2.0 应保留 Markdown 研究工件，同时为运行状态引入更适合关系、任务和事务的存储。
4. 第一项实现工作应是应用壳、版本化 API、统一 ID / relation / event / job 基础，而不是直接开发自动化。
5. 每个垂直切片迁移后都必须继续运行现有 61 + 5 测试，防止已有治理能力回退。
