# e014-structure-score-iou-explore-v1-sft659-seed11451 · 三项奖励与条件探索训练

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-147b898d75a529bd0d48103a / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
整体替换为结构、最坏候选置信度、Selected IoU及条件探索扣分后，候选覆盖和最终定位是否改善？

## 2. 目的
用户明确要求启动刚实现的独立奖励方案训练。原SFT659 fresh初始化、纯GRPO、multi_v2、G4；不恢复旧训练，不使用旧多框补偿。

## 3. 方法（干预 · 对照 · 指标与判定规则）
采用structure_score_selected_iou_explore_v1：合法奖励1-.12O+1.1(1-max_i(s_i-y_i)^2)+SelectedIoU-.2z*I(SelectedIoU<.3)*(1-D)，y由同实例IoU>=.5给出，D为预测框间IoU<.9，非法总分-1；旧Ranking/Distractor/Coverage/Duplicate/Count/multi_bonus不参与。最终选框最高score并列取首。整体方案对照，不归因于单个探索项。后续评测另行登记，本次只训练。

## 4. 详细实现细节
指定发布SHA 1e2caec81668dafaf015005415d219b4e5e4ca2e；独立薄配置整块替换reward；score数字无CE，反事实权重0；沿用原4000条及1000对AB/BA/Reference切换派生4000条，总8000条；8GPU/G4/3epochs/1500updates/seed11451/max_new_tokens192/max_pixels262144/lr8e-5/beta.04/clip.2/save_every50。计划值需以启动快照核验。审阅1bf0165bbb510796通过，未测试；必要执行preflight按受管流程。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run.sh configs/experiments/E-014/training/e014_structure_score_iou_explore_grpo.py`
- commit: `1e2caec81668dafaf015005415d219b4e5e4ca2e`
- workspace: 03
- tmux: incontext-E-014-e014-structure-score-iou-explore-v1-sft659-seed11451
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-sft659-seed11451/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
（可留空；如有明显的数据、模型或比较限制，请简短记录。）

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "implementation_details": "指定发布SHA 1e2caec81668dafaf015005415d219b4e5e4ca2e；独立薄配置整块替换reward；score数字无CE，反事实权重0；沿用原4000条及1000对AB/BA/Reference切换派生4000条，总8000条；8GPU/G4/3epochs/1500updates/seed11451/max_new_tokens192/max_pixels262144/lr8e-5/beta.04/clip.2/save_every50。计划值需以启动快照核验。审阅1bf0165bbb510796通过，未测试；必要执行preflight按受管流程。",
  "claim_boundary": "新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
