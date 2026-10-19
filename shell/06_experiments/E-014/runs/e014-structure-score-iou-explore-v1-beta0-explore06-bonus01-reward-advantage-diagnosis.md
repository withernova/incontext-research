# e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis · 用户同意检查多框消失前两层。仅用显式既有75步分析Run e014-structure-score-iou-explore-v1-beta0-explore06

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451`
- 来源版本：2026-10-14T19:38:49
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户同意检查多框消失前两层。仅用显式既有75步分析Run e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis/source_snapshot，不读取新live日志。逐条合法多框与保留首框/保留实际selected框单框的反事实奖励比较，拆分score/IoU/空间顺序/.6探索/.1补偿收益；按第一框和SelectedIoU条件、original正负/collage/时间分层。对实际G4组检查mixed组多框单框胜率/adv、单框组共同扣分抵消、非法多框及token预算；必要反事实仅重算已有组，不伪装生成或更新。无模型重放、训练变更、评测、持续监控或Claim升级。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：仅显式既有75步source_snapshot，独占保存副本/SHA；8rank共同1..75及4800rollout/1200G4完整核验。按记录的同实例candidate_ious/labels和原始生成bbox-score重新计算完整奖励与分项，并对合法多框保留首框/实际selected框为单框重算（不重新生成、GT不选框）。保存每条分项delta、first/selected IoU条件、worst错误类型、保留其他3回答的假设adv；实际G4 mixed胜率/mean差及actual adv，all4单框低IoU共同扣分抵消、去掉.1/.6分项对已有组优势变化，非法raw多框/token预算。原始adv来自日志，float64重算仅校验符号/误差记录，不等同float32更新或训练效果。时间/原正负/collage分层，无模型重放/训练变更/新增测试/持续监控/Claim升级。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/analyze.py
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json

## 结果
75步固定快照4800rollout/1200G4，反事实与组诊断exit0。首框IoU<.3：168条中162条多框奖励更高，mean+.68683，但其中82条实际负adv。首框IoU>=.5：240条中177条追加后奖励更低，mean-.37426（score-.23460/SelectedIoU-.19767/order-.042/+bonus.1）。第73步2条首框IoU.667/.552、score0，错第二框IoU0/score.95，追加无额外score/结构惩罚但选错，reward1.1低于首框单框1.667/1.552，adv均-.99931。100 mixed组等权胜率46%、mean差-.03385，多框251正216负adv；40..75正组421中低IoU组88，有87组无合法多框，57组四条低IoU单框共同-.6抵消。raw多框509含42非法，其中28达到192且未终止。只诊断奖励/同组信号，未检查EOS概率/梯度，不能确定单一收缩机理。

### 辅助指标
```json
[
  {
    "metric_id": "completed_updates",
    "value": 75,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json"
  },
  {
    "metric_id": "legal_multibox",
    "value": 467,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json"
  },
  {
    "metric_id": "positive_multibox",
    "value": 422,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json"
  },
  {
    "metric_id": "first_only_delta_mean",
    "value": 0.05951801140126039,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json"
  },
  {
    "metric_id": "mixed_groups",
    "value": 100,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json"
  },
  {
    "metric_id": "mixed_group_win_rate",
    "value": 0.4599999999999999,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json"
  },
  {
    "metric_id": "uniform_low_single_groups",
    "value": 93,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis/metrics.json"
  }
]
```

### 分析
# E-014 多框奖励与组内优势诊断

分析 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis`。用户同意完成前两层检查。仅复用显式75步分析Run的不可变source_snapshot：4800 rollouts、1200完整G4组，4728合法；不读取新live日志，不加载模型、不改训练。受管分析exit0/complete，结果待人工科研审阅，Claim不变。

## 主要发现

1. 探索补偿在首框明显失败时有明确收益，不能说奖励没有生效。第一框IoU<0.3的168条合法正多框，162条相对只保留第一框奖励更高、6条更低，平均差+0.68683。
2. 第一框已经准确时，当前实际多框经常比停止更差。第一框IoU>=0.5的240条里，177条奖励降低（73.75%），63条提高；平均差-0.37426。score错误增加和选错框收益损失远超0.1补偿。
3. 自身反事实收益不能等同实际组内优势。上述162条首框失败且追加有收益的回答中，82条仍是实际负advantage，80条为正。它们虽胜过自身截短版本，仍可能输给同Query其他回答。
4. 采样收缩之后，可学习到的多框相对信号很少。40–75步共421个正样本G4组，其中88组有低SelectedIoU回答，87组没有合法多框；57组四条均为低IoU单框、共同扣0.6，标准化后共同扣分抵消。
5. 这些是现有轨迹的诊断，不能单独证明EOS概率变化的原因。未做第三层checkpoint概率重放，也没有token级梯度/结束概率证据。

## 同一回答的反事实奖励

只保留原始第一候选，保持bbox与score不变；假设该单框合法正常结束。不是模型重新生成或早停控制，不是GT选框。使用已有同实例candidate_ious/labels及原始bbox-score，重算顺序、distinct与当前奖励；完整回答各分项重算通过。

