# 全仓库审查（进行中）

## 用户目标

对现有 config、Run Shell 和相关模块代码做全方位审查。不限于最近的重构或一个实验。不限 token 数量，但不以耗时/读取数量代替质量证据。

## 基线与授权范围

- 仓库：`code-repositories/03/iploc-szy`。
- 基线：`1622e5f64a70239d02145f017cfd991cf8318e47`；审查开始时 Git 工作区干净。
- 本次为审查，不自动修复、删除文件或重写计算逻辑。
- 不运行测试套件、构建、import/smoke、模型、服务器命令或实验；这些未获本轮明确授权。
- 不 push/deploy；不改变 Run 状态、目录、源数据或 checkpoint。
- 前两轮重构的静态等价记录可作为历史证据，但不能替代当前集成链路审查。

## 成功标准与交付核对表

| 用户要求 | 必须提供的证据 | 当前状态 |
|---|---|---|
| 现有 config 全面审查 | 全量配置清单、继承与覆盖、来源/路径/协议/资源/输出契约的实际源码核对 | 待完成 |
| Run Shell 全面审查 | 全量脚本与 alias、执行/转发、CLI/环境/GPU/目录及失败传播链 | 待完成 |
| 相关模块代码全面审查 | 公共基础、模型/数据、SFT/蒸馏/GRPO、评测、干预、分析、构造与统计覆盖 | 待完成 |
| 软件工程和科研复现边界 | checkpoint/恢复、snapshot、原始输出、指标和 GT 使用、默认行为/兼容的跨层核对 | 待完成 |
| 不依赖绿灯替代审查 | 每个问题有源码位置/触发条件/影响；测试覆盖与未验证范围分别记录 | 待完成 |
| 审查结论可追踪 | 版本/文件哈希、覆盖账本、分级问题、修复建议、最终逐项审计 | 进行中 |

## 覆盖等级

- `inventoried`：登记路径、类型、版本和哈希，不表示已审阅逻辑。
- `static_scanned`：源码 AST/引用/结构扫描，不表示手工逐行或行为验证。
- `read_complete`：当前版本全文实际读取，不表示发现的问题已核实。
- `reviewed`：职责/接口/风险与相关链路已核对，记录审查备注和证据。
- `archival_classified`：历史检查/备份产物已分类，不将重复快照当作当前执行代码。
- `excluded_with_reason`：明确排除的非源码或需外部运行授权的验证；不得把排除项算通过。

## 范围初查

Git 跟踪 1264 个文件。主要目录：138 configs 文件（129 Python 配置）、132 tools 文件（导航扫描 88 个 Shell）、110 package 文件、61 tests 文件、21 docs 文件。另有 `.task-backups` 273 个和 `.task-checks` 520 个跟踪项，其中包含旧测试快照、锁、软链接和 checkpoint 占位产物，总计约 3.67 MB。需要作为仓库卫生/复现来源问题单独核对，不能只审查显眼目录。

主要活动源码合计约 4.2 万行（configs/tools/package/tests），不包括隐藏备份。81 个跟踪软链接解析目标均不在本代码仓库内，本次仅记录链接自身，未跟随读取；不能把它们当作活动源码已读。

## 进度

1. 已核对当前 Git 版本、工作区和已有审查材料位置。
2. 全量 tracked 清单/哈希及源码导航已生成。754 个非软链接 Python 文件按 3.9 AST 语法解析、88 个 Shell 经 bash -n 解析，均无语法错误；这些不是运行或语义验证。
3. 已全文实际读取 230 个当前文件，按 coverage.json 的逐文件 full_text_read_with_tool 布尔证据去重计数（早期简单累加计数已纠正）。129配置声明范围完成：87非config_alias全文读、42literal-only alias目标/图核对。88Shell主体/转发范围完成：全文读或严格短模板核对，其中21 common shortcuts、27 relative aliases；另1固定绝对旧checkout alias单独记录，不假称当前部署。29个-m/analysis入口经AST存在/re-export解析核对，不import执行。
4. 当前129配置AST无import且只用dict/sum(values)/list(range)，顶层未见模型/产物/GPU/目录IO；不是安全沙箱。GRPO20文件全文已读，数学/模式/数据/保存/observer审查写入grpo_contract_review.md。公共生命周期、SFT/pipeline/hooks/蒸馏与公共候选评测的跨层源码契约已有独立报告；head干预、AP消费者、统计/数据及全量测试/依赖/文档覆盖继续。
5. `findings.md` 暂记录20个source_confirmed问题、1个科学设计风险、1个仓库卫生问题，共22项。新增A017 SFT resume未绑定数据/布局一致性、A018 optimizer只读取lr/weight_decay而忽略其他键、A019 teacher partial-resume无来源绑定而可能混用/重新标注旧maps、A020宽松bbox parser对部分非法结构抛转换异常，可能中止整批指标并尚未保存原始predictions。继续核对head核心后新增A021 decodability忽略bbox rows而平均全序列A@V、A022 steerability零有效配对仍completed/exit0。所有运行触发均未实际执行；不据此否定历史Run。
6. 尚未完成全仓审查。已完成配置/Shell声明与入口层覆盖，不等于worker算法全通过。SFT数据/collator/grammar与periodic head hook依赖已补入报告；下一步head筛选/干预、评测消费者/统计/数据构造的完整语义，再完成测试定义/依赖/文档/历史Run证据及最终逐项审计。

文件：`coverage.json`、`source_navigation.json`、`structural_scan.json`、`shell_syntax.json`、`shortcut_template_review.json`、`config_source_calls.json`、`shell_forward_template_review.json`、`entrypoint_existence_review.json`、`config_shell_review.md`、`common_runtime_contract_review.md`、`sft_distillation_contract_review.md`、`grpo_contract_review.md`、`evaluation_contract_review.md`、`head_screening_contract_review.md`、`findings.md`。这些只记录真实审查事实；空白状态不是通过。
