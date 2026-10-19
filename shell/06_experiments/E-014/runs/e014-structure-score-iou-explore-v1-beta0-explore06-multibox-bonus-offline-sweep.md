# e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep · 用户同意离线扫描额外多框补偿0.1/0.2/0.3/0.5。只用显式75步诊断Run固定source_snapshot及counterfactual_rows，

- 父 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis`
- 来源版本：2026-10-14T22:01:17
- 状态：analysis_pending
- Workspace：03

## 本次任务
用户同意离线扫描额外多框补偿0.1/0.2/0.3/0.5。只用显式75步诊断Run固定source_snapshot及counterfactual_rows，保持已生成回答和其他奖励/score/IoU/选择/G4不变，重算各真实同Query G4组reward和组内优势、mixed胜率与平均差，分source/时间/首框与SelectedIoU，检查Oracle有正确候选却score选错的回答和第73步2例是否仍低奖励/负adv。不改当前训练/代码/参数，不重新采样/模型重放/评测，不持续监控或Claim升级。

> 用户任务已登记一次执行授权；继承父 Run 的数据与指标，不要求重复填写完整设计。

## 执行记录
- 实际变化：单次离线扫描0.1/0.2/0.3/0.5，复用显式75步诊断Run source_snapshot及counterfactual_rows，复制SHA、验证4800rollout/1200G4组与467CF逐条匹配。新total=原total+(lambda-.1)*合法正样本distinct资格；其他reward/候选/score/选择/IoU不变，非法-1、负样本不变。各组按总体std+1e-6 float64重算诊断adv（与日志float32近似，baseline多框符号核验）；mixed组等权严格胜率/mean差、多框正adv及首框/Selected条件、source/window分层、Oracle正确而Selected错的风险子集与73步2例。无eligible组及4条全eligible组优势不变核验；保留逐条/逐组扫描明细。仅分析已有轨迹，不重新生成或更新，不改当前训练/代码/参数、无模型重放/评测/持续监控或Claim升级。

2026-10-15 服务器目录整理（用户明确要求）：原目录 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep 已原样迁至 /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep；Run ID、数据、日志、快照、脚本、指标内容与实际执行命令均保留。当前产物/日志/指标路径更新；历史脚本中的旧绝对路径为执行时记录，不可直接重跑。映射与完整性记录：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/directory_migration_20261015.json。
- 命令：python /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/analyze.py
- 代码版本：7bb09c762b4e6030fe870b34f9c1a119d7c81425
- 随机种子：11451
- 日志：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/logs/run.log
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/outputs
- 指标文件：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json

## 结果
75步固定4800rollout/1200G4离线扫描exit0，0.1/.2/.3/.5：100mixed组等权多框胜率46/51.9167/54.3333/61.5%，mean差-.033854/+.053146/+.140146/+.314146；422正多框正adv232/242/253/266（54.976/57.346/59.953/63.033%）。首框>=.5的240条多框减首框单框mean-.374264/-.274264/-.174264/+.025736。正确Selected219中正adv169/176/181/191，有正确候选却选错154中正adv38/39/44/45；73步2条到.5仍负adv-.93415、reward1.5低于首框1.667/1.552。1041无资格+59全资格组优势不变，只有100组有资格差异。0.5是新训练候选，非已验证最优/性能或多框率提升；当前训练参数不变，未新训练/重放/测试/评测。

### 辅助指标
```json
[
  {
    "metric_id": "mixed_win_rate_bonus_0_1",
    "value": 0.4599999999999999,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  },
  {
    "metric_id": "mixed_win_rate_bonus_0_2",
    "value": 0.5191666666666666,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  },
  {
    "metric_id": "mixed_win_rate_bonus_0_3",
    "value": 0.5433333333333333,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  },
  {
    "metric_id": "mixed_win_rate_bonus_0_5",
    "value": 0.615,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  },
  {
    "metric_id": "positive_multibox_positive_adv_bonus_0_1",
    "value": 232,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  },
  {
    "metric_id": "positive_multibox_positive_adv_bonus_0_2",
    "value": 242,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  },
  {
    "metric_id": "positive_multibox_positive_adv_bonus_0_3",
    "value": 253,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  },
  {
    "metric_id": "positive_multibox_positive_adv_bonus_0_5",
    "value": 266,
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/metrics.json"
  }
]
```

### 分析
# E-014 额外多框补偿离线扫描

Run：`e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep`。用户授权单次离线扫描0.1/0.2/0.3/0.5。受管执行exit0/complete，科研结果仍为analysis_pending，未升级Claim。

## 数据与计算边界

- 只复用显式诊断Run `e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis` 的不可变75步source_snapshot和467条counterfactual_rows；4800生成/1200完整G4组，合法多框467，其中正样本422。
- 固定所有bbox/score/标签/IoU/选框及其他奖励，条件探索仍0.6、beta0。只改合法正样本distinct多框一次bonus：`R_new=R_old+(lambda-0.1)*eligible`。非法仍-1，负样本不变。
- 每个真实同Query/rank/update G4组按总体std+1e-6重算诊断advantage；float64近似原float32，baseline多框正负符号核验一致（0差异），全组最大数值差0.00372。
- mixed严格胜率先在组内multi×single计算，再对100个mixed组等权平均；负样本mixed也保留，不能混为仅正样本。正多框adv分母422；首框准确反事实分母240。
- 没有重新采样或训练，IoU和多框数量保持不变，扫描不能预测未来输出比例或模型性能。

## 扫描结果

| 额外补偿 | mixed组多框严格胜率 | mean(multi)-mean(single) | 正样本多框正adv | 首框IoU>=0.5时多框减只留首框mean |
|---|---:|---:|---:|---:|
| 0.1 | 46.00% | -0.03385 | 232/422（54.98%） | -0.37426 |
| 0.2 | 51.92% | +0.05315 | 242/422（57.35%） | -0.27426 |
| 0.3 | 54.33% | +0.14015 | 253/422（59.95%） | -0.17426 |
| 0.5 | 61.50% | +0.31415 | 266/422（63.03%） | +0.02574 |

0.2令总体mixed均值与胜率刚转为有利于多框；0.3增强但首框已准确时追加收益均值仍-0.17426；0.5令该条件的自身反事实均值转为+0.02574（145胜/95负），并把mixed胜率提高到61.5%。

仅collage的76个mixed组，四个权重胜率48.79%/55.70%/58.11%/67.11%；original正的11个mixed组为47.73%/53.79%/59.09%/62.12%。原负13个mixed组各扫描均28.21%，没有获得补偿。

## 是否削弱错误选框约束

“选框正确”=SelectedIoU>=0.5（219条）；“候选有正确框却选错”=OracleIoU>=0.5且SelectedIoU<0.5（154条）。这些条件只是诊断，不改变实际选择。

| 补偿 | 选框正确的正adv | 有正确候选却选错的正adv | 相对0.1新增正adv的正多框 |
|---|---:|---:|---:|
| 0.1 | 169/219 | 38/154 | 0 |
| 0.2 | 176/219 | 39/154 | 10 |
| 0.3 | 181/219 | 44/154 | 21 |
| 0.5 | 191/219 | 45/154 | 34 |

从0.1到0.5：正确选择的正adv增加22条，错误选择的正adv增加7条，其他尚未达到正确定位的回答增加5条。更强bonus增强多框信号，同时会使部分错误选框回答也转正；不能说所有错误仍为负或没有风险。

第73步两条错误选择，在0.5时reward=1.5，仍低于首框单框1.66730/1.55232，假设同组adv均-0.93415，仍受约束。它们相对首框的损失为0.16730/0.05232。

## 探索稀疏的限制

1200组中1041组没有bonus资格候选，59组四条全部有资格；这1100组（91.67%）共同平移或完全不变，优势不变。只有100组有不同bonus资格，系数提高才有机会改变组内相对信号。40–75步只有一个含多框mixed组（73步两条）；四个系数均未将这两条变为正adv。

因此0.5是有依据的下一轮单变量候选，但不是已验证最优值。当前缺少多框采样的阶段，离线调大系数不能凭空制造多框轨迹；是否维持多框仍需新训练或继续概率分析。本任务只扫描，当前训练配置仍为额外补偿0.1，未启动新训练。

## 审阅与复现

4800行/1200G4及467CF逐条匹配通过；非法/负样本reward不变、无资格组与全资格组adv不变通过，SHA保存。分析脚本SHA256：`a1972fe11074f88cc289def7b692365f8b420d8883e71a9538555f749eacd5e3`；训练源码SHA为7bb09c762b4e6030fe870b34f9c1a119d7c81425。本次没有代码仓库修改或新代码审阅，未测试/模型重放/评测；实际离线分析已执行并核验。

本地analysis.json/integrity_audit.json/report.md；远端独立Run保留source_snapshot、sweep_rollouts.jsonl（19200条，含四个权重）、sweep_groups.jsonl（4800条）、脚本和metrics。没有读取新live日志或持续监控。


### 局限
float64诊断adv近似日志float32；有选错框轨迹随补偿增大转正，采样缺多框的组不会凭空获得多框信号。未测试/模型重放/评测/新训练，不持续监控。

### 结论范围
固定0.1 policy已有轨迹离线重算，单seed，其他奖励/score/IoU和回答不变，不是重训效果或已验证最优；保持当前训练和Claim不变。

### Claim 边界
新奖励未验证；多框比例本身不构成成功；不改Claim、不覆盖历史产物、不自动重跑。

### 产物索引
.pi/analysis/e014/e014-multibox-bonus-sweep/analysis.json
.pi/analysis/e014/e014-multibox-bonus-sweep/integrity_audit.json
.pi/analysis/e014/e014-multibox-bonus-sweep/report.md
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/sweep_rollouts.jsonl
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/sweep_groups.jsonl
/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-014/analysis/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep/analyze.py

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
