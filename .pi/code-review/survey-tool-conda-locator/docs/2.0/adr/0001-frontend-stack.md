# ADR-0001：2.0 前端采用 TypeScript 组件化应用

- 状态：Accepted
- 日期：2026-08-15
- 决策范围：Survey Tool 2.0 新界面

## 背景

当前前端是无构建步骤的 vanilla JavaScript SPA：

- `static/app.js`：2,112 行；
- `static/index.html`：单页入口；
- 少量纯逻辑已拆到 `static/js/*.js`。

现有方案安装简单，也便于把纯函数直接交给 Node 测试。但 2.0 需要：

- 全新一级导航和对象中心；
- Inbox；
- Paper Candidate / Job 状态；
- 多阶段 Run 和 Automation 页面；
- 草稿、diff、人工确认；
- 多对象关系；
- 统一异步加载、错误和权限反馈。

继续将这些功能加入单个 `app.js` 会显著增加回归和维护风险。

## 决策

2.0 新前端采用：

- TypeScript；
- React；
- Vite；
- 浏览器 History / Router；
- 生成静态资源后仍由 Python 本地服务托管；
- 核心状态机和 schema 使用可独立测试的纯 TypeScript 模块。

旧版 `static/` 在迁移期间保持可用。新应用先放在独立目录和独立路由下，以垂直切片逐步接管功能，不进行一次性替换。

建议目录：

```text
web/
  src/
    app/
    api/
    components/
    features/
      inbox/
      papers/
      questions/
      experiments/
      automation/
    domain/
    styles/
  tests/
  package.json
  vite.config.ts
```

构建产物进入可明确清理的目录，例如 `static/v2/`，源文件不与构建产物混放。

## 约束

1. Python 后端仍然可以零云服务运行；Node 仅作为开发和构建依赖。
2. 不把研究正文只存入 React 内存或浏览器 localStorage。
3. 服务端负责权限、状态迁移和 schema 校验；前端校验仅改善体验。
4. 高风险动作必须使用共享确认组件并显示服务端计算的影响。
5. 纯状态机、导入解析和格式化逻辑应保持无 DOM 依赖，便于测试。
6. 不在迁移期重写已有 Experiment / Run 合同。

## 选择 React 的原因

- 新页面交互复杂，组件和生态成熟；
- TypeScript 支持良好；
- Agent 生成和维护代码时有更稳定的常见模式；
- 可逐页嵌入，不要求后端同时换栈；
- 适合 Timeline、Board、Drawer、Diff 和多阶段对象编辑。

## 未选择方案

### 继续 vanilla JS

优点是无构建步骤、迁移成本低。拒绝作为 2.0 主方案的原因是现有单文件已较大，未来页面和异步状态复杂度远高于当前。

### Web Components

可以保持轻量，但状态管理、路由和团队通用性不如 React，无法显著降低本项目的整体实现风险。

### 全栈框架

Next.js 等方案会引入与当前本地 Python 服务重复的服务端能力，也扩大部署和迁移范围，暂不采用。

## 后果

正面：

- 类型化 API 和领域对象；
- feature 级边界；
- 更易实现非问卷式交互；
- 更易建立组件与浏览器测试；
- 旧 UI 可渐进迁移。

代价：

- 增加 Node 构建依赖；
- 需要管理构建产物；
- 一段时间内存在 v1 / v2 两套前端；
- 需要制定视觉组件和 API client 规范。

## 实施检查点

在开始 Paper 或 Experiment 页面迁移前，应先完成：

1. `web/` 工程骨架；
2. `/v2` 应用壳和路由；
3. 统一 API client；
4. 错误、加载、确认、状态徽标基础组件；
5. TypeScript 单测；
6. 至少一个浏览器 smoke test。
