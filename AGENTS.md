# AGENTS.md — In-Context Object Localization

> 遵循 **research-survey** skill（全局：~/.pi/agent/skills/research-survey）。
> 行动前先阅读其 SKILL.md，遵守反幻觉硬规则与项目约定（中文模板 C1、MinerU 优先 C2）。

## 项目输入（从 INTAKE.md 物化而来）
- **代码仓库路径：** `code-repositories/03/iploc-szy`（Workspace 03，本地独立 Git 仓库）
- **种子论文：**
  - zotero incontext
- **想法：** 测试 idea
- **领域：** in-context object localization
- **目标会议：** CVPR 2027
- **联系邮箱：** songzhengyue04@gmail.com

## 约束
- none

## 工作流
- 始终从 state.md 恢复进度。
- 声明存于 kernel/claims.md；只有 validated 的声明才能进入综合。
- 引用格式 [[citekey]] §小节。绝不允许引用未实际抓取过的论文。
- 论文内容问答：优先读取同名目录下 MinerU 抽取的 .md（含图像与公式）；否则对 PDF 做 read/pdf-converter 抽取。
- 使用 ~/.pi/agent/skills/research-survey/scripts/ 下的脚本。
- **E-002 填表/同步前必须读取** `shell/06_experiments/E-002/ledger_filling_skill.md`，并遵守其中 run id 一一对应、干预细节、shuffle 区域、token-grid、seed、selected-token-counts、结论边界等记录要求。

## 轻量衍生实验（用户约定）
- 单个 checkpoint 评测、已有产物分析、小范围参数变体，优先用 Survey Tool 的“衍生实验”入口；Agent 可调用 `survey_run_execution action=derive` 或 `surveyctl.py --project <本项目> run derive <父 Run> --request '<用户任务>'`。工具自动登记独立子 Run、父来源版本及数据/指标/seed/Workspace；不要求用户重填完整设计。
- 用户明确要求执行该任务即本次授权，Agent 直接准备并使用返回的子 Run ID 受管执行；不重复索要 submit-review / approve / authorize 或指定 SHA 部署确认。必要部署仍由 Agent 对具体已发布 SHA 执行并记录，不能部署 latest。只请求方案不等于授权运行。
- 只补本次实际变化、checkpoint 来源、真实命令/代码版本/seed、日志与产物、真实指标和简短结论边界。单次任务复用现有评测/分析入口，不要求 Trial manifest 或新增批量 runner。父训练的暂停/恢复须属于用户任务范围，不能自动继承父命令、结果、Solid 标签或授权。
- E-002 的专门干预事实由 Agent 自动记录；减少填表不删除复现事实。研究 Claim 的 validated 门禁保持原规则。

## 代码维护：职责优先，配置表达差异
- 修改代码前读取仓库的 `AGENTS.md`、`README.md` 和 `CONFIG_MANAGEMENT.md`；之后只读当前任务涉及的模块，不默认遍历全部实验历史。
- 实验编号表示研究归属，不表示实现职责。共享代码和工具按用途命名；编号、checkpoint、seed、数据范围和权重放在配置或 Run 记录中。
- 参数变化先用配置覆盖；需要长期维护的方案再新增薄配置。普通训练、评测和分析复用已有 launcher、worker、模型包装和快照接口，不默认新增协调器或配套 Shell。
- 如现有接口不能表达任务，先说明缺口，再扩展职责模块。不得复制整套实验实现后改编号。上述顺序是默认选择，不禁止必要重构：职责混杂、重复实现或入口难找时，可以重命名、移动、合并、拆分源码和入口目录；简述目标与取舍，不要求逐个文件申请批准。
- 重构时同批更新调用方、职责地图与导航。已发布接口、已登记 Run 命令及无法核清的外部引用保留必要薄兼容；纯内部引用已查清时可以直接迁移，不要求所有旧路径永久保留。不能留两套实现。
- 不擅动历史数据、checkpoint、日志、结果和 Run ID。不静默改变 prompt、奖励、采样、损失、优化器、指标或默认参数。科学变化与工程整理分开记录；所有权不明，或接口/科学变化及历史复现影响超出本次授权时再请求确认，不重复索要已明确授权的逐文件批准。
- 本次用户明确要求的本地离线整理不连接或更新远端。若改前同步被活动 Run 拒绝，应记录未同步的基线和原因；离线编辑不能视为已发布、已部署或执行授权。恢复在线流程后仍须正常核验同步、审阅和指定版本。
- 找已有入口时先读仓库 `docs/LAUNCH_CATALOG.md`（Config → Shell）和 `configs/ENTRYPOINT_INDEX.md`（Shell → Config/转发）。不要依赖修改时间或重读所有历史实现。
- 从研究项目根目录查单个实验及其 Run 记录：`python3 code-repositories/03/iploc-szy/tools/audit_entrypoints.py --source-only --catalog --experiment E-014 --project .`。该命令只读显式源码/Run 文档字段，不执行配置、检查 GPU 或修改 Run 状态。
- config/Shell/action/代码转发关系变化时，按仓库 `AGENTS.md` 同步生成全量源码导航、Shell 顶部注释与目录入口页，和实现一起审阅提交。单路径查找用 `tools/audit_entrypoints.py --source-only --trace PATH`；`--check-navigation` 只检查源码导航漂移。Run 文档/产物/历史ID不搬动，动态字段或缺失字段不得补造。
- 管理的目标是让下一位维护者少猜、少找、少复制：沿 Shell → Config（或明确的无 Config CLI）→ 代码入口 → 职责实现查找；参数属于配置、共享能力属于职责模块、执行事实属于 Run。不要为每次小改动复制一份管理表或增加多层目录。
- 新增文件在任务说明中简述职责和位置即可；一次性工具不强制框架化。对当前改动做相称的导航/引用/兼容检查，不把每个任务扩大成全仓审计，也不拿导航检查代替测试或实际运行。
- 具体入口与操作规则以仓库 `AGENTS.md` 为单一维护位置；项目层不复制完整细则。约定妨碍当前任务时允许有说明的简化方案，但不能解除历史产物保护、Claim 人工 verdict 或工具执行权限。

## Intake 缺口（如有）
- none
