# E-013 GRPO 基础模块与上游对齐（2026-10-10）

## 目标与范围

回应用户关于自主实现严谨性、基础模块抽象和 Visual-RFT 对应关系的要求。开始前重新读取 canonical E-013/Workspace 03，并经 Survey Tool `code prepare` 准备本地仓库，基线为 `9d42d2be43464988cde879857a9d31864cf49851`。prepare 未创建远端提交，未启动实验。

完成提交：`1639e24ec845610957fc17dd127dfad0148a4ec9`。改动 13 个精确任务文件，实际 code_change_review 审阅通过，无阻断项或警告。本次保留现有算法和奖励默认值，未修改任何实验配置、Claim、审批或 Run 授权。

Survey Tool `code publish --workspace-id 03 --commit 1639e24ec845610957fc17dd127dfad0148a4ec9` 已成功，退出码 0；回执 `push_performed=true`、`execution_started=false`。本地工作树干净。

## 完成内容

- `rl/core.py`：与任务无关的分组优势、token log-prob 选择、KL、clipped surrogate 和 completion mask 归约。提供批量张量接口及独立诊断量；现有逐条训练通过兼容入口复用同一数学核心，维持原 mean 路径。
- `rl/task.py`：从 trainer 提取奖励选择、框坐标参数、score counterfactual 资格与奖励提升门禁。只接收任务数据和 processor，不依赖 model/optimizer。
- `rl/counterfactual.py`：集中 score-token preference 辅助数学项；`objective.py` 保留旧导入兼容。采样直接使用基础核心的 log-prob 工具。
- `docs/GRPO_UPSTREAM_ALIGNMENT.md`：固定上游 commit、文件哈希、阶段映射、张量契约、算法差异和验证边界。初版文档增加历史版本提示。
- `tests/test_grpo_core.py`：11 项基础检查，包括上游数值对照、不同长度 mask、padding 零梯度、正负优势的 clipping 梯度和原默认归一化。
- fixture 的期望值由固定版本 Visual-RFT 原始 9 条数学赋值直接导出；生成脚本在执行这些赋值前核对源文件 SHA-256。随仓库提交生成脚本与数值，自动测试无需联网。

## 上游依据

固定 Visual-RFT commit：`2ffad63b25ddd79bfe25d3e046645401201c89d6`。

[trainer 源文件](https://github.com/Liuziyu77/Visual-RFT/blob/2ffad63b25ddd79bfe25d3e046645401201c89d6/src/virft/src/open_r1/trainer/grpo_trainer.py)，实际已获取，SHA-256 `138f15aabf846751fc0ddbc9fe9da9224173a4f4342312213995917b2b12a0c1`。

对照覆盖 advantage、loss、KL 和梯度。数值相同的条件明确为：上游样本标准差与 `1e-4` epsilon、old=current.detach、相同 completion mask 和 reference 概率。本项目训练仍使用原有总体标准差与 `1e-6`，不能称整个 trainer 完全复现上游。

## 实际检查

1. 全仓 CPU 回归：`547 passed, 2 deselected, 3 warnings`，退出码 0。
   - 使用已存在临时环境 `/tmp/iploc-cpu-check`，命令显式设置 `PYTHONPATH=.` 并先 import torchvision。
   - 排除项沿用此前已独立确认的原有 `test_native_noop_gt_and_restore[eager]` 零容差 CPU 精度问题，以及依赖真实模型资产的 processor 测试。
2. 重构前后合成训练对照：使用 Git HEAD 提取的原 trainer 与原 objective，对 steps/epochs、模拟单/双 rank 的四种组合验证输出记录、optimizer state、RNG 和完成元数据一致，退出码 0。
3. 实际两进程 CPU/Gloo 对串行 global batch：2 个 optimizer step，通过；包含 counterfactual 双前向、非重入 checkpointing、梯度累积和 anchor 切换，anchor 不变；梯度最大绝对差 `3.725290298461914e-09`，退出码 0。
4. 上游 fixture 重生成后逐字节一致；Ruff 未定义符号、Python 3.9 语法、git diff whitespace 检查通过，退出码均 0。

过程中的失败已定位并处理：提取 helper 后过早访问 tokenizer，恢复到资格门禁通过后才访问；首次全仓测试未传 PYTHONPATH，两个子进程入口无法导入包，修正检查命令后通过。未通过修改测试断言掩盖失败。

精确命令和审阅回执见同目录 `grpo_core_alignment_20261010_review.json`。

## 剩余问题

此前发现的 multi3/multi3_rank 有效奖励相同，以及排序与 Brier 目标冲突，仍需单独明确实验语义后处理；不能把它们归为不影响结论的小细节。本次只做基础层抽象和可核验的上游对照。

没有执行真实 CUDA/NF4/NCCL 验证，没有部署服务器或启动训练。当前 Solid Run ID：无；未使用其他实验或历史 Run 结果作为证据。canonical 主指标、成功标准和对照仍缺失，不能据工程测试推断科学有效性。
