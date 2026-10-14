# 如何阅读和维护一个 Experiment

先打开 `shell/06_experiments/<E-ID>/<E-ID>.md`。不要从目录中的几十个文件逐个开始读。

## 在网页中检索子目录文档

入口是 **实验页面 → 选择一个 Experiment → 文档** 页签。不是 Run 分组，也不会把其他 Experiment 放进当前 Experiment。

- 搜索框匹配**标题、文件相对路径、专题属性**，包含子目录；不是正文全文检索。
- “子目录”选择框可选择 `diagnostics` 或更深的目录。选择后包含该目录的子目录，不会搜索其他实验。
- 可按核心文档、Run 文档、专题文档和版本标记筛选；“最近修改”排序将专题文档放在工具生成页之前。
- 点击结果进行只读阅读，切换“Markdown 原文”查看原始文本，或“复制路径”后在 Obsidian 找同一文件。
- “重新检索”实时读取当前目录，不写文件。“更新 Obsidian 导航”需要确认，只刷新所选实验的三页生成文档，不移动目录。

### HTTP 接口

所有接口都必须点名 Experiment；项目路径按 URL 编码传入。

```text
GET /api/v2/p/<encoded-project>/experiments/E-012/documents?q=report&directory=diagnostics&sort=modified
GET /api/v2/p/<encoded-project>/experiments/E-012/documents/content?path=diagnostics/report.md
POST /api/v2/p/<encoded-project>/experiments/E-012/documents/refresh
     {"confirmation":"REFRESH EXPERIMENT DOCUMENTS E-012"}
```

查询参数：`q`、`directory`、`kind=all|core|run|topic`、`sort=path|modified`、`status=all|current|superseded|draft|archived|unmarked`。列表返回文档及子目录候选、匹配数和扫描提示；GET 不初始化数据库或写研究文件。内容预览上限为 512 KiB。

### Experiment 目录独立性

`E-012` 的独立目录必须是 `shell/06_experiments/E-012/`，与 `E-013/` 同级。

- 如果 `E-013/E-012/` 意外存在，扫描 E-013 时**跳过**该目录并提示，不能把 E-012 的文件归属给 E-013。
- 如果独立目录缺失，文档 GET/刷新返回 `409 experiment_directory_unavailable`；CLI 文档预览/刷新也会拒绝操作。
- 重建 Obsidian 索引会跳过缺失的实验目录，不自动补建、移动或合并目录。实际目录恢复必须先由用户确认。
- 符号链接、`../` 路径和嵌套 E-ID 不能用于跨实验读取。允许显式引用其他实验，但引用不改变文件归属。

## 在 Obsidian 中找对应文档和最近修改

1. 从 `index/Experiments.md` 选择实验，点击该行的“文档目录”；也可在快速切换中搜索 `E-012-documents` 或别名 `E-012 文档目录`。
2. 每个实验都有独立命名的 `<E-ID>-documents.md`。在这页内搜索标题、文件名、目录或 `doc_topic` 专题即可找对应文档。目录包含子目录报告，不只列顶层文件。
3. 实验入口和文档目录都有“最近修改”列表。它按专题文件修改时间倒序显示最多 10 篇。自动生成的核心页、Run 笔记和索引不参与此排序，避免每次工具回写后占满列表。
4. 同名 `report.md` 会显示标题和精确路径，并使用相对文件链接定位；不使用 `[[report]]` 猜文件，也不把文件夹链接当作报告入口。
5. 目录是刷新时的快照。仅在 Obsidian 编辑、新增或移动文件，不会自动更新目录；编辑后使用网页“更新 Obsidian 导航”或运行下方刷新命令。无需 Dataview 等额外插件。网页的“文档”页签则按查询直接扫描当前文件。

**最近修改不等于当前有效版本。** 文件复制、迁移或手工整理可能改变修改时间。工具不会从 `latest`、`final`、日期文件名或修改时间推断哪个研究结论有效。

### 可选：明确标记当前版本和替代关系

为需要长期查找的专题文档添加少量 Obsidian 属性。例如：

```yaml
---
doc_topic: 第二框塌缩分析
doc_status: current
---
```

旧版本可标记为：

```yaml
---
doc_topic: 第二框塌缩分析
doc_status: superseded
superseded_by: diagnostics/second_box_report_v2.md
---
```

- `doc_status` 支持 `current`、`superseded`、`draft`、`archived`。它只控制阅读导航，不是 Run 状态、科研审核或执行授权。
- `doc_topic` 是显式专题名。文档目录按这个字段识别同一专题；同一专题有多个 `current` 时全部列出并提示冲突，不擅自选出一个。
- `superseded_by` 是**相对 Experiment 根目录**的 Markdown 路径。目录只为已索引且有效的目标生成链接；找不到目标时给出提示。
- 标题优先取 `title` 属性，其次取一级标题，最后才用文件名。不复制正文，也不自动重命名已有文档。
- 属性只支持上述平面字符串；无需嵌套 YAML。没有标记的文档显示“未标记”，不会自动进入“当前版本”区。

