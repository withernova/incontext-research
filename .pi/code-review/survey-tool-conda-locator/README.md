# survey-tool — 研究调研工作台

本地可视化工具，配合仓库内的 [`research-survey` skill](skills/research-survey/SKILL.md) 与 pi agent 使用。
把 research-survey 的文件型工作流变成可视化交互：论文细读 + 七问 + 图片标注 + 代码探测、多对比项目、全局 Idea 讨论。

> 网页模型或代码审阅者请先阅读 [`docs/WEB_MODEL_REVIEW.md`](docs/WEB_MODEL_REVIEW.md) 和 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。多机器使用见 [`docs/MULTI_MACHINE.md`](docs/MULTI_MACHINE.md)。

## 快速开始

```bash
git clone git@github.com:withernova/survey-tool.git
cd survey-tool
cp config.example.json config.json   # 修改本机项目路径
python3 server.py
# → 浏览器打开 http://127.0.0.1:7421
```

配置见本地且不入库的 `config.json`（`projects_root` / `projects` 注册表 / `skill_dir` / `port`），或命令行 `--port/--root/--skill` 覆盖。后端只依赖 Python 3 标准库；KaTeX 静态资源已 vendored。

如需 terminal pi 的 research-survey skill、steward、轻量 plan 和通用代码改动审阅：

```bash
./scripts/install-pi-components.sh
# 然后在 pi 中 /reload，或重启 pi
```

安装脚本以符号链接方式指向当前 clone，不会复制出第二份可编辑源码。
扩展主名为 Experiment Steward（实验管家），命令 `/steward`。旧 `/watchdog` 和旧工具名仅作为 deprecated aliases 暂时兼容；安装脚本只安装新扩展，避免新旧两份同时运行。

Research Explorer（自由研究探索器）提供 `/explore` 与 `research_explorer_control/round/finalize`，围绕 Experiment、Idea、Question、Comparison 做有 deadline/轮次上限的 proposal 探索。浏览器只生成 terminal pi 协调指令；边界与文件布局见 [docs/RESEARCH_EXPLORER.md](docs/RESEARCH_EXPLORER.md)。

Light Plan 扩展为多步骤编码任务提供 Codex 风格的 `update_plan` 工具，并将当前计划原子写入项目的 `.pi/plan.json`。它限制最多一个 `in_progress` 步骤，并拒绝跳步完成；可用 `/plan status` 查看、`/plan clear` 清除。简单单步任务无需建 plan。

Code Change Review 扩展提供 `code_change_review`：在准备提交、交接或启动 Run 时，批量审阅代码改动，检查范围越界、疑似凭据、危险命令、diff 完整性，以及用户要求时实际执行的测试证据。未测试不阻断代码交付，必须如实标注。审阅绑定固定 Git 基线与内容；仅暂存或提交已审阅的内容不会使它失效，后续内容修改会。Run 实现未通过当前内容审阅时不能进入 managed execution。若 Agent 漏调，扩展会在本轮结束时自动补审并把阻塞项交回修复。

远程代码任务在每项可验证改动完成后及时提交，包含实验开始前的实现和重跑前的修复。调用 `code_change_review` 时传远端 `ssh_host`、`repository_path`、已获授权且实际执行的 `test_evidence`（未测试可省略）、本任务的精确 `commit_paths` 和 `commit_message`；工具只暂存指定文件，审阅通过后仅提交这些文件，返回 commit SHA、`review_id` 和 `review_current`，不自动 push。审阅失败会保留暂存改动但不提交；提交钩子改变内容时 `review_current=false`，需要重新检查。先核对已有用户改动，避免同文件内混入他人修改；目录、通配符、子模块和已识别的重命名不走这一便捷提交入口。

## 文件结构

```
survey-tool/
  server.py          # 本地 HTTP 服务器（stdlib only）+ JSON API
  surveyctl.py       # terminal agent 的稳定 Experiment/Run 写回桥
  config.example.json
  DATA_CONTRACT.md   # 前端↔文件↔pi 的数据流通规则（必读）
  static/            # vanilla JS SPA + vendored KaTeX
  skills/research-survey/
  extensions/experiment-steward/
  extensions/light-plan/
  extensions/code-change-review/
  scripts/install-pi-components.sh
  docs/
```

## 项目注册表（registry）

### 本地 Zotero 库

在运行服务的机器上，`~/.pi/agent/multi-workspace.json` 的 `workspaces.zotero.path` 指向包含 `zotero.sqlite` 的绝对目录，而不是 `storage` 附件子目录。WSL 访问 Windows 库时，例如填写 `/mnt/c/Users/zhengyuesong/Zotero`。修改配置后刷新本地库即可。

论文库 → 检索新论文 → Zotero 本地库支持关键词、PDF 和未添加筛选，可勾选多篇连续添加；已登记条目复用候选，已在正式论文库中的条目不重复添加。添加后保留当前列表，可在“候选与本地任务”中继续准备 PDF、解析和纳入论文库。没有本地 PDF 的条目可以仅登记文献信息。Zotero 新增文献后点击“刷新本地库”。

