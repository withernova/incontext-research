# 本地代码可读性整理交付（2026-10-09）

## 完成内容

根据用户已确认的可读性优先方案，在真实绑定本地仓库完成改动、CPU 检查、Code Change Review、精确提交及工具发布。没有将临时审查快照当成正式源码，没有再使用 SSH patch。

本地仓库：`code-repositories/03/iploc-szy/`。改动共 10 个文件：5 个库源码文件、2 个测试文件和 3 份源码阅读文档。

- **GRPO**：用 `TrainingRuntime`、`PromptBatch`、`RolloutRecord`、`RolloutGroup` 明确模型依赖、输入、一次采样和同 prompt 分组；取消 rollout 数字索引。将奖励参数、反事实门禁、completion loss 和日志组织分开；14 个参数的 backward helper 改为具名依赖和少量关键字控制参数。`train()` 从 93 行降至 59 行。
- **SFT**：`run()` 从 161 行降至 14 行，阶段为 `_prepare_run`、`_train_step`、`_accumulate_microbatches`、`_finalize_run`；`_RunBaseline` 承载固定诊断数据。有限性检查、裁剪、optimizer/scheduler、Hook 和 checkpoint 顺序保持原实现。
- **Pruning worker**：`execute` 从 532 行降至 245 行；冻结样本、固定 donor/support 输入、读出评估、修改输入重编码和汇总各自有入口。两个相同的重编码分支复用 helper，保持其 token/预算校验及原错误信息。
- **Target/background worker**：入口从 558 行降至 155 行；冻结输入、模型资源、十项编码输出和基线结果改为具名对象，基线、条件执行、mask 保存、报告及 CSV 输出分段维护。
- 去除 Builder 的临时属性名调试输出，展开相关紧凑写法、整理格式并增加中文边界注释。新增 `docs/READING_TRAINING_FLOWS.md`，更新 GRPO/head-screening 阅读入口。

函数行数只用于描述阅读入口的变化；没有通过复制实验包或引入新框架完成整理。实验配置、采样分布、seed、loss 缩放、统计口径、保存格式和日志字段没有在此任务中改写。

## 检查结果

临时本地检查环境位于 `/tmp/iploc-cpu-check`，Python 3.11、Torch 2.8.0+cpu、Transformers 4.57.3、PEFT 0.17.1。没有改服务器依赖或提交依赖版本变化。匹配的 Torchvision 先加载，避免仓库针对旧环境的 NMS schema shim 与正常 CPU 扩展重复注册。

| 检查 | 结果 |
|---|---|
| 聚焦训练、微型 Qwen 重放/梯度、pipeline、pruning 检查 | 80 passed |
| 增补反事实资格、奖励提升、token 预算及单进程/累积同步控制检查 | 聚焦组合 34 passed |
| SFT 抽取阶段语句 AST 对比 | 4 个块一致 |
| Target/background 冻结输入、加载、基线、条件、数组写入与报告 AST 对比 | 6 个块一致，CSV 抽取展开后一致 |
| Pruning 冻结样本、donor、汇总及 CE/生成 readout AST 对比 | 一致；重编码两分支仅错误标签不同 |
| SFT 前后合成训练对比 | 权重、optimizer、scheduler、metrics 与 RNG 一致 |
| GRPO 前后合成训练对比 | steps/epochs 与同步/累积分支的日志、optimizer、完成记录与 RNG 一致 |
| Python 3.9 语法解析、Ruff 未定义名称检查、Git diff 空白检查 | 通过 |
| 全库 CPU 测试（未排除既有精度失败） | 536 passed，1 failed，1 deselected |
| 单独复核既有精度失败 | HEAD 原版与当前未改动 hook 出现完全相同的 `5.960464477539063e-08` 逐位相等失败 |
| 排除已复现基线精度失败及真实 processor 资产测试后 | 536 passed，2 deselected，3 warnings |

完整 CPU 测试命令在本地使用显式仓库包路径、先加载 Torchvision，再执行 pytest。原版精度失败位于 `tests/test_query_attention_intervention.py::test_native_noop_gt_and_restore[eager]`；hook 实现与该测试均未修改，没有放宽容差。真实 processor 检查为 `real_qwen_processor_alignment_when_available`，没有打开真实资产。

Code Change Review 使用工具实际提供的 `code_change_review` 扩展检查当前完整 diff、精确允许路径和测试证据，结果为 `passed=true`、`review_current=true`，无阻塞项或警告，并仅提交任务的 10 个文件。回执见同目录 `readability_refactor_20261009_review.json`。

## 版本与发布

- 准备命令：原 `surveyctl.py ... code prepare --workspace-id 03`。针对用户指定的 Windows SSH，在本次进程中适配 SSH 可执行文件；工具的自动发现、服务器空闲、分支、Git 状态、来源和同步检查保持运行，没有修改 Survey Tool 源码。
- 自动准备成功，创建项目内绑定与 clone；基线为 `4d279e1aadf05237f2430202a38bac2ef4e2c2e8`。
- Authored/published commit：`9d42d2be43464988cde879857a9d31864cf49851`。
- 提交说明：`Improve readability of GRPO, SFT and head-screening execution flows`。
- `code publish --workspace-id 03 --commit 9d42d2be43464988cde879857a9d31864cf49851` 退出码 0，`push_performed=true`，`execution_started=false`。
- 未执行 `code deploy`。本次新代码没有服务器 Linux/CUDA 验证结果，不将本地检查当作服务器通过。

## 剩余风险与边界

当前 CPU 环境中的原版逐位相等精度失败仍需独立处理；真实 processor、NF4 与多卡 GPU 行为未在本轮执行。同步覆盖使用合成模型验证控制边界，不能替代真实多卡训练。

之前记录的通用 adapter 完整性、SFT/GRPO checkpoint 契约与精确恢复能力边界仍在，本轮没有把它们混入可读性重构。

未读取历史 Run 结果、日志、凭据或 Agent memory，未启动实验、修改 Claim、审批或 Run 授权。代码绑定与发布由用户更新后的默认工具流程自动完成。Solid Run ID：无；本报告只提供工程验证。
