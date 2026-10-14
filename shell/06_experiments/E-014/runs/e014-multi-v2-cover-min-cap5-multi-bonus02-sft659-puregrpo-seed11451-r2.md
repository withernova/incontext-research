# e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2 · 多框补偿独立训练（修正日志位置）

- workflow: v2 / ready_to_run / 等待执行授权
- review_status: approved
- group_id: 未分组
- execution_dispatch:  / 
- spec_drift_fields（批准后有改动）：config, implementation_details, implementation_summary, log_path, output_dir, purpose, run_type, variant

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
新奖励下同prompt混合采样组是否更偏好多框，且多框探索是否仍随训练减少？

## 2. 目的
从SFT659重新训练，观察一次0.2多框补偿是否保留多框尝试并改善真实候选覆盖；不是续训。

## 3. 方法（干预 · 对照 · 指标与判定规则）
复用父 Run 的数据与指标，按本次任务要求执行；实际差异记入实现细节。

**指标计划**：明确mixed组等权q主口径、strict>、tie与null；group/sample分母及条件窗口分层；保留pooled/best/mean差/正adv辅指标，不偷换指标定义。

**指标计算定义**：主诊断p_multi_reward_gt_single：对合法终止mixed组g，qg=sum_{multi i,single j}1[Ri>Rj]/(nM*nS)，再对mixed组等权平均。按采样组比较，绝不跨prompt/Reference/rank配对，actual total reward。空mixed分母null，strict>与tie分离。附mixed_groups/总groups/比较pairs、tie probability、mean组内multi-single reward差、best-multi vs best-single、pooled pair概率、multi实际正adv率、多框率(all/given-valid)、invalid、按original正/负和collage正分层、每50完成更新窗。

**判定门槛 / no-silent-zero**：冻结源manifest/alias/identity/GT/split/provenance；真实双源实例位置仅用于对称候选覆盖，不进入Query消息。独占payload拒绝覆盖，原checkpoint200/800只读。指定SHA部署/conda:IPLoc固定环境、8GPU idle、正式managed authorization。observer pending pre-update group不混入完成窗口，统计完整覆盖/rank/update校验，无mixed不静默0。

## 4. 详细实现细节
日志使用Run根managed_console.log，符合现有训练入口fresh脚手架契约；命令通过output.run_name覆盖到本Run ID。父Run仅记录失败来源，不加载其checkpoint或复用结果。原SFT659 fresh policy+固定anchor；multi_bonus_weight=0.2；min覆盖/cap5、multi_v2、纯GRPO、seed11451、8卡、3epoch/1500更新、每50存档和统计均沿用已发布配置。实际数据/训练快照写入本Run payload；旧失败目录全部保留。未运行额外测试。

**数据身份与构造**：冻结原trainable_pairs.json SHA017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130。原4000正负输入仅image路径派生到只读alias；1000同类不同身份/来源源对，AB/BA×ReferenceA/B生成4000对称正输入。只用真实源对象标注，其他对象不制造GT。

**数据规模**：8000输入/4000pair；原2000正+2000负；对称4000正。8rank500update/epoch×3=1500，2prompt/rank/update×4rollouts=64全局，完整96000生成。

**实现摘要**：修正受管日志位置，并用独立新目录运行已部署的多框补偿配置；奖励算法不变。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `bash tools/run.sh configs/experiments/E-014/training/e014_multi_v2_cover_min_cap5_multi_bonus_grpo.py output.run_name=e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2`
- commit: `69f786a3db89177cea11178714f560ce5760d36c`
- workspace: 03
- tmux: incontext-E-014-e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2/outputs
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
  "implementation_summary": "修正受管日志位置，并用独立新目录运行已部署的多框补偿配置；奖励算法不变。",
  "implementation_details": "日志使用Run根managed_console.log，符合现有训练入口fresh脚手架契约；命令通过output.run_name覆盖到本Run ID。父Run仅记录失败来源，不加载其checkpoint或复用结果。原SFT659 fresh policy+固定anchor；multi_bonus_weight=0.2；min覆盖/cap5、multi_v2、纯GRPO、seed11451、8卡、3epoch/1500更新、每50存档和统计均沿用已发布配置。实际数据/训练快照写入本Run payload；旧失败目录全部保留。未运行额外测试。",
  "metric_plan": "明确mixed组等权q主口径、strict>、tie与null；group/sample分母及条件窗口分层；保留pooled/best/mean差/正adv辅指标，不偷换指标定义。",
  "data_definition": "冻结原trainable_pairs.json SHA017bd2a64d1cb80dbb62152bf20a7fafada72a88cea4f5f3f88be152d1bb2130。原4000正负输入仅image路径派生到只读alias；1000同类不同身份/来源源对，AB/BA×ReferenceA/B生成4000对称正输入。只用真实源对象标注，其他对象不制造GT。",
  "data_scale": "8000输入/4000pair；原2000正+2000负；对称4000正。8rank500update/epoch×3=1500，2prompt/rank/update×4rollouts=64全局，完整96000生成。",
  "metric_definition": "主诊断p_multi_reward_gt_single：对合法终止mixed组g，qg=sum_{multi i,single j}1[Ri>Rj]/(nM*nS)，再对mixed组等权平均。按采样组比较，绝不跨prompt/Reference/rank配对，actual total reward。空mixed分母null，strict>与tie分离。附mixed_groups/总groups/比较pairs、tie probability、mean组内multi-single reward差、best-multi vs best-single、pooled pair概率、multi实际正adv率、多框率(all/given-valid)、invalid、按original正/负和collage正分层、每50完成更新窗。",
  "integrity_gates": "冻结源manifest/alias/identity/GT/split/provenance；真实双源实例位置仅用于对称候选覆盖，不进入Query消息。独占payload拒绝覆盖，原checkpoint200/800只读。指定SHA部署/conda:IPLoc固定环境、8GPU idle、正式managed authorization。observer pending pre-update group不混入完成窗口，统计完整覆盖/rank/update校验，无mixed不静默0。",
  "claim_boundary": "主诊断高且multi率下降支持Exploration瓶颈假设，但不能单独确定主要原因或排除Reward Design。该Run不自动validated Claim，不输出因果结论；工程complete不等于收益。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
