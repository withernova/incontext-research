# 20260929T055808Z--multi3-rank-cf-latest-eval · 反事实三框模型验证

- workflow: v2 / code_planning / 代码方案
- review_status: draft
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
新增分数反事实训练后，模型在独立验证集上能否更常选中 IoU 最优候选，同时保持候选框质量？

## 2. 目的
对本次 E-013 反事实 GRPO 的最新完整 checkpoint 做一次全量验证，分别报告按分数选框、首框和三框 oracle 的定位表现，并按 GT 最优框位置核查分数排序。

## 3. 方法（干预 · 对照 · 指标与判定规则）
等待当前训练退出且 SZY-3090 双卡空闲；选择该训练 Run 最新完整 adapter checkpoint；在固定 1766 条验证清单上用三框实例提示、确定性解码和最高 score 选框；输出预测、标准指标及 GT 最优框分组统计。

**指标计算定义**：score 选框 mIoU、Acc@0.5/0.75、首框 mIoU、三框 oracle mIoU、非首框选择率；按 GT 最优候选位置报告平均三个 score、最终选择位置和正确选择率。

**判定门槛 / no-silent-zero**：固定验证清单哈希；三框提示与训练协议一致；仅选择已完整写入 adapter 权重与配置的最新 checkpoint；评测时不与训练争用双卡；保存 checkpoint 路径和完整预测。

## 4. 详细实现细节
双卡运行仓库已有 MultiCandidateLocalizationDataset、MultiCandidateLocalizationEvaluator 和 tools/run_branch.py；验证配置 configs/sft/e013_multi3_rank_cf_eval.py；离线分组脚本 tools/analysis/e013_cf_eval_summary.py。

**数据身份与构造**：SZY-3090 项目内 E-009 现有 test_combined_lasot600_gotval_taoval_1shot_focus.json 验证清单，SHA-256 48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b；用户已明确授权本次测评读取。

**数据规模**：1766 条验证样本；全量，无抽样。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash /defaultShare/archive/songzhengyue/projects/IPLoc/tools/tmux-local/launchers/20260929T055808Z--multi3-rank-cf-latest-eval.sh`
- commit: `be40ea7b13d03aa5b3e59a12a25066e83ea74998`
- workspace: 03
- tmux: incontext-E-013-20260929T055808Z--multi3-rank-cf-latest-eval
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/launch_logs/20260929T055808Z--multi3-rank-cf-latest-eval.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260929T055808Z--multi3-rank-cf-latest-eval/evaluation
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
父训练按用户要求在step470停止，本次评测使用step450完整checkpoint，不能代表原定3 epoch终点。验证清单混合LaSOT与GOT10k/TAO验证划分；未在本轮读取其他Run结果作直接对照。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "implementation_details": "双卡运行仓库已有 MultiCandidateLocalizationDataset、MultiCandidateLocalizationEvaluator 和 tools/run_branch.py；验证配置 configs/sft/e013_multi3_rank_cf_eval.py；离线分组脚本 tools/analysis/e013_cf_eval_summary.py。",
  "data_definition": "SZY-3090 项目内 E-009 现有 test_combined_lasot600_gotval_taoval_1shot_focus.json 验证清单，SHA-256 48b7b0537816cef608b1be6c926c03ec30827941fdfba6c3d3278d3da66a2d9b；用户已明确授权本次测评读取。",
  "data_scale": "1766 条验证样本；全量，无抽样。",
  "metric_definition": "score 选框 mIoU、Acc@0.5/0.75、首框 mIoU、三框 oracle mIoU、非首框选择率；按 GT 最优候选位置报告平均三个 score、最终选择位置和正确选择率。",
  "integrity_gates": "固定验证清单哈希；三框提示与训练协议一致；仅选择已完整写入 adapter 权重与配置的最新 checkpoint；评测时不与训练争用双卡；保存 checkpoint 路径和完整预测。",
  "conclusion_scope": "该checkpoint在本验证清单上未利用后续更优候选框；可支持score选择失效的行为描述，不能单凭此测评断言反事实训练机制无效或优于/劣于未读取的对照Run。",
  "claim_boundary": "不把训练 rollout 当作独立验证，也不凭单次测评断言信用分配机制的因果性。",
  "artifacts": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260929T055808Z--multi3-rank-cf-latest-eval/evaluation/metrics.json; /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260929T055808Z--multi3-rank-cf-latest-eval/evaluation/score_position_summary.json; /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260929T055808Z--multi3-rank-cf-latest-eval/evaluation/predictions.jsonl"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