组件浏览器回归使用模拟文献：启动 `npm --prefix web run dev -- --host 127.0.0.1 --port 5177` 后运行 `SURVEY_TOOL_COMPONENT_TESTS=1 SURVEY_TOOL_URL=http://127.0.0.1:5177 npm --prefix web run test:e2e -- zotero-browser.spec.ts`。

### 研究项目

顶栏下拉列出**已登记的研究项目**，来源是两路并集：
1. `config.json` 的 `projects` 数组——你在哪创建/注册就记哪。
2. 自动扫描 `projects_root` 下含 `state.md` 的目录（pi 用 bootstrap.py 建的项目也能被发现）。

- **＋ 新项目**：选父目录（默认 projects_root）+ 名称 → bootstrap 建骨架 → 自动登记路径。
- **＋ 注册已有**：粘贴一个已有 research-survey 项目目录（需含 state.md）→ 登记。

## 数据层契约（核心）

- **规范研究工件** → `kernel/` `shell/` `state.md`：pi 直接读。前端写。
- **工具/UI 元数据** → `.survey-tool/`（项目根下）：pi **永不读**，仅前端用。

这样与 pi 讨论时不会被前端冗余信息污染。详见 `DATA_CONTRACT.md`。

| 前端动作 | 规范落点 | pi 可见 |
|---------|---------|--------|
| 七问文本 / 图片标注 | `shell/03_evidence/papers/<citekey>.md` | ✅ |
| claims | `kernel/claims.md` | ✅ |
| ideas | `shell/00_idea/idea.md` | ✅ |
| 研究疑问 | `shell/01_questions/Q-xxx.md` | ✅ |
| 对比正文 | `shell/04_comparisons/<comparison-id>.md` | ✅ |
| Findings | `shell/04_comparisons/findings/F-xxx.md` | ✅ |
| 对比结构兼容索引 / triage | `.survey-tool/` | ❌ |
| Obsidian MOC 索引 | `index/*.md` | ✅ |

## API 速查

```
GET  /api/config
GET  /api/projects
POST /api/projects/init          {name, slug}
GET  /api/p/<proj>                state + counts + citations
GET  /api/p/<proj>/papers         from INDEX.md
GET  /api/p/<proj>/paper/<ck>     note + seven-q + annotations + claims + images + tool-state
PUT  /api/p/<proj>/paper/<ck>     {seven, annotations, state}
GET  /api/p/<proj>/claims
POST /api/p/<proj>/claims         {text, sources, citekey, rationale}
PUT  /api/p/<proj>/claim/<Cxx>    {fields}
GET  /api/p/<proj>/ideas
POST /api/p/<proj>/ideas
PUT  /api/p/<proj>/idea/<Ixx>      {fields}
GET  /api/p/<proj>/compares       canonical Markdown + legacy JSON structure
POST /api/p/<proj>/compares        append project
PUT  /api/p/<proj>/compares        {compares:[...]}
GET  /api/p/<proj>/questions
POST /api/p/<proj>/questions       create Q-xxx.md
PUT  /api/p/<proj>/question/<Q-ID>
GET  /api/p/<proj>/obsidian
POST /api/p/<proj>/obsidian        configure vault + generate index
POST /api/p/<proj>/obsidian/index  regenerate MOC
GET  /api/p/<proj>/publish         published GitHub snapshot metadata
POST /api/p/<proj>/gpt/assistant   canonical objects + precise focus → bounded GPT instruction
POST /api/p/<proj>/gpt/parse       parse a forgiving GPT Markdown response for preview
POST /api/p/<proj>/sync           zotero_sync
POST /api/p/<proj>/scan-github
POST /api/p/<proj>/clone          {repo, dir}
GET  /file/<proj>/<relpath>       serve project file (images/PDFs)
```

## 与 pi 协作

pi 只读规范文件。讨论时无需贴前端状态，直接让 pi 读 `kernel/claims.md`、`shell/00_idea/idea.md`、`shell/01_questions/*.md`、`shell/03_evidence/papers/*.md` 和 `shell/04_comparisons/**/*.md` 即可继续 GATHER/R2/synthesis。

终端 Agent 创建实验时必须通过稳定 bridge，并绑定已登记 Workspace：

```bash
python3 surveyctl.py --project <project> experiment create E-003 \
  --title "实验名称" --workspace-id W-01 --objective "简单实验概要" \
  --evidence-ref F-004
python3 surveyctl.py --project <project> run create E-003 \
  --id E003-R-001-smoke-n2 \
  --variant "最小 smoke test" --purpose "验证实现链路" \
  --necessity "正式实验前排除环境/解析链路失败" \
  --data-definition "数据来源、split身份与构造规则" \
  --model-config "模型、checkpoint与关键参数" \
  --metric-definition "指标公式与TP/FP/FN计数规则" \
  --integrity-gates "预期records、role counts、finite/parser/traceback门槛" \
  --claim-boundary "smoke仅支持链路可运行，不支持科学性能结论"
```

Experiment ID 可省略以自动分配；显式 ID 必须形如 `E-003`。创建只生成 `draft` 初稿和 canonical Markdown，不会执行 Run。

