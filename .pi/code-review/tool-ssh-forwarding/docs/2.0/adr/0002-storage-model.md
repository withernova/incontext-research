# ADR-0002：Markdown 研究工件 + SQLite 运行状态的混合存储

- 状态：Accepted
- 日期：2026-08-15
- 决策范围：Survey Tool 2.0 项目数据

## 背景

当前系统采用两层：

1. `kernel/`、`shell/`、`state.md` 等 Markdown 作为研究工件；
2. `.survey-tool/*.json` 与 `.pi/*.json` 保存 UI、registry、队列和 Agent 状态。

Markdown 对论文笔记、Question、Finding、Experiment 概览和结果解释非常合适，但以下 2.0 需求更适合事务型关系存储：

- 稳定对象 ID 和多对象关系；
- Inbox；
- Paper Candidate；
- 持久 Job；
- Agent / Herdr session binding；
- Automation 阶段、预算与子任务；
- append-only event；
- 并发更新与 revision；
- 可恢复 dispatch 和 lease。

继续为每项功能增加独立 JSON，会增加跨文件事务和关系查询复杂度。

## 决策

采用混合存储：

### A. Markdown 是研究正文的 canonical source

包括：

- 论文笔记与七问；
- Comparison 正文；
- Finding 正文与证据；
- Question 正文；
- Idea / Claim 的研究表述；
- Experiment 概览；
- Run 设计和结果分析的人类可读视图；
- Automation 过程与最终报告。

这些内容保持可由人、pi、Obsidian 和 Git 直接读取。

### B. SQLite 是工具运行状态的 canonical source

每个研究项目使用：

```text
.survey-tool/survey-tool-v2.sqlite3
```

保存：

- 对象身份、类型和生命周期状态；
- 对象关系；
- Paper Candidate 状态；
- Job 与进度；
- Inbox item；
- Agent / Herdr session binding；
- Automation 状态、预算、checkpoint 和子任务；
- 事件与审计 metadata；
- 需要事务一致性的 dispatch、lease 和 revision。

### C. 禁止双主写

每个字段必须在 schema 中声明唯一 authority：

- prose / evidence body → Markdown；
- lifecycle / relation / lease / progress → SQLite；
- SQLite 可以保存 Markdown 路径、hash、mtime 和索引摘要，但不是正文的第二份可编辑副本；
- Markdown 可以渲染状态摘要，但不能反向覆盖 SQLite 状态机，除非通过显式 import / migration。

## SQLite 运行要求

- 使用 Python 标准库 `sqlite3`；
- 开启 foreign keys；
- 使用显式事务；
- schema 使用整数 migration version；
- 每个写请求使用 expected revision 或合法状态迁移；
- 数据库与 Markdown 的跨介质写入使用 operation record / outbox 恢复，而不是假定原子；
- 备份数据库时使用 SQLite backup API 或安全 checkpoint，不直接复制活动中的 WAL 文件组合；
- 损坏和 migration 失败必须显式停止并保留原文件。

## 与现有 JSON 的关系

2.0 不立即删除现有 `.survey-tool/*.json`：

1. v1 功能继续读取原 JSON；
2. v2 schema 先建立导入器和只读 adapter；
3. 每个领域垂直迁移后，SQLite 成为该领域状态的唯一 authority；
4. 兼容 JSON 如有必要由 SQLite 确定性导出；
5. 禁止长期双向同步。

现有 canonical Markdown 不批量改写。migration 只登记对象 ID、路径、hash 和关系；需要格式升级时逐文件生成 diff 和报告。

## 未选择方案

### 仅 Markdown / JSON

部署简单，但无法可靠处理越来越多的关系、lease、Job 和跨对象查询。

### SQLite 保存所有正文

事务简单，但会破坏当前 pi、Obsidian、Git 和人类直接阅读的工作流，也会使研究内容导出成为必要步骤。

### 独立数据库服务

对本地单用户工具过重，增加部署和备份复杂度。SQLite 已足够支持当前并发模型。

## 后果

正面：

- 运行状态有事务、约束、索引和 migration；
- Markdown 研究资产继续开放可读；
- 对象关系、Inbox 和 Job 查询更可靠；
- 可逐领域迁移。

代价：

- 需要严格维护 authority map；
- 跨 SQLite / 文件写入需要恢复协议；
- 备份和迁移文档更复杂；
- Agent 不应直接编辑数据库，必须通过 API / `surveyctl`。

## 第一阶段 schema 范围

只建立 2.0 基础设施表，不立即迁移所有 Experiment / Run 字段：

- `schema_migrations`
- `objects`
- `object_relations`
- `events`
- `jobs`
- `inbox_items`
- `agent_sessions`
- `automations`
- `automation_steps`
- `migration_records`

Experiment Outbox 等现有可靠 JSON 合同在对应垂直迁移前继续保持 authority。