扫描会排除符号链接、源码审阅工作树、`research_tmp`、缓存、依赖、数据集和 `checkpoints`。扫描深度、文件数和读取量都有上限；无法读取或超限会显示提示。因此目录是研究阅读导航，不是完整的磁盘清单。

## 三种阅读顺序

- **了解现状（约 1 分钟）**：入口页的研究目标 → 已有结论 → 开放问题 → 当前 Run 状态。
- **复盘过程**：入口页的 Run 登记时间线 → `events.md` 中的变更原因 → 对应 Run 笔记及产物。
- **核对结论**：`result.md` 摘要 → 数值、比较对象、不确定性和来源 → 详细审计正文。完成状态不等于证据有效，也不等于 Claim 已获批准。

## 每种文件只负责一种问题

| 文件 | 用途 | 更新方式 |
|---|---|---|
| `<E-ID>.md` | 阅读入口、记录时间、Run 导航、最近修改 | 工具生成；只在最后的“自由笔记（Obsidian）”节手写阅读提示 |
| `<E-ID>-documents.md` | 子目录文档、标题、精确路径、修改时间与显式版本标记 | 工具生成，不在此页手写；版本属性写在专题文档内 |
| `brief.md` | 用户原始目标和约束 | 通过 Experiment 字段更新 |
| `plan.md` | 假设、干预、对照、指标和判定规则 | 通过工具更新；自由笔记可手写 |
| `result.md` | 先展示摘要和结论边界，再展示分组 Run 数值与来源 | 工具管理摘要和表格；最后的“详细审计正文（canonical）”节可手写 |
| `events.md` | 每次动作何时发生、为什么发生 | 用 `surveyctl event` 追加；完整 details 按事件 ID 查询 |
| `review.md` | AI 审核意见 | 导入审核意见；不代表人工 Claim verdict |
| `mission.md` | Agent 的操作规则与权限边界 | 工具生成；不是研究总结，不必作为研究者的首读文件 |
| `runs/<group>/<run-id>.md` | 单轮问题、方法、实现、数值、解释和复现信息 | Run 字段通过工具更新；自由笔记可手写 |
| 专题 Markdown | 某个问题的深入分析和证据 | 保留原文；入口页提供导航，不自动摘要或评级 |

不要把同一段结论复制进所有文件。入口只引用 Experiment 已登记摘要。详细论证放到审计正文或专题文档，保留来源链接。

## 时间的含义

- **记录截至**：Experiment 和 Run 的最后有效 `updated`（缺失时用 `created`）记录中的最大值。不包含专题文档修改或尚未回写的远端进展。它不是当前时间，也不是实时健康检查。
- **Run 登记时间线**：按 Run 的 `created` 从早到晚排列。实际启动时间、重试和中止原因请查事件记录。
- 缺少日期就写“未登记”。不从 Run ID、文件名或文件修改时间推断实际运行时间。
- 有时区的记录按 UTC 排序；旧的无时区记录仅按钟面时间排序。混合这两种记录不能用于精确计算间隔。
- 创建时间无效的记录置后。原始日期保留显示，不能为了排序而补造日期。

专题分析建议在开头注明：**问题、所用 Run/产物、资料截至时间、观测、解释、限制、后续问题**。当旧解释被新证据替代时，加明确的替代说明和链接，不静默改写历史。

## 结果缺失不等于实验没有结果

结果页同时读取 v2 `key_results` 和 `metric_observations`，分别标注来源类别。它们不自动合并或求平均；辅助指标不会自动成为主指标。

“摘要未登记”与“没有结果”必须区分。工具不会扫描日志或专题正文去猜结论。已有产物但未回写时，应先核对产物，再更新相应 Run 的结果字段。

## 刷新现有实验文档

先查看预览：

```bash
python3 surveyctl.py --project /path/to/project experiment docs E-012 --dry-run
```

确认预览后刷新：

```bash
python3 surveyctl.py --project /path/to/project experiment docs E-012
```

此命令只更新该 Experiment 的 `<E-ID>.md`、`<E-ID>-documents.md` 和 `result.md`。它不修改注册表、Run 状态、审核或执行授权，也不移动或删除专题文档。入口的自由笔记和结果页的详细审计正文会保留；其他手写内容不要放在工具管理区。

如果已经存在同名的非工具生成文档目录，显式刷新会拒绝覆盖。请先自行备份并重命名冲突文件。正常 Experiment/Run 回写遇到此冲突时保留原文件，并在入口显示提示；不会让可选导航阻断结果回写。

`--dry-run` 不写文件。刷新命令是显式写入，请在迁移核验完成后再使用。正常 Experiment/Run 更新会通过结果生成链路同步这三页；单独重建 Obsidian 索引刷新入口和文档目录，不刷新结果页。首次使用可在工作台中重建 Obsidian 索引，更新 `index/Experiments.md` 的目录入口；单个 Experiment 的 CLI 刷新不会重建全局索引。