| 正样本首框条件 | n | 多框比首框单框更高/更低 | 平均reward差 |
|---|---:|---:|---:|
| IoU<0.3 | 168 | 162 / 6 | +0.68683 |
| 0.3<=IoU<0.5 | 14 | 7 / 7 | -0.03199 |
| IoU>=0.5 | 240 | 63 / 177 | -0.37426 |

首框IoU>=0.5时，平均差额拆分：

| 分项 | 多框减只留首框 |
|---|---:|
| 空间结构 | -0.04200 |
| 加权score | -0.23460 |
| Selected IoU | -0.19767 |
| 条件探索 | 0 |
| 新增多框补偿 | +0.10000 |
| 总差 | -0.37426 |

该240条中，140条追加后最大score误差变大，84条逆序，58条最终选中框IoU低于首框。这些集合重叠，不相加。

全部422条合法正多框，平均相对首框仅+0.05952（232胜/190负），分项为结构-0.05289、score-0.18110、IoU-0.04536、探索+0.23886、bonus+0.1。不能用总体平均掩盖首框条件差异。

另对照只保留实际Selected候选，排除选框改变。当实际SelectedIoU>=0.5时，219条中148条保留额外框降低奖励、71条提高，平均差-0.16935，来自结构-0.04712与score-0.22223，bonus仅+0.1。没有框数扣分，但额外候选实际引入了其他扣分。

## 第73步两条回答的具体失败

两条来自同一rank/Query/G4组，均合法两框、无逆序、非近重复：

- 第一框IoU分别0.66730、0.55232，score都为0.00，标签1。
- 第二框IoU为0，score为0.95，标签0；因此最终SelectedIoU=0。
- 最大score误差由第一框低置信度造成，E=1；追加没有进一步增大score扣分，也没有结构扣分。
- 完整多框reward均1.1；只留首框reward分别1.66730、1.55232，损失0.56730/0.45232。
- 这两条actual advantage均-0.99931。只把该条替换成首框单框、保留组内另三条不变时，假设adv为+0.94464/+0.60906。这只是重算诊断，不是实际更新。

这直接说明：即使追加没有额外score或结构惩罚，仍可能因score选错框损失定位奖励，0.1不能抵消这种损失。

## 实际G4组信号

- 1200组里，179组有合法多框，100组同时有合法单框与多框。
- mixed组按组等权multi-single严格胜率46.0%，mean(multi)-mean(single)=-0.03385；collage对应48.79%、-0.02473。实际多框251正adv、216负adv，并非始终受负向更新。
- 在固定已有组内移除0.1后重算，只有4条多框由原正adv变为非正。它仍可能增大其他多框优势或减轻负优势；符号翻转数不是全部作用。
- 全期93组四条均低IoU单框，共同探索扣分抵消。40–75步其中57组，仍缺少实际多框对照。
- 探索分项在119组有差异，其中80组没有合法多框，差异来自单框定位跨越0.3阈值等已有轨迹，而不是直接多框比较。
- 原日志adv为float32；stdlib float64重算的最大差0.00372，非微小adv符号不一致0。共同探索项移除后优势差最大7.93e-12（float64）。不以float64假设adv冒充实际更新。

## 格式与预算

509条raw多框中42非法（8.25%）；其中28条未正常终止且达到192 token预算，14条协议非法。合法单框/多框平均completion tokens为30.95/72.06。非法reward=-1，不进入合法截短奖励比较。这是额外风险来源，不能单凭这些比例证明长度或预算是主因。

## 结论与边界

支持的诊断是：失败首框后的探索收益有效；首框已准确时当前追加候选的score和选择质量往往抵消0.1；同组中多框优势不稳定；采样收缩后，共同扣分无法提供多框相对信号。不能将结果简化为统一“奖励没有生效”或单纯“系数不够大”。

没有检查checkpoint上的EOS/继续生成概率或token级梯度，因此具体策略收缩机理仍未确认。本轮不更改奖励、采样、预算或训练，不增加模型评测，不升级Claim。分析已执行并核验，测试/模型重放未执行。

明细：counterfactual_rows.jsonl、group_rows.jsonl；汇总analysis.json、additional_counts.json；完整性/SHA为integrity_audit.json。原始快照在独立Run保留。


### 局限
未测试/模型重放/评测；没有EOS继续概率或token梯度证据。未改训练，不读live日志、不持续监控。

### 结论范围
只用显式不可变75步训练快照，现有回答反事实与实际同Query G4组诊断；假设reward/adv不代表重新生成或更新，单seed非因果，Claim不变。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/analysis/e014/e014-bonus01-diagnosis/analysis.json
.pi/analysis/e014/e014-bonus01-diagnosis/report.md
.pi/analysis/e014/e014-bonus01-diagnosis/counterfactual_rows.jsonl
.pi/analysis/e014/e014-bonus01-diagnosis/group_rows.jsonl
.pi/analysis/e014/e014-bonus01-diagnosis/integrity_audit.json
.pi/analysis/e014/e014-bonus01-diagnosis/additional_counts.json

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
