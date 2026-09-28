# E-013：无需重新 SFT 的多候选推理评测

目标：对同一 baseline SFT 和 GRPO step-500 checkpoint，在同一 1,766 条测试样本上比较单框与多候选推理。此次不训练模型。

## 固定协议 v2

- 要求模型输出恰好 3 个框假设，每个框紧跟自己的 score。它们都针对 Reference 中的同一实例，可表示不同位置或边界假设，并非检测三个不同物体。
- 沿用已有标签格式，每行 `<answer>[x1,y1,x2,y2]</answer><score>0.00</score>`。
- 分数为 0.00–1.00、两位小数，无需总和为 1。不强制分数或框的解码语法。
- 最高 score 选框，同分选先输出者；选择过程不接触 GT。未遵循三个框但给出 1/2 个完整合法框时，仍按其实际候选选择，同时单列数量遵循率。畸形或夹杂额外文字的整条输出判为无效，不截取合法片段补救。
- 贪心生成，最大 192 new tokens；四卡；视觉预处理仍为 4,096 patch tokens / 1,048,576 pixels，与已有单框 confidence 评测一致。
- 提示词全文由 `iploc_szy/evaluation/multi_candidate.py:candidate_prompt` 生成，并保存为每次汇总目录中的 `prompt.txt`。

v1 启动检查允许“最多三个，可少给”，8 条样本均只给一个框，无法检验多候选选择。因此仅根据数量遵循性改为 v2 的明确三框要求，并停止尚未完成的 v1 全量评测。没有按这 8 条的 IoU 调整提示词。

## 对照与指标

- Baseline checkpoint：`focus-confidence-sft/checkpoints/samples_00042136_step_000659`。
- GRPO checkpoint：`20260921T172801747698Z--focus-confidence-grpo-overnight-ready/grpo/checkpoints/step_000500`。
- 单框对照：`20260922T053508406009Z--baseline-confidence-ap-full`、`20260922T060906496816Z--grpo-step500-confidence-ap-full`。
- 主报告：选中框 mIoU、IoU@0.5/0.75、AP；诊断：首框、oracle 最佳框、数量分布、格式有效率、重复率、选择非首框比例。oracle 仅作为事后上限。
- AP 是合并样本的单目标定位 AP，按同分数聚合后计算全点插值面积；不是官方 COCOeval 的 101 点 AP。AP50–95 是十个 IoU 阈值的平均。
- 原清单有 10 条退化 GT（ID：163-1、170-1、178-1、208-1、215-1、220-1、226-1、227-1、265-1、335-1）。主 AP 对所有对照共同排除这些条目，使用 1,756 条有效 GT；同时保留 1,766 条历史 AP 口径用于追溯。mIoU 仍保留原全量口径。
- 清单 SHA-256：`48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b`。
- 自动核对样本 ID、dataset_index、dataset、sequence、GT、checkpoint 和视觉预算；保留每条件预测文件 SHA-256。

## 命令（远端代码仓库根目录，IPLoc 环境）

```bash
# 只读检查：不加载权重，不创建输出目录
python tools/analysis/run_e013_multi_candidate.py \
  --output-dir /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-013/multi3-v2-baseline-vs-grpo500 --inspect

# 串行跑两个四卡全量评测并汇总；输出目录必须是新的
IPLOC_PYTHON=/root/miniconda3/envs/IPLoc/bin/python \
  python tools/analysis/run_e013_multi_candidate.py \
  --output-dir /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-013/multi3-v2-baseline-vs-grpo500
```

单独评测一个模型：

```bash
bash tools/run/run_branch.sh configs/sft/e013_multi_candidate_branch.py \
  branch.source=baseline named_run.run_name=baseline-multi3-v2

bash tools/run/run_branch.sh configs/sft/e013_multi_candidate_branch.py \
  branch.source=grpo_step500 named_run.run_name=grpo500-multi3-v2
```

这些是本次用户指定评测的工程产物，不改变实验审批、Claim 或 Solid 状态。

## 启动检查与执行状态（2026-09-22）

- 代码提交：`131165a`，既有通用 branch 文件中的用户修改保持原样。
- 130 项针对性测试通过；v2 修改后重跑 13 项多候选测试通过。
- v2 真实四卡检查：`20260922T070457653403Z--baseline-multi3-v2-smoke`，8 条输出中 5 条为三个合法候选、2 条为一个、1 条格式无效。检查仅用于验证代码与格式，不据此判断定位收益。
- 已启动串行全量评测。Baseline：`20260922T070728536077Z--baseline-multi3-v2-full`；其完成后程序自动加载固定的 GRPO step-500 checkpoint 做同一全量评测。
- 汇总目录（远端）：`/defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-013/multi3-v2-baseline-vs-grpo500`。`status.json` 为当前执行状态；每条件日志、`prompt.txt`、`protocol.json`、`partial_report.json` 和最终 `report.json` 均存于此。此处记录的是已启动，尚不声称两次评测完成。