Run 的 `--id` 是必填的 canonical/descriptive ID，同时作为 registry 主键、canonical Markdown 文件名和默认远端产物目录名；新 Run 不再自动分配全局 `R-xxx`。不要再把真实 Run ID 塞入 `variant`、`notes` 或 event。历史自动编号可在核对真实目录与 note 后迁移：

```bash
python3 surveyctl.py --project <project> run rekey R-010 \
  E003-R-004b-joint-f1-iou-local-lasot-n140-t128 \
  --adopt-existing-note
```

如果目标 note 已存在而未显式指定 `--adopt-existing-note`，迁移会停止；采用已有 note 时，旧工具生成的 `R-010.md` 会归档到 `.survey-tool/migrations/run-notes/`。

科学 Run 不应只有命令和 metrics JSON。跨项目最低登记字段包括：必要性/证据链位置、研究依据、数据身份与构造、模型配置、变量与对照、指标定义、完整性门槛、观测结果、局限、可支持结论、不支持结论和审核入口。完整性门槛失败时必须保留 `failed/incomplete/aborted` 状态，禁止 silent zero。评测审计还必须区分“缺少 joint metric”和“没有评测 component”，并区分官方 split 与本地 reconstruction。

`.survey-tool/compares.json` 只保留旧 UI 结构兼容；对比分析与 Finding 的 canonical prose 已进入 Markdown。

## 阅读实验内部文档

网页入口：**实验 → 选择 Experiment → 文档**。可按标题、路径或专题搜索，筛选子目录（包含更深目录）、类型和版本，并只读查看文档。每个 Experiment 独立；遇到嵌套 E-ID 会跳过并提示，缺失目录不会自动补建。

实验代码默认自动从 Workspace 远端仓库的 origin 和当前分支建立本地 Git 绑定，无需手填 URL、分支和路径；SSH origin 的首次克隆也保留 SSH。已有绑定不覆盖，显式远程模式可保留。新绑定存放于研究项目的 `code-repositories/<Workspace-ID>/<仓库名>/`，首次准备时克隆，不进入 Publish。私人代码仓库默认改前远端 commit/push、本机 ff-only 同步；本地审阅及提交后立即 code publish；测试仅按用户明确要求执行。服务器部署仍需指定 commit 授权，不自动启动 Run。见 [本地代码工作流](docs/LOCAL_CODE_WORKFLOW.md)。

Obsidian 中先读 `shell/06_experiments/<E-ID>/<E-ID>.md`；找具体报告时打开同目录的 `<E-ID>-documents.md`。最近修改不等于当前有效版本。HTTP 接口、子目录检索、Obsidian 阅读与刷新方式见 [Experiment 文档指南](docs/EXPERIMENT_DOCUMENTS.md)。

## 典型流程

1. **新项目**：顶栏「＋ 新项目」→ 跑 bootstrap.py → 填 INTAKE.md → pi 里 "intake done"
2. **同步论文**：左侧列表来自 `papers/INDEX.md`；更新在 pi 里跑 zotero_sync
3. **细读**：选论文 → 扫代码 → 抽 claims → 填七问（自动存规范笔记）→ 引用图片标注
4. **疑问/对比**：随时「记一个疑问」→ 在同一项目 Vault 中深究 → 建对比 → findings → 归档到 Idea
5. **询问 GPT**：顶栏「询问 GPT」→ 选主对象和具体项目索引 → 添加参考对象 → 生成/复制 → 顶栏统一导入并预览写回
6. **Idea**：补假设/证伪/支撑 → 提交为 claim → pi 继续 GATHER + R2 + 人工审核
7. **综合**：pi 跑 SYNTHESIS（只用 validated claims）

应用内点右上「？帮助」也有同样说明。

## 回归测试

```bash
python3 -m unittest -v tests/test_experiment_contract.py
npm --prefix web test
```

这些测试覆盖富 Run 字段 round-trip、schema 外字段拒绝、项目级并发更新、原子 JSON/损坏显式报错、状态迁移、Run 审核/独立执行授权门禁和调用方 timeout。

## 推荐的 Run 人机协作

算法实现优先：Agent 先完成数据流、损失/梯度、干预逻辑与指标计算。默认不运行测试、构建、smoke 或 import/启动检查，也不新增测试 Run；只有用户明确要求时执行。未测试不阻断代码交付、审阅或提交，必须标注“未测试”，不编造 test_evidence 或声称已验证。仓库默认测试约定不算本轮授权，也不得通过委派其他 Agent 绕过。Git 与路径安全检查、代码审阅、凭据保护、禁止强推和正式 Run 授权仍保留。

```text
Agent 在工具中创建完整 draft Run
→ Agent submit-review 后停止
→ 用户在 Run 页面审核
   ├─ 补充要求/提问并退回
   │  → Agent 只完善该 Run 并重新 submit-review
   └─ 批准当前规范
      → 用户另行授权本次执行
      → 将点名执行指令发给终端 Agent
```

`approved` 只表示 Run 规范已冻结，不会自动激活或执行。正式执行还要求单独的 `execution_authorized_at`，且审核后的数据、变量、命令、seed、artifact 路径等规范不得变化。
