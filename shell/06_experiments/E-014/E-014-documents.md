---
survey_tool_generated: true
type: experiment-document-catalog
aliases: ["E-014 文档目录"]
---
# E-014 · 文档目录

- [返回 E-014 实验入口](E-014.md)
> 本页是刷新时的文件快照。可在 Obsidian 当前笔记内搜索标题、路径或专题；不是实时索引。

## 当前版本（仅按显式标记）

> 只有 doc_status: current 的专题文档进入此区。工具不按文件名或修改时间选出“权威版本”。同一专题有多篇 current 时全部保留并提示冲突。

（暂无显式标记的当前版本；请先看最近修改列表，不把它当作有效性判断。）

## 找文档与最近修改

> 以下按专题文件修改时间倒序排列，最多 10 篇；不是“当前有效版本”，也不是实际运行时间。文件复制可能改变修改时间。新增或编辑文档后需刷新索引。

| 最近修改（UTC） | 专题文档 | 版本标记 |
|---|---|---|
| 2026-10-14T01:05:38+00:00 | [G8 step150：1766样本评测与训练日志诊断](visualizations/g8-step150-20261014/report.md) · <code>visualizations/g8-step150-20261014/report.md</code> | 未标记 |
| 2026-10-11T07:25:25+00:00 | [E-014：变长候选 prompt 与当前常用 prompt 的完整对照](prompt_comparison.md) · <code>prompt_comparison.md</code> | 未标记 |

## 核心文档

| 问题入口 | 文件 |
|---|---|
| [原始目标](brief.md) | <code>brief.md</code> |
| [实验方案](plan.md) | <code>plan.md</code> |
| [结果与审计](result.md) | <code>result.md</code> |
| [事件时间线](events.md) | <code>events.md</code> |
| [审核意见](review.md) | <code>review.md</code> |
| [Agent 操作规则](mission.md) | <code>mission.md</code> |

## 专题文档（按目录排列）

> 文件标题取自 title 属性或一级标题；路径用于区分同名 report.md。版本标记只用于阅读导航，不代表科研审核或执行授权。

### 实验根目录

| 文档标题 / 专题 | 精确路径 | 文件修改（UTC） | 版本标记 / 替代入口 |
|---|---|---|---|
| [E-014：变长候选 prompt 与当前常用 prompt 的完整对照](prompt_comparison.md) | <code>prompt_comparison.md</code> | 2026-10-11T07:25:25+00:00 | 未标记 |

### visualizations/g8-step150-20261014

| 文档标题 / 专题 | 精确路径 | 文件修改（UTC） | 版本标记 / 替代入口 |
|---|---|---|---|
| [G8 step150：1766样本评测与训练日志诊断](visualizations/g8-step150-20261014/report.md) | <code>visualizations/g8-step150-20261014/report.md</code> | 2026-10-14T01:05:38+00:00 | 未标记 |

## Run 文档（精确路径）

- [e014-cover-min-cap5-step150-eval1766-8gpu · 最新min覆盖/cap5分支step150、multi_v2、原1766八卡评测](runs/e014-cover-min-cap5-step150-eval1766-8gpu.md) · <code>runs/e014-cover-min-cap5-step150-eval1766-8gpu.md</code>
- [e014-multi-bonus02-g8-sft659-seed11451 · 用户选方案1并要求重新训练及约400步自动评测：新独立训练从原SFT659 fresh policy+固定anchor，纯GRPO；仅settings.trai](runs/e014-multi-bonus02-g8-sft659-seed11451.md) · <code>runs/e014-multi-bonus02-g8-sft659-seed11451.md</code>
- [e014-multi-bonus02-g8-step150-eval1766-r2 · 用户明确要求“修正然后评测”，授权修正前次output_dir布局错误后一次新评测。保留失败父Run全部产物，新Run根级outputs为canonical o](runs/e014-multi-bonus02-g8-step150-eval1766-r2.md) · <code>runs/e014-multi-bonus02-g8-step150-eval1766-r2.md</code>
- [e014-multi-bonus02-g8-step150-eval1766 · 用户要求现在停止G8训练并开始评测，不再等400。训练已按授权停止，8rank实际完成154更新；最新完整保存checkpoint为本父Run payload/](runs/e014-multi-bonus02-g8-step150-eval1766.md) · <code>runs/e014-multi-bonus02-g8-step150-eval1766.md</code>
- [e014-multi-bonus02-g8-step400-eval1766 · 用户追加要求新G=8训练约400step时自动评测400step。此独立评测仅在父训练保存payload/grpo/checkpoints/step_00040](runs/e014-multi-bonus02-g8-step400-eval1766.md) · <code>runs/e014-multi-bonus02-g8-step400-eval1766.md</code>
- [e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001 · 对 step150 的 ckpt 进行评测一下](runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001.md) · <code>runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001.md</code>
- [e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2 · 多框补偿独立训练（修正日志位置）](runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2.md) · <code>runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2.md</code>
- [e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451 · 用户要求发布部署后立即启动本次已实现的0.2多框奖励独立训练。以已发布部署的69f786a3db89177cea11178714f560ce5760d36c为准](runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451.md) · <code>runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451.md</code>
- [e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451 · multi_v2 / min实例覆盖 / soft预算5 / 同组奖励诊断 / freshSFT659纯GRPO](runs/e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451.md) · <code>runs/e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451.md</code>
- [e014-multi-v2-step200-eval1766-8gpu · multi_v2本分支step200、原1766样本八卡评测](runs/e014-multi-v2-step200-eval1766-8gpu.md) · <code>runs/e014-multi-v2-step200-eval1766-8gpu.md</code>
- [e014-multi-v2-symmetric-sft659-puregrpo-seed11451 · multi_v2多实例枚举、两行模板、原SFT659独立纯GRPO](runs/e014-multi-v2-symmetric-sft659-puregrpo-seed11451.md) · <code>runs/e014-multi-v2-symmetric-sft659-puregrpo-seed11451.md</code>
- [e014-step800-variable-candidates-eval1766-8gpu · step800原1766样本八卡变长候选评测](runs/e014-step800-variable-candidates-eval1766-8gpu.md) · <code>runs/e014-step800-variable-candidates-eval1766-8gpu.md</code>
- [e014-variable-symmetric-sft659-puregrpo-seed11451 · SFT659 变长候选与双向对称数据纯 GRPO](runs/e014-variable-symmetric-sft659-puregrpo-seed11451.md) · <code>runs/e014-variable-symmetric-sft659-puregrpo-seed11451.md</code>

## 扫描范围与提示

- 仅扫描本实验内 Markdown 的标题和少量平面属性；不复制正文，不跟随符号链接。
- 排除隐藏目录、review_worktree*、research_tmp、codespace、依赖、缓存、数据集和 checkpoints。
- 上限：8 层目录、10000 个目录项、1000 篇 Markdown；标题/属性只读取前 16384 字节。
- 未展示的源码或临时资料仍在原位置；扫描结果不代表全部研究资料。
