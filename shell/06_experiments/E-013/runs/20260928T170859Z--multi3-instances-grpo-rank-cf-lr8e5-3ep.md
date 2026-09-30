# 20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep · 三框分数反事实训练

- workflow: v2 / ready_to_run / 等待执行授权
- review_status: approved
- group_id: 未分组
- execution_dispatch:  / 

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
在相同三框排序GRPO与SFT初始化下，增加仅监督score数字token的反事实偏好损失，能否改善错选更优候选框的问题？

## 2. 目的
比较原三框排序GRPO与额外加入score反事实偏好损失的训练，检查选框改善是否同时保留候选框定位质量。

## 3. 方法（干预 · 对照 · 指标与判定规则）
保留原GRPO reward与训练清单。对有效三框正例，仅在GT最优框唯一、IoU至少0.5、与错选框IoU差至少0.1、分数严格排错且交换后现有reward提高时，交换两个score字符串；仅对score数字token计算anchor校正的偏好损失，并以0.1权重加到原GRPO loss。

**干预与对照**：与原三框排序GRPO相比，新增counterfactual.weight=0.1及score偏好通路；SZY-3090只有两张GPU，本Run用双进程而原配置为四进程。SFT起点、训练清单、学习率、轮数、group_size和解码参数保持一致；GPU数差异需在结果比较时列为限制。

**指标计算定义**：验证集报告score选框mIoU、首框mIoU、oracle三框mIoU，并按GT最优框位置统计score选择位置与正确选择率；训练日志记录CF pair数、CF loss和交换reward增益。

**判定门槛 / no-silent-zero**：格式有效且恰好三框；score交换不改bbox文本；交换后必须选中GT最优框且现有reward提高；tokenizer往返和数字token span严格对齐；无CF pair时不得标记完成。

## 4. 详细实现细节
SZY-3090双卡；从songzhengyue E-013 SFT checkpoint初始化；学习率8e-5、3 epochs、group_size=4、max_new_tokens=192；使用独立命名Run目录。训练启动检查tokenizer数字span对齐，训练结束要求至少产生一条CF pair。

- 公共包：`iploc_szy`
- 入口：`iploc_szy.rl.trainer:train`
- 配置：`configs/grpo/e013_multi3_rank_cf_branch.py`
- Shell launcher：`tools/run/run_branch.sh`
- 复用模块：iploc_szy/rl/multi_candidate.py, iploc_szy/rl/objective.py, iploc_szy/rl/trainer.py
- 新增模块：iploc_szy/rl/counterfactual.py
- 测试：tests/test_e013_counterfactual.py, tests/test_e013_grpo_tiny.py

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `cd /defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy && PYTHONPATH=/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy /root/miniconda3/envs/IPLoc/bin/python tools/run_branch.py configs/grpo/e013_multi3_rank_cf_branch.py named_run.timestamp=20260928T170859Z`
- commit: `bc1b3c59a300c1e7b6ec06ef8b00e5835eb59895`
- workspace: 03
- tmux: incontext-E-013-20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep/logs/grpo.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-013/focus-confidence-sft/branches/20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep/grpo
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
score损失仅直接监督数字token，共享模型参数仍可能影响框生成；双卡与原四卡训练配置存在进程数差异；效果需要独立验证集判断。目前Run尚未获得Survey Tool执行授权，未启动真实8B训练。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "现有GRPO把整条输出的单个优势作用于框和分数；需要独立训练通路检验score排序信用分配是否限制选框。",
  "implementation_details": "SZY-3090双卡；从songzhengyue E-013 SFT checkpoint初始化；学习率8e-5、3 epochs、group_size=4、max_new_tokens=192；使用独立命名Run目录。训练启动检查tokenizer数字span对齐，训练结束要求至少产生一条CF pair。",
  "variables_controls": "与原三框排序GRPO相比，新增counterfactual.weight=0.1及score偏好通路；SZY-3090只有两张GPU，本Run用双进程而原配置为四进程。SFT起点、训练清单、学习率、轮数、group_size和解码参数保持一致；GPU数差异需在结果比较时列为限制。",
  "metric_definition": "验证集报告score选框mIoU、首框mIoU、oracle三框mIoU，并按GT最优框位置统计score选择位置与正确选择率；训练日志记录CF pair数、CF loss和交换reward增益。",
  "integrity_gates": "格式有效且恰好三框；score交换不改bbox文本；交换后必须选中GT最优框且现有reward提高；tokenizer往返和数字token span严格对齐；无CF pair时不得标记完成。",
  "claim_boundary": "本Run仅比较训练路径与评测行为，不凭训练rollout推断验证泛化或内部因果机制。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
