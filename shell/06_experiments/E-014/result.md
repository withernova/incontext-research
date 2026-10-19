# E-014 · 实验结果

> 记录截至：2026-10-19T14:06:09。记录更新不等于实际运行完成；程序完成也不等于科研结论成立。

## 结果摘要（survey-tool 管理）
（Experiment 级摘要待登记；以下保留已登记 Run 的结果。）

## 对 Claims 的影响（survey-tool 管理）
（待人工判断；不会自动提升 Claim）

## 局限性（survey-tool 管理）
（待补充）

## 运行汇总（survey-tool 管理）

### 历史未分组 (`legacy`)

| Run / 名称 | Seed | 当前状态 | 最近记录更新 | 已登记数值 |
|---|---|---|---|---|
| [e014-variable-symmetric-sft659-puregrpo-seed11451](runs/e014-variable-symmetric-sft659-puregrpo-seed11451.md) · SFT659 变长候选与双向对称数据纯 GRPO | 11451 | failed | 2026-10-12T11:12:33 | 尚无已登记数值；不表示没有产物 |
| [e014-step800-variable-candidates-eval1766-8gpu](runs/e014-step800-variable-candidates-eval1766-8gpu.md) · step800原1766样本八卡变长候选评测 | 20260901 | analysis_pending | 2026-10-12T12:53:53 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-v2-symmetric-sft659-puregrpo-seed11451](runs/e014-multi-v2-symmetric-sft659-puregrpo-seed11451.md) · multi_v2多实例枚举、两行模板、原SFT659独立纯GRPO | 11451 | failed | 2026-10-12T16:14:13 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-v2-step200-eval1766-8gpu](runs/e014-multi-v2-step200-eval1766-8gpu.md) · multi_v2本分支step200、原1766样本八卡评测 | 20260901 | analysis_pending | 2026-10-12T16:56:41 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451](runs/e014-multi-v2-cover-min-cap5-sft659-puregrpo-seed11451.md) · multi_v2 / min实例覆盖 / soft预算5 / 同组奖励诊断 / freshSFT659纯GRPO | 11451 | failed | 2026-10-12T20:47:30 | 尚无已登记数值；不表示没有产物 |
| [e014-cover-min-cap5-step150-eval1766-8gpu](runs/e014-cover-min-cap5-step150-eval1766-8gpu.md) · 最新min覆盖/cap5分支step150、multi_v2、原1766八卡评测 | 20260901 | failed | 2026-10-13T19:01:47 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451](runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451.md) · 用户要求发布部署后立即启动本次已实现的0.2多框奖励独立训练。以已发布部署的69f786a3db89177cea11178714f560ce5760d36c为准 | 11451 | failed | 2026-10-13T19:36:00 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2](runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2.md) · 多框补偿独立训练（修正日志位置） | 11451 | approved | 2026-10-13T23:34:27.083208 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001](runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001.md) · 对 step150 的 ckpt 进行评测一下 | 11451 | analysis_pending | 2026-10-14T00:37:56 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-bonus02-g8-sft659-seed11451](runs/e014-multi-bonus02-g8-sft659-seed11451.md) · 用户选方案1并要求重新训练及约400步自动评测：新独立训练从原SFT659 fresh policy+固定anchor，纯GRPO；仅settings.trai | 11451 | failed | 2026-10-14T09:07:05 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-bonus02-g8-step400-eval1766](runs/e014-multi-bonus02-g8-step400-eval1766.md) · 用户追加要求新G=8训练约400step时自动评测400step。此独立评测仅在父训练保存payload/grpo/checkpoints/step_00040 | 11451 | approved | 2026-10-14T08:29:22 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-bonus02-g8-step150-eval1766](runs/e014-multi-bonus02-g8-step150-eval1766.md) · 用户要求现在停止G8训练并开始评测，不再等400。训练已按授权停止，8rank实际完成154更新；最新完整保存checkpoint为本父Run payload/ | 11451 | failed | 2026-10-14T08:29:22 | 尚无已登记数值；不表示没有产物 |
| [e014-multi-bonus02-g8-step150-eval1766-r2](runs/e014-multi-bonus02-g8-step150-eval1766-r2.md) · 用户明确要求“修正然后评测”，授权修正前次output_dir布局错误后一次新评测。保留失败父Run全部产物，新Run根级outputs为canonical o | 11451 | analysis_pending | 2026-10-14T09:06:45 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-sft659-seed11451.md) · 三项奖励与条件探索训练 | 11451 | failed | 2026-10-14T14:15:33 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-current-multibox-analysis.md) · 我想知道目前的多框目测是否带来了更好的结果呢：只分析父训练当前已有rollout，按完成更新及同prompt组比较单框与多框Selected/Oracle Io | 11451 | analysis_pending | 2026-10-15T08:59:26 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-current-multibox-analysis-r2](runs/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2.md) · 继续完成用户当前多框是否带来更好结果的分析：首次分析逐行JSON解析漏掉拼接rank完成日志；以已保存的同一固定快照重新解析，8rank完整1..68已核验。保 | 11451 | analysis_pending | 2026-10-15T08:59:26 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-latest-training-analysis](runs/e014-structure-score-iou-explore-v1-latest-training-analysis.md) · 现在看看截止目前的训练结果呢：只读取本父训练最新完成更新、checkpoint及rollout快照，分析奖励/置信度/定位/多框趋势；不停止训练，不执行chec | 11451 | analysis_pending | 2026-10-15T08:59:26 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-step150-eval1766](runs/e014-structure-score-iou-explore-v1-step150-eval1766.md) · 现在停止训练，然后开始150step的评测eval：训练已按请求停止在154，评测本父Run保存step150（不是其他奖励训练checkpoint）；原176 | 20260901 | analysis_pending | 2026-10-14T15:39:13 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis](runs/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis.md) · 根据目前训练结果分析为什么多框逐渐消失：只用父训练保存日志1..150，检查同prompt组奖励/advantage、探索扣分触发与组内差异、raw多框非法及t | 11451 | analysis_pending | 2026-10-15T08:59:26 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451.md) · 你可以试着关闭KL散度吗，将settings.trainer.beta=0.0：按用户要求执行独立fresh SFT659训练变体，只改beta .04→0，沿 | 11451 | failed | 2026-10-14T16:34:40 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis.md) · 现在我想知道会不会多框输出的情景会更多了呢：只分析KL=0父训练已完成更新的现有日志，按相同早期更新窗口统计合法/raw多框、正负与拼图分层、advantage | 11451 | failed | 2026-10-15T08:59:26 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2](runs/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2.md) · 继续完成用户当前问题：现在多框输出是否更多。首次只读分析因min参数类型错误没有形成结果，保留失败目录；独立修正版只读比较beta0与本会话显式引用beta.0 | 11451 | analysis_pending | 2026-10-15T08:59:26 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-step50-eval1766](runs/e014-structure-score-iou-explore-v1-beta0-step50-eval1766.md) · 刚刚的训练帮我停止，然后对step50的结果进行一个评测吧：停止当前KL=0新奖励父训练，独立评测其保存step50，原1766样本/8GPU/multi_v2 | 20260901 | analysis_pending | 2026-10-14T16:58:21 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-beta0-explore06-sft659-seed11451.md) · 改好了就直接运行吧，也不要过多去监控：用户授权独立fresh SFT659训练，保持beta=0，只将条件探索扣分从0.2改到0.6。低Selected IoU | 11451 | failed | 2026-10-14T19:32:46 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis.md) · 那根据目前的已训练的，多框比例怎么样：一次性只读当前beta0/探索.6父训练已完成更新，核验8rank共同连续完成日志、G4组和真实配置，统计合法/raw多框 | 11451 | analysis_pending | 2026-10-15T08:59:27 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451.md) · 用户要求完成修改审阅后运行，并授权停止上一轮。独立fresh原SFT659训练：保持新奖励、beta0、低SelectedIoU探索扣分.6、G4/seed11 | 11451 | failed | 2026-10-14T23:57:30 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis.md) · 用户问现在结果、多框是否改善。只读当前beta0/探索.6/补偿.1训练固定日志快照，核验8rank共同完成更新、G4和实际奖励，统计合法/raw多框及最近20 | 11451 | analysis_pending | 2026-10-15T08:59:27 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis.md) · 用户问现在结果、多框是否又消失。仅当前beta0/.6探索/.1补偿训练一次固定快照，核验8rank共同连续完成更新及G4组、实际配置和奖励重算；报告合法/ra | 11451 | analysis_pending | 2026-10-15T08:59:27 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis.md) · 用户同意检查多框消失前两层。仅用显式既有75步分析Run e014-structure-score-iou-explore-v1-beta0-explore06 | 11451 | analysis_pending | 2026-10-15T08:59:27 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep](runs/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep.md) · 用户同意离线扫描额外多框补偿0.1/0.2/0.3/0.5。只用显式75步诊断Run固定source_snapshot及counterfactual_rows， | 11451 | analysis_pending | 2026-10-15T08:59:27 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451.md) · 用户要求试着开启0.5额外多框奖励。独立fresh原SFT659，beta0和低SelectedIoU条件探索.6不变，仅合法正样本distinct一次补偿由. | 11451 | failed | 2026-10-15T08:34:56 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis.md) · 用户问当前0.5训练是否再次消失。仅本父Run一次固定日志快照，核验beta0/.6条件探索/.5补偿与8rank共同完成更新/G4组和实际奖励，统计合法/ra | 11451 | analysis_pending | 2026-10-15T08:59:27 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis.md) · 用户问现在进展。只对0.5父训练一次最新固定快照，核验8rank共同连续完成更新和G4/实际reward，统计多框累计、25步窗/最近20和50步、原正负/co | 11451 | analysis_pending | 2026-10-15T08:59:27 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766.md) · 用户要求暂停当前0.5额外补偿训练并评测其step350。父训练已主动停止，8rank完成380；评测本父Run保存payload/grpo/checkpoin | 20260901 | failed | 2026-10-15T08:43:38 | 尚无已登记数值；不表示没有产物 |
| [e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2.md) · 继续完成用户已授权的暂停0.5训练并评测step350任务。首次仅目录preflight失败，无输入准备/模型加载/预测。保留失败Run全部产物。独立修正版Ru | 20260901 | analysis_pending | 2026-10-15T09:23:21 | 尚无已登记数值；不表示没有产物 |
| [e014-boxes-then-scores-beta0-sft659-seed11451](runs/e014-boxes-then-scores-beta0-sft659-seed11451.md) · 用户明确授权修改完成后训练且关闭KL；在新协议step0评测完成后，从原单框SFT659全新启动统一GRPO。boxes_then_scores_v1；beta | 11451 | failed | 2026-10-15T15:14:21 | 尚无已登记数值；不表示没有产物 |
| [e014-boxes-then-scores-sft659-step0-eval1766](runs/e014-boxes-then-scores-sft659-step0-eval1766.md) · 用户授权新协议先全部bbox后全部score；对原SFT659做新协议step0既有1766评测，作为随后新GRPO训练基线。使用新配置和实际EOS完整回答校验 | 20260901 | analysis_pending | 2026-10-15T12:25:25 | 尚无已登记数值；不表示没有产物 |
| [e014-boxes-then-scores-beta0-step150-eval1766](runs/e014-boxes-then-scores-beta0-step150-eval1766.md) · 用户要求停止本次训练并评测step150。独立1766评测，boxes_then_scores_v1、require_eos、greedy192、vision4 | 20260901 | analysis_pending | 2026-10-15T17:20:18 | 尚无已登记数值；不表示没有产物 |
| [e014-boxes-then-scores-collapse-analysis](runs/e014-boxes-then-scores-collapse-analysis.md) · 用户要求分析新协议多框为何消失。对已停止的184步rollout做一次CPU离线诊断：分阶段合法/原始多框、长度/截断、同prompt组优势、奖励分解和固定候选 | 11451 | analysis_pending | 2026-10-15T16:02:45 | 尚无已登记数值；不表示没有产物 |
| [e014-discovery-priority-score04-beta0-sft659-200step-seed11451](runs/e014-discovery-priority-score04-beta0-sft659-200step-seed11451.md) · 用户批准新的统一标量奖励：H+OracleIoU+.5双实例min覆盖+.2SelectedIoU+.4(1-max score误差)-.05近重复-.05逆序 | 11451 | analysis_pending | 2026-10-15T23:28:56 | 尚无已登记数值；不表示没有产物 |
| [e014-discovery-score04-step200-eval1766-20261015T152856Z](runs/e014-discovery-score04-step200-eval1766-20261015T152856Z.md) · 用户要求整理训练目录后评测本次发现优先score.4的step200。训练已正常完成200且真实目录改为含启动时间和奖励描述的新名，旧路径兼容。独立1766评测 | 20260901 | analysis_pending | 2026-10-16T00:12:07 | 尚无已登记数值；不表示没有产物 |
| [e014-discovery-score04-step150-eval1766-20261015T161128Z](runs/e014-discovery-score04-step150-eval1766-20261015T161128Z.md) · 用户要求：再评测同一轮discovery-priority score0.4 beta0训练的step150，与step200比较训练是否改善。使用同一1766 | 20260901 | analysis_pending | 2026-10-16T00:37:26 | 尚无已登记数值；不表示没有产物 |
| [e014-step150-vs200-paired-analysis-20261016](runs/e014-step150-vs200-paired-analysis-20261016.md) · 用户要求分析step150结果为何与预期不同；离线比较同轮step200的1766条prediction，分解候选质量和score选择，不重新推理。 | 20260901 | approved | 2026-10-16T00:37:49 | 尚无已登记数值；不表示没有产物 |
| [e014-reward-order-simulation-20261016](runs/e014-reward-order-simulation-20261016.md) · 用户要求编写并执行纯合成离线奖励模拟，比较讨论中的硬档位与较平滑方案，穷举单/双候选网格、十五种行为示例和阈值反例；不读训练产物、不修改训练奖励、不训练。 | 11451 | approved | 2026-10-16T01:02:25 | 尚无已登记数值；不表示没有产物 |
| [e014-reward-constraint-solver-20261016](runs/e014-reward-constraint-solver-20261016.md) · 用户授权继续完成奖励自动求解：本地合成约束求解、反例迭代与G=4优势模拟。继承现有未提交模拟程序继续开发，不读取训练产物，不部署或训练。 | 11451 | approved | 2026-10-16T01:20:06 | 尚无已登记数值；不表示没有产物 |
| [e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451](runs/e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451.md) · 用户授权：使用自动求解的hard_tier五档奖励，从原SFT659重新训练400step，GRPO同prompt组大小8，beta=0。沿用先框后分协议、既有 | 11451 | failed | 2026-10-16T08:53:28 | 尚无已登记数值；不表示没有产物 |
| [e014-tier-g8-onecheck-20261015T183221Z](runs/e014-tier-g8-onecheck-20261015T183221Z.md) · 用户授权一小时后仅检查一次多框是否消失及定位、评分、非法输出诊断；不重复监控。当前已为硬分档，原硬分档替代参数尚未确认；发现问题先记录原因及优化建议。 | 11451 | approved | 2026-10-16T02:32:23 | 尚无已登记数值；不表示没有产物 |
| [e014-tier065-g8-step200-eval1766-20261016T002327Z](runs/e014-tier065-g8-step200-eval1766-20261016T002327Z.md) · 评测当前tier065/G8/KL0训练step200 checkpoint，沿用1766固定评测集、boxes_then_scores_v1、greedy19 | 20260901 | analysis_pending | 2026-10-16T09:16:57 | 尚无已登记数值；不表示没有产物 |
| [e014-tier065-g8-step150-eval1766-20261016T011613Z](runs/e014-tier065-g8-step150-eval1766-20261016T011613Z.md) · 用户要求评测同一训练step150，与step200相同1766固定清单、boxes_then_scores_v1、greedy192、seed20260901 | 20260901 | analysis_pending | 2026-10-16T09:43:39 | 尚无已登记数值；不表示没有产物 |
| [e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451](runs/e014-20261016T014300Z-discovery-score05-g8-kl0-sft659-400step-seed11451.md) · 用户确认回退至发现优先奖励，score_weight .4→.5；fresh SFT659、400step、G8、KL0，其余奖励和数据保持；独立Run，保留所 | 11451 | failed | 2026-10-16T20:41:12 | 尚无已登记数值；不表示没有产物 |
| [e014-score05-multibox-check-20261016T045945Z](runs/e014-score05-multibox-check-20261016T045945Z.md) · 用户询问当前训练是否存在多框问题；仅一次日志快照，分完整步窗口分析多框、合法率、候选增益和选择差距，不修改训练。 | 11451 | approved | 2026-10-16T13:01:09 | 尚无已登记数值；不表示没有产物 |
| [e014-score04-step150-200-visual-20261016T060926Z](runs/e014-score04-step150-200-visual-20261016T060926Z.md) · 离线可视化score0.4的step150与step200评测；显式比较e014-discovery-score04-step150-eval1766-2026 | 20260901 | approved | 2026-10-16T14:12:59 | 尚无已登记数值；不表示没有产物 |
| [e014-score05-gap-check-20261016T064643Z](runs/e014-score05-gap-check-20261016T064643Z.md) · 用户查询当前训练多框率与Oracle-Selected gap；单次只读快照，最近20完整步按原图/拼图报告，不修改训练。 | 11451 | approved | 2026-10-16T14:46:52 | 尚无已登记数值；不表示没有产物 |
| [e014-score05-step100-check-20261016T074036Z](runs/e014-score05-step100-check-20261016T074036Z.md) · 用户查询约100步的变化；一次只读训练快照，核实完整rollout步和step100保存，按原图/拼图分析多框与Oracle gap，不修改训练。 | 11451 | approved | 2026-10-16T15:41:17 | 尚无已登记数值；不表示没有产物 |
| [e014-score05-progress-20261016T103959Z](runs/e014-score05-progress-20261016T103959Z.md) · 用户要求读取当前训练结果；单次只读快照核对实际coverage配置、保存checkpoint、多框和Oracle gap；不改权重、不持续监控。 | 11451 | approved | 2026-10-16T18:40:39 | 尚无已登记数值；不表示没有产物 |
| [e014-score05-progress-20261016T123919Z](runs/e014-score05-progress-20261016T123919Z.md) · 用户查询最新变化；一次只读快照统计最近20完整rollout步多框率和Oracle gap、核验配置及checkpoint，不改训练。 | 11451 | approved | 2026-10-16T20:39:48 | 尚无已登记数值；不表示没有产物 |
| [e014-discovery-score05-g8-step200-eval1766-20261016T124126Z](runs/e014-discovery-score05-g8-step200-eval1766-20261016T124126Z.md) · 用户暂停训练并评测step200；固定1766/boxes_then_scores_v1/greedy192/seed20260901。评测结束后从step20 | 20260901 | analysis_pending | 2026-10-16T21:05:29 | 尚无已登记数值；不表示没有产物 |
| [e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150](runs/e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150.md) · 用户明确评测后从已保存step200恢复policy和optimizer继续到累计400，coverage .5/score .5/G8/KL0不变；每150累 | 11451 | analysis_pending | 2026-10-17T13:17:31 | 尚无已登记数值；不表示没有产物 |
| [e014-resume-multibox-20261016T165703Z](runs/e014-resume-multibox-20261016T165703Z.md) · 读取续训最新完整窗口、多框率与Oracle gap，核验step300周期评测是否生成；不改训练。 | 11451 | approved | 2026-10-17T00:59:13 | 尚无已登记数值；不表示没有产物 |
| [e014-resume-progress-20261017T022724Z](runs/e014-resume-progress-20261017T022724Z.md) · 用户查询当前进展；单次只读续训窗口和step300自动评测，不改训练。 | 11451 | approved | 2026-10-17T10:27:25.459409 | 尚无已登记数值；不表示没有产物 |
| [e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150-derived-001](runs/e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150-derived-001.md) · 用户明确要求将当前从200续训到400的训练继续扩展，一直训练到累计1500 iter（不是额外1500）。从当前Run实际完整step400 checkpoi | 11451 | failed | 2026-10-18T10:44:26 | 尚无已登记数值；不表示没有产物 |
| [e014-score04-step200-native-vqa1766-20261018](runs/e014-score04-step200-native-vqa1766-20261018.md) · 用户授权暂停当前训练后直接在原1766测试集做零训练VQA候选选择。固定历史score0.4/G4/step200已保存候选（Oracle最高），仅对791多框 | 20260901 | analysis_pending | 2026-10-18T11:23:46 | 尚无已登记数值；不表示没有产物 |
| [e014-score04-step200-native-vqa-exact1766-20261018](runs/e014-score04-step200-native-vqa-exact1766-20261018.md) · 用户要求在上一版VQA提示词中强调Reference同一个体exactly出现在Query中，然后重测。只变prompt_variant=exact_insta | 20260901 | analysis_pending | 2026-10-18T11:49:10 | 尚无已登记数值；不表示没有产物 |
| [e014-score04-step200-native-vqa-drawn1766-20261018](runs/e014-score04-step200-native-vqa-drawn1766-20261018.md) · 用户授权编写代码运行画框VQA。保持原始Qwen3-VL-8B-Instruct无adapter BF16/SDPA、冻结历史score0.4/G4/step2 | 20260901 | analysis_pending | 2026-10-18T12:15:17 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-sft-data-step200-20261018](runs/e014-selection-sft-data-step200-20261018.md) · 用户授权独立画框选择LoRA训练的必要数据阶段：从现有2000正训练对排除与1766评测集同身份/原视频来源（只读审计59）后约1941，以原视频/序列seed | 20260901 | analysis_pending | 2026-10-18T13:20:19 | 尚无已登记数值；不表示没有产物 |
| [e014-drawn-selection-lora-sft1epoch-20261018](runs/e014-drawn-selection-lora-sft1epoch-20261018.md) · 用户已授权独立选择LoRA训练。本训练Run只在数据父Run成功且train/validation分组、候选及渲染/标签哈希验收后启动。原始Qwen3-VL-8 | 20260901 | failed | 2026-10-18T14:51:00 | 尚无已登记数值；不表示没有产物 |
| [e014-drawn-selection-lora-sft1epoch-20261018-r2](runs/e014-drawn-selection-lora-sft1epoch-20261018-r2.md) · 用户明确要求修正后直接运行。修复空localization_iou_thresholds与基类校验不兼容，使用53ab7653602f62ffc1d5c9dad | 20260901 | failed | 2026-10-18T16:42:26 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-lora-step72-validation334-20261018](runs/e014-selection-lora-step72-validation334-20261018.md) · 用户同意评测训练后的独立选择LoRA。按刚才建议仅做内部验证集334例（123多候选）评测，使用r2最终step72 adapter及已验收数据Run的vali | 20260901 | analysis_pending | 2026-10-18T18:11:18 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-lora-step72-test1766-20261018](runs/e014-selection-lora-step72-test1766-20261018.md) · 用户要求开始1700集完整评测，即此前1766例冻结测试集。评测最终step72独立选择LoRA；使用历史score04-step200最高已记录Oracle候 | 20260901 | analysis_pending | 2026-10-18T18:39:33 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-lora-resume72-total5epochs-20261018](runs/e014-selection-lora-resume72-total5epochs-20261018.md) · 用户明确要求有Oracle提升空间则累计训练5epoch。已有1766结果LoRA69.9607% vs Oracle75.7399%，多框62.9412% v | 20260901 | failed | 2026-10-18T20:08:34 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-lora-step360-test1766-20261018](runs/e014-selection-lora-step360-test1766-20261018.md) · 用户要求现在评测已完成累计5epoch的step360选择LoRA。复用上一轮1766完整冻结测试集（791多框），只改变selector-checkpoint | 20260901 | analysis_pending | 2026-10-18T21:41:20 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-fulltrain-step200-gtaugment-20261018](runs/e014-selection-fulltrain-step200-gtaugment-20261018.md) · 用户明确授权启动完整训练集的固定候选生成LoRA推理及选择数据构造，不训练选择器。采用E009完整有效10522正例清单（原10534排除12无效框），包括GO | 20260901 | analysis_pending | 2026-10-19T01:12:40 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-fulltrain-gt-lora5epoch-20261019](runs/e014-selection-fulltrain-gt-lora5epoch-20261019.md) · 用户明确授权完成数据后自动启动5epoch训练且不走Steward。现在启动一个受管串行任务：只读inotify等待已在运行的渲染exit0，不重复渲染；核增强 | 20260901 | failed | 2026-10-19T08:14:14 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-fulltrain-step2095-test1766-20261019](runs/e014-selection-fulltrain-step2095-test1766-20261019.md) · 用户要求暂停当前训练，用最后完整checkpoint评测全部1766。训练已SIGINT退出释放GPU，固定samples_00033516_step_0020 | 20260901 | analysis_pending | 2026-10-19T08:28:53 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-coordinates-only-lora4epoch-20261019](runs/e014-selection-coordinates-only-lora4epoch-20261019.md) · 用户明确授权训练4epoch无画框版本：原始Reference/Query图像+文字Reference bbox及候选bbox列表，无任何叠加框或视觉编号，候选 | 20260901 | failed | 2026-10-19T13:02:00 | 尚无已登记数值；不表示没有产物 |
| [e014-selection-coordinates-only-lora4epoch-20261019-derived-001](runs/e014-selection-coordinates-only-lora4epoch-20261019-derived-001.md) · 用户明确要求评测当前无框原图+文字bbox选择器的step1310 checkpoint。固定原1766候选数据，与已有画框版本对照；使用exact_insta | 20260901 | running | 2026-10-19T14:06:09 | 尚无已登记数值；不表示没有产物 |

## 指标观测（survey-tool 管理）

> 关键结果与指标观测分别保留，不混合计算。辅助指标不自动成为主指标；结论仍需人工判断。

<details><summary>e014-step800-variable-candidates-eval1766-8gpu · 结果、来源与解释</summary>

- Run 笔记：[e014-step800-variable-candidates-eval1766-8gpu](runs/e014-step800-variable-candidates-eval1766-8gpu.md)
- 最近记录更新：2026-10-12T12:53:53

### 本轮分析
Managed execution exited successfully with 0 declared and 43 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-multi-v2-step200-eval1766-8gpu · 结果、来源与解释</summary>

- Run 笔记：[e014-multi-v2-step200-eval1766-8gpu](runs/e014-multi-v2-step200-eval1766-8gpu.md)
- 最近记录更新：2026-10-12T16:56:41

### 本轮分析
Managed execution exited successfully with 0 declared and 43 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001 · 结果、来源与解释</summary>

- Run 笔记：[e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001](runs/e014-multi-v2-cover-min-cap5-multi-bonus02-sft659-puregrpo-seed11451-r2-derived-001.md)
- 最近记录更新：2026-10-14T00:37:56

### 本轮分析
评测exit0，1766条indices和unique IDs完整；源SHA及实际prompt核验通过。Selected=First mIoU0.7018657614736732，Oracle0.7126411223176852，IoU>=.5为1349/1766。候选数1/2/3/4分别1652/104/7/3，多框114/1766。全部选首框：多框中64条首框score严格最高，50条首框并列最高。25条后续候选IoU更高，其中23条可将IoU<.5提升至>=.5，但score选择均未利用。多框子集Selected/Oracle mIoU=.6566238435459423/.8235474159189673；空间顺序合法79/114，6/114含近重复。

### 本轮局限
单checkpoint、单训练seed、已看测试集；未做同预算无补偿配对对照，不能归因0.2奖励或证明总体性能提升。Oracle只用GT事后选框。多框子集是模型自选子集，不能与单框组直接作因果比较。继承的训练mixed组胜率不是此次greedy评测指标；本轮不提升Claim。

</details>

<details><summary>e014-multi-bonus02-g8-sft659-seed11451 · 结果、来源与解释</summary>

- Run 笔记：[e014-multi-bonus02-g8-sft659-seed11451](runs/e014-multi-bonus02-g8-sft659-seed11451.md)
- 最近记录更新：2026-10-14T09:07:05

### 本轮分析
复用原日志逐组核对2400group及24已完成窗口；只取rollout.step0..149，排除151..154共512条。全程mixed462组/4818对；主指标组等权严格胜率q=.473704，ties=.089341，pooled=.475509，mean multi-single差+.052170；original正/负/collage分层q=.274555/.136618/.689450。multi正adv4694/8015。全分母及窗口/score奖励诊断见shell/06_experiments/E-014/visualizations/g8-step150-20261014/report.md和training_audit.json。不同条件差异明显，不支持统一整体探索坍缩说法；不作因果或Claim升级。训练仍暂停，不声称1500完成或自动恢复。

</details>

<details><summary>e014-multi-bonus02-g8-step150-eval1766 · 结果、来源与解释</summary>

- Run 笔记：[e014-multi-bonus02-g8-step150-eval1766](runs/e014-multi-bonus02-g8-step150-eval1766.md)
- 最近记录更新：2026-10-14T08:29:22

### 本轮分析
前置检查失败，exit1，没有模型加载、预测或评测结果。训练已按用户要求停止154，最新可评测checkpoint150。

### 本轮局限
父训练实际154但只评测保存step150；151..154未保存，不进入该checkpoint训练诊断；取消step400等待。训练保持暂停。

</details>

<details><summary>e014-multi-bonus02-g8-step150-eval1766-r2 · 结果、来源与解释</summary>

- Run 笔记：[e014-multi-bonus02-g8-step150-eval1766-r2](runs/e014-multi-bonus02-g8-step150-eval1766-r2.md)
- 最近记录更新：2026-10-14T09:06:45

### 本轮分析
# G8 step150：1766样本评测与训练日志诊断

## 结论

- 本次评测已完成。退出码0，1766条输出覆盖完整，来源哈希及实际配置通过核验。受管 complete 于2026-10-14 09:03:18成功。
- 分数选择开始产生实际收益：Selected mIoU为70.243%，First为69.775%，差值为+0.468个百分点。但Oracle为71.526%，仍有1.284个百分点的选择差距。
- 不能把本次训练描述为“多框整体持续消失”。训练collage多框率由54.82%升至89.89%；原始正、负输入的多框率下降。必须按输入条件区分。
- 这是单seed、已查看测试集上的诊断。没有因果结论，也没有Claim升级。

## 执行与完整性

- Run：`e014-multi-bonus02-g8-step150-eval1766-r2`。
- 来源训练：`e014-multi-bonus02-g8-sft659-seed11451`。
- 来源checkpoint：`payload/grpo/checkpoints/step_000150`。先前已读取`optimizer.steps=150`。
- 训练8个rank实际完成154更新，随后按用户要求停止。151–154未保存为本评测checkpoint，也不进入本报告的训练诊断。
- 部署及实际快照SHA：`26e35eee07dfc1d6274b594005b984d647822017`；代码审阅：`9b229d52a506b1e7`。
- 配置：`configs/experiments/E-014/evaluation/e014_multi_bonus02_g8_step150_eval1766_r2.py`；复用现有`explicit_binding` Shell及`tools/evaluate.py`。
- 本次修正只涉及新Run输出身份。canonical输出目录为根级`outputs`，日志为根级`managed_console.log`。实际worker产物为`payload/evaluation`。失败旧Run未覆盖。
- 实际评测：8rank、greedy、192 new tokens、vision4096、seed20260901、multi_v2。顶层继承的11451是训练seed。
- 原1766=LaSOT600/GOT10k180/TAO986。只变更image_path别名，其余manifest字段逐条相等。
- 1766个唯一ID，dataset_index恰为0–1765。rank0–5各221条，rank6–7各220条。
- 5个只读来源哈希全部重新核验：原manifest、adapter配置、adapter权重、optimizer、训练配置快照。派生manifest及实际prompt哈希也一致。
- 指标稳定观测：09:00:50至09:03:17，9226 bytes及mtime相同。首次complete因稳定观测不足被拒绝；没有重跑评测，后续complete成功。
- 最终无GPU compute进程；训练退出码254对应用户停止。旧失败Run保留，step400评测目录不存在。训练不恢复。
- 源文件只读复制索引及SHA见`source_hashes.json`；实际核验见`integrity_audit.json`。原日志、checkpoint与结果未修改。

## 评测指标

Selected=最高score，并列取首。Oracle=GT事后最佳候选，不是可部署选择。全量指标分母1766，非法输出按现有评测器记IoU=0。

| 指标 | First | Selected | Oracle |
|---|---:|---:|---:|
| mIoU | 0.697745657 | 0.702426486 | 0.715262965 |
| IoU≥0.25 | 1405/1766 | 1413/1766 | 1438/1766 |
| IoU≥0.50 | 1339/1766 | 1348/1766 | 1374/1766 |
| IoU≥0.75 | 1180/1766 | 1191/1766 | 1212/1766 |

合法率：1765/1766（99.943%）。解析后的候选数0/1/2/3/4分别为1/1677/79/7/2。

原始文本中的完整answer-score对数1/2/3/4/6分别为1677/79/7/2/1。唯一非法样本为LaSOT index446：含6个完整对，随后第7个answer未闭合。不能把解析后的候选数0解释为原始模型没有输出框。未改生成预算、未重新推理该样本。

| 子集 | n | First mIoU | Selected mIoU | Oracle mIoU |
|---|---:|---:|---:|---:|
| LaSOT | 600 | 0.651586378 | 0.650123029 | 0.667373634 |
| GOT10k | 180 | 0.799870053 | 0.809232995 | 0.812336498 |
| TAO | 986 | 0.707191069 | 0.714756001 | 0.726683211 |
| 合法多候选 | 88 | 0.483127255 | 0.577062981 | 0.834667777 |

总平均收益不表示每个数据集都有收益：LaSOT的Selected低于First。

### 多候选评分诊断

- 合法多候选：88/1766（4.983%）。选择非首候选24/1766，亦为24/88。
- 这24次非首选择中，IoU比首框更高15次、更低6次、相同3次。全量Selected与First相同1745/1766。
- 多候选中，首框分数严格最高50/88，首框并列最高14/88；任意最高分并列15/88。
- 后续候选严格优于首框：38/88。Selected命中该非首Oracle为15/38。
- 多候选Selected与最早Oracle索引一致58/88；Selected达到Oracle IoU为59/88。两者差异来自IoU并列。
- 112个候选对中，16对IoU相同；其余96对中，score与IoU顺序一致54、相反24、score并列18。此处是候选对加权描述，不冒充样本等权统计。
- IoU≥0.5：Oracle相对First可挽救35个多候选样本；Selected挽救15个、损失6个，净增9个。
- 空间顺序合法75/88；近重复0/88（候选间IoU≥0.9）。全量空间顺序合法1752/1766。
- AP只是分数选定框的AP，不是完整检测AP。原始metrics同时保留valid-GT分母1756及legacy分母1766，不能互换。

完整逐项统计：`evaluation_audit.json`、`raw_candidate_audit.json`；源指标：`evaluation/metrics.json`。

## 训练日志：仅完成更新1–150

每个rank/update/sample_id为一个G8采样组。rollout.step从0开始，完成更新=step+1。仅取0–149，并与已有group记录及完成窗口交叉核验。

- 共19200 rollouts、2400组；每rank2400条/300组。每个更新每rank恰2组，每组恰8条。
- 逐组重算统计与2400条既有group记录一致；24个已完成rank窗口统计也一致。
- 排除151–154共512条rollouts。任何未完成采样组不进入统计。
- 合法多框8015/19200；非法252/19200。只在合法且终止的输出中定义single与multi。
- 总共462个mixed组，4818个multi×single比较对。

主诊断：每个mixed组先计算`q_g = sum[ R_multi > R_single ] / (n_multi*n_single)`，再对mixed组等权平均。使用实际total reward；严格大于和平局分开；不跨prompt、rank或更新配对。空分母输出null。下表的multi率分母包含非法输出。

| 完成更新 | multi/全部rollout | mixed/全部组 | q：组等权严格胜率 | 组等权平局率 | pooled严格胜率 | mean(multi)-mean(single) | multi正adv/全部multi |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1–50 | 2190/6400（34.219%） | 186/800 | 0.498768 | 0.016919 | 0.508162 | +0.022665 | 1273/2190 |
| 51–100 | 2995/6400（46.797%） | 130/800 | 0.388979 | 0.177047 | 0.377953 | +0.029865 | 1656/2995 |
| 101–150 | 2830/6400（44.219%） | 146/800 | 0.517213 | 0.103510 | 0.524310 | +0.109618 | 1765/2830 |

全1–150：q=0.473704，平局率0.089341，pooled胜率2291/4818=0.475509；组等权mean差+0.052170。best-multi严格胜best-single为250/462，并列57/462；multi正adv为4694/8015。全量multi率41.745%；合法输出内multi率8015/18948=42.300%。

### 条件分层

| 条件 | 窗口1–50 multi率 | 窗口51–100 multi率 | 窗口101–150 multi率 | 对应q序列 |
|---|---:|---:|---:|---|
| original positive | 226/1632（13.848%） | 230/1712（13.435%） | 74/1696（4.363%） | 0.335083 → 0.215476 → 0.283397 |
| original negative | 245/1632（15.012%） | 172/1712（10.047%） | 52/1696（3.066%） | 0.219220 → 0.088676 → 0.093006 |
| collage positive | 1719/3136（54.815%） | 2593/2976（87.130%） | 2704/3008（89.894%） | 0.638111 → 0.746772 → 0.721931 |

| 全1–150条件 | mixed/全部组 | 比较对 | q | 平局率 | 组等权mean差 | best严格胜/并列 | multi正adv |
|---|---:|---:|---:|---:|---:|---:|---:|
| original positive | 99/630 | 1025 | 0.274555 | 0.008899 | −0.280027 | 24/99；0/99 | 263/530 |
| original negative | 106/630 | 1071 | 0.136618 | 0.381082 | −0.086505 | 11/106；57/106 | 221/469 |
| collage positive | 257/1140 | 2722 | 0.689450 | 0 | +0.237333 | 215/257；0/257 | 4210/7016 |

完整分层、窗口、pooled/best/tie及合法分母均见`training_audit.json`。合并使用充分统计量，不平均不同大小rank的概率。

### 既有分数奖励诊断

以下是各窗口全部合法rollout的均值，包含单框；不是仅针对有ranking pair的条件均值。

| 完成更新 | 合法n | calibration_penalty | ranking_loss | distractor_penalty | order_penalty | multi_bonus | total reward | 非首选择/合法n |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1–50 | 6223 | 0.346612 | 0.034149 | 0.043641 | 0.013599 | 0.054379 | 0.246527 | 489/6223 |
| 51–100 | 6364 | 0.238042 | 0.036403 | 0.036011 | 0.007593 | 0.081050 | 0.524682 | 1029/6364 |
| 101–150 | 6361 | 0.202224 | 0.028371 | 0.024650 | 0.004657 | 0.084421 | 0.609915 | 1239/6361 |

这些数值来自原日志，不是新损失或重新计算的训练奖励。不同窗口样本和候选组成不同，因此均值变化不能单独证明评分能力的因果改善。每个条件的均值、有效分母和候选数直方图保存在JSON中。

## 解释边界与下一步

事实：本checkpoint的分数选择相对固定首框有净收益，但选择仍未利用全部候选上限。训练中，collage条件的multi奖励优势与multi率上升同时出现；原始输入的mixed组multi收益较低且multi率下降。

推断：当前证据不支持把全部现象归结为统一的“探索不足”。奖励与输入条件之间的差异需要保留。不能仅凭这些相关统计断言某项奖励导致变化，也不能断言多框数量代表有效双实例覆盖。

G8与G4在相同更新数下生成量不同（本次至150为19200 rollouts），不能视为等计算预算对照。本报告未重新评测旧G4，不以未经重新核验的旧记录作主要比较。保持训练暂停；不自动延长训练、改奖励、重跑或升级Claim。


### 本轮局限
单seed、已查看测试集；G8与G4同更新不等rollout预算。训练停154但仅评测保存150；诊断只取1..150，排除512条151..154及未完成组。mixed组选择偏差和窗口样本组成变化，相关性不等因果。43辅助指标未注册为primary，工程complete不等科学validated，无Claim升级。

</details>

<details><summary>e014-structure-score-iou-explore-v1-sft659-seed11451 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-sft659-seed11451.md)
- 最近记录更新：2026-10-14T14:15:33

### 本轮分析
用户于本次任务要求停止训练并评测step150。已受管记录主动停止并SIGTERM唯一新配置协调器；8rank最后完成154，全部自有worker已退出，8GPU各2MiB。保存step150 policy/config/optimizer存在非空，policy SHA256=2d6b64aec234746230d820e7a4b112f4d23788b036485312a8ba7b2435b24379；151..154未保存。新独立e014-structure-score-iou-explore-v1-step150-eval1766已开始。未完成1500计划，不是算法崩溃，不自动恢复父训练。

</details>

<details><summary>e014-structure-score-iou-explore-v1-current-multibox-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-current-multibox-analysis.md)
- 最近记录更新：2026-10-15T08:59:26

### 本轮分析
Managed execution exited successfully with 0 declared and 16 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-current-multibox-analysis-r2 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-current-multibox-analysis-r2](runs/e014-structure-score-iou-explore-v1-current-multibox-analysis-r2.md)
- 最近记录更新：2026-10-15T08:59:26

### 本轮分析
Managed execution exited successfully with 0 declared and 22 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-latest-training-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-latest-training-analysis](runs/e014-structure-score-iou-explore-v1-latest-training-analysis.md)
- 最近记录更新：2026-10-15T08:59:26

### 本轮分析
Managed execution exited successfully with 0 declared and 22 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-step150-eval1766 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-step150-eval1766](runs/e014-structure-score-iou-explore-v1-step150-eval1766.md)
- 最近记录更新：2026-10-14T15:39:13

### 本轮分析
Managed execution exited successfully with 0 declared and 43 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis](runs/e014-structure-score-iou-explore-v1-multibox-collapse-diagnosis.md)
- 最近记录更新：2026-10-15T08:59:26

### 本轮分析
Managed execution exited successfully with 0 declared and 26 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-sft659-seed11451 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-beta0-sft659-seed11451.md)
- 最近记录更新：2026-10-14T16:34:40

### 本轮分析
用户要求停止并评测step50；managed authorization/nonretryable记录主动停止后SIGTERM唯一output.run_name绑定beta0协调器，自有worker全退出，8rank最后52，8GPU各2MiB。保存step50 policy/config/optimizer非空，policy SHA256=d917925092923f0841ecc4cba74b7c8508bb80c95a4f17b3551a333e4fe0e18a，读取期间stat稳定；源snapshot beta0/new reward/G4/multi_v2已核验。51..52未保存，不用于step50评测；不是1500完成或算法崩溃，父训练保持停止。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2](runs/e014-structure-score-iou-explore-v1-beta0-current-multibox-analysis-r2.md)
- 最近记录更新：2026-10-15T08:59:26

### 本轮分析
Managed execution exited successfully with 0 declared and 13 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-step50-eval1766 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-step50-eval1766](runs/e014-structure-score-iou-explore-v1-beta0-step50-eval1766.md)
- 最近记录更新：2026-10-14T16:58:21

### 本轮分析
Managed execution exited successfully with 0 declared and 43 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-current-multibox-analysis.md)
- 最近记录更新：2026-10-15T08:59:27

### 本轮分析
Managed execution exited successfully with 0 declared and 7 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-sft659-seed11451.md)
- 最近记录更新：2026-10-14T23:57:30

### 本轮分析
用户切换0.5独立奖励变体，当前0.1训练按范围主动停止；8rank真实最后完成288，唯一协调器SIGTERM、自有workers退出，8GPU无compute进程；全部checkpoint/日志/数据保留，不是1500更新完成，不自动恢复。

### 本轮局限
未测试；仅源代码审阅及AST/配置/导航静态核对、实际受管启动和配置核验。0.1补偿是否能维持有效多框仍待训练与评测，Claim不变。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis.md)
- 最近记录更新：2026-10-15T08:59:27

### 本轮分析
# E-014 新增0.1补偿：当前一次快照

分析 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-current-multibox-analysis`。截至8rank共同完成53更新，3392 rollouts/848完整G4组。正式分析exit0，完整性、实际奖励重算、实际配置比较和同输入组核验通过；未执行模型评测或测试。

前期多框明显增加，但未持续。最后多框在39步，40–53连续14步没有合法/raw多框。

| 同前53步 | 无额外0.1 | 新增0.1 |
|---|---:|---:|
| 合法多框/全部生成 | 72/3392（2.12%） | 465/3392（13.71%） |
| 拼图正样本 | 52/1672（3.11%） | 388/1672（23.21%） |
| 原始正样本 | 4/860（0.47%） | 32/860（3.72%） |
| 原始负样本 | 16/860（1.86%） | 45/860（5.23%） |

新分支1–25/26–50/51–53窗口多框率20.75%/8.31%/0%。最近20步25/1280（1.95%）。raw多框507条，其中42非法，不能当合法多框。

420条合法正多框First/Selected/Oracle mIoU为0.47719/0.43452/0.73855。后续候选比首框更好151例，但实际选框相对首框41改善、60损失。IoU≥0.5：Oracle可救援133条；实际救援37条、损失56条。Oracle仅GT事后诊断，不能视为实际性能。

补偿实际生效420次，其中232条SelectedIoU≥0.3，确认补偿不局限低IoU。合法多框251正adv、214负adv；99同Query mixed组的组等权严格胜率46.46%，组等权mean(multi)-mean(single)=-0.02972。没有据此定位单一消失机理。

比较使用显式上一轮分析Run的不可变122步source_snapshot，只取共同前53步；实际配置除独立路径和新增multibox_bonus_weight=.1一致，输入group keys/条件匹配。两轮生成输出已随策略分化，单seed训练观察不能作稳定因果或测试集性能结论。父训练不停止、无持续监控，无Claim升级。

本地详细统计：analysis.json；SHA与完整性：integrity_audit.json；远端完整source_snapshot在本独立Run目录。


### 本轮局限
前期多框增加但40..53已连续14步无多框；score选择损失多于收益。未测试/模型评测，不持续监控或自动停训。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis.md)
- 最近记录更新：2026-10-15T08:59:27

### 本轮分析
# 新增0.1补偿：75步最新快照

最新固定快照8rank共同完成1..75，4800rollout/1200G4组、4728合法；beta0/.6/.1实际配置和奖励重算通过，排除pending0。合法多框467/4800=9.7292%，raw509含42非法。1..25/26..50/51..75多框332/133/2，率20.75%/8.3125%/.125%。近20步2/1280=.15625%，近50步135/3200=4.21875%；最近多框73。51..75仅2条均合法collage正样本、低IoU非近重复、adv均负。原正/负最后多框35/34。前期增加之后多框几乎消失，但不是严格零；累计比例不能代表当前输出。不改参数或训练、未测试/模型评测、不持续监控、无Claim升级。

最近非零多框更新：[{"update": 73, "valid_multi": 2, "raw_multi": 2}]

分析Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-latest-multibox-analysis`。单seed训练日志观察，不是最终性能或因果结论。详见analysis.json与integrity_audit.json；完整只读source_snapshot及SHA在独立Run。


### 本轮局限
未测试、未执行checkpoint评测；累计比例主要反映早期输出。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus01-reward-advantage-diagnosis.md)
- 最近记录更新：2026-10-15T08:59:27

### 本轮分析
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


### 本轮局限
未测试/模型重放/评测；没有EOS继续概率或token梯度证据。未改训练，不读live日志、不持续监控。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep](runs/e014-structure-score-iou-explore-v1-beta0-explore06-multibox-bonus-offline-sweep.md)
- 最近记录更新：2026-10-15T08:59:27

### 本轮分析
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


### 本轮局限
float64诊断adv近似日志float32；有选错框轨迹随补偿增大转正，采样缺多框的组不会凭空获得多框信号。未测试/模型重放/评测/新训练，不持续监控。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-sft659-seed11451.md)
- 最近记录更新：2026-10-15T08:34:56

### 本轮分析
用户要求暂停并评测step350；8rank最后完成380，唯一协调器SIGTERM、自有workers退出，8GPU idle，所有产物保留。当前保持暂停，不是1500完成，不自动恢复。step350 policy SHA2399a6db32649adc219f4e85f859dd052cbc634fe85571e5aee087ccdb235a84，beta0/.6/.5/G4来源核验。

### 本轮局限
未测试/模型评测；本次只有参数覆盖，无源码改动或新代码发布部署。0.5是否维持有效多框仍待训练，启动核验不是收益验证。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis.md)
- 最近记录更新：2026-10-15T08:59:27

### 本轮分析
# 0.5额外多框补偿：18步快照

分析 Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-current-multibox-analysis`。受管exit0/complete，8rank共同连续更新/G4完整组和实际奖励重算核验通过。

本次一次固定快照8rank共同完成1..18，1152rollout/288G4组，1124合法；实际beta0/.6探索/.5额外补偿重算通过。合法多框207/1152=17.96875%（合法分母18.4164%），raw222含15非法；最后多框18且该步17/64，未见持续消失。短窗口1..6/7..12/13..18为101/31/75（26.3021%/8.0729%/19.53125%），中段降后回升。collage正178/536=33.209%、原正4/308=1.2987%、负25/308=8.1169%，多框116正adv91负adv。只有18步，不能推断后续持续性或定位改善。用户同时要求整理分析log：默认本地.pi/analysis/e014/归档10辅助目录51文件，逐文件SHA/size不变，4个canonical Run本地artifact引用更新；服务器原Run/训练checkpoint不搬动。未测试/模型评测、不改训练或持续监控。

| 更新窗口 | 合法多框/全部生成 | 比例 |
|---|---:|---:|
| 1–6 | 101/384 | 26.30% |
| 7–12 | 31/384 | 8.07% |
| 13–18 | 75/384 | 19.53% |

这是单seed早期训练观察，未执行checkpoint评测或测试，Claim不变。父训练保持原配置，只在用户请求下做一次快照。

本地分析目录已归入第二层`.pi/analysis/e014/`，索引与移动前后路径/SHA见上级README.md及directory_migration_20261015.json。当前训练启动控制脚本保持原位置。


### 本轮局限
只有18共同完成步；多框主要在collage，原正低比例。未测试或模型评测。整理限本地辅助副本和路径引用，不改变服务器执行事实。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis.md)
- 最近记录更新：2026-10-15T08:59:27

### 本轮分析
# 额外0.5补偿：377步最新快照

Run：`e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-latest-multibox-analysis`。受管分析exit0/complete；仅一次固定字节快照，不持续监控。8rank共同完成377更新，24128生成/6032完整G4组，实际beta0/.6条件探索/.5额外补偿分项与总奖励重算通过。

## 当前观察

多框没有消失。累计合法多框20547/24128（85.16%），近50步3176/3200（99.25%），近20步1262/1280（98.59%）。近20步合法1262条全部2框，另18条非法；raw1280条全部有至少2个answer开头。

| 更新窗口 | 合法多框/全部生成 | 比例 |
|---|---:|---:|
| 1–25 | 348/1600 | 21.75% |
| 26–50 | 1198/1600 | 74.88% |
| 51–75 | 1308/1600 | 81.75% |
| 76–100 | 1344/1600 | 84.00% |
| 101–125 | 1249/1600 | 78.06% |
| 126–150 | 1447/1600 | 90.44% |
| 151–175 | 1593/1600 | 99.56% |
| 176–200 | 1389/1600 | 86.81% |
| 201–225 | 1165/1600 | 72.81% |
| 226–250 | 1409/1600 | 88.06% |
| 251–275 | 1599/1600 | 99.94% |
| 276–300 | 1597/1600 | 99.81% |
| 301–325 | 1597/1600 | 99.81% |
| 326–350 | 1594/1600 | 99.62% |
| 351–375 | 1583/1600 | 98.94% |
| 376–377 | 127/128 | 99.22% |

## 分层与质量

| 输入条件 | 全期多框比例 | 合法正样本Selected mIoU | 合法正样本Oracle mIoU |
|---|---:|---:|---:|
| collage:positive | 94.57% | 0.66575 | 0.70703 |
| original:negative | 64.09% | 不适用 | 不适用 |
| original:positive | 87.72% | 0.73468 | 0.74639 |

近50步合法正样本2375条：Selected mIoU=0.69558，Oracle=0.69794；负样本最大score均值=0.04920。这是训练观察，不是checkpoint评测，也不与不同条件组成窗口作因果比较。

近期基本固定两框，原始负样本也普遍两框，尽管负样本没有额外bonus。这表明出现广泛输出模式，不能仅用多框率判断有效实例覆盖、模型自适应候选数或最终定位收益。Oracle仅针对同Reference GT的事后候选上限，不是图中所有实例的覆盖指标。

## 边界

累计23911合法、217非法；raw多框20730中183非法。最新多框377。分析只按8rank共同连续完成更新截断，未完成行不混入。脚本保存source_snapshot及SHA，原日志和训练参数不变。

未测试/模型评测/新采样，Claim不变，不自动停训或评测。产物analysis.json与integrity_audit.json；本地目录保持在用户指定整理的第二层。


### 本轮局限
训练窗口组成不同；模型近期广泛输出两框，负样本也如此。未测试/模型评测，不持续监控或修改训练。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766.md)
- 最近记录更新：2026-10-15T08:43:38

### 本轮分析
首次启动目录preflight exit1：将参数配置放到outputs违反必须空占位约定；无payload/inputs、无模型加载/预测/指标，失败目录保留。当前用户任务由独立修正版 e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2 继续首次实际评测，未重用失败目录。

</details>

<details><summary>e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2 · 结果、来源与解释</summary>

- Run 笔记：[e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2](runs/e014-structure-score-iou-explore-v1-beta0-explore06-bonus05-step350-eval1766-r2.md)
- 最近记录更新：2026-10-15T09:23:21

### 本轮分析
step350正式评测完成：1766条/8GPU/exit0，indices与ID完整，逐条Selected/First/Oracle mIoU重算一致。Selected .6437733，First .6486097，Oracle .6540893，gap .0103161；1764条全部两个框、2非法，多框99.88675%。第二框meanIoU .0129444，仅13/1764≥.5，平均score .0358163；23条改善First，10条从First<.5救至Oracle≥.5，20条Selected错而Oracle正确。多框大量出现但有效新增定位很少，与低分错误第二框领取.5补偿的奖励投机解释一致；不宣称因果或量化下降，尚无用户指定同协议基线。训练暂停，不改奖励/重训/Claim，未额外测试，正式评测及完整性验收完成。 奖励构造例：正确单框u=.8/s=1得2.9；distinct两框u=.4/0、s=0/0得3.0，较差Selected定位可因.5补偿获更高R。结论仍需匹配对照验证。 横向位置核对（同predictions SHA、不重推理）：1756有效GT左/右半区893/863，第一框mIoU .6413275/.6636608，右半区也由第一框有效定位；1764个第一框有986个中心x≥500。第二框均值中心912.17，中位916.5，1676/1764=95.01%中心≥850，1486中心≥900，显示最右端低分补框模式；生成序号1不等于图像左侧真实实例。GT半区不等于AB/BA实例排名，不能替代拼图专项评测。

### 本轮局限
此前已查看测试集；未指定匹配对照，不能报告下降幅度或单独归因于0.5；指标未注册为Experiment主证据，无Solid结果，不提升Claim。未额外测试。

</details>

<details><summary>e014-boxes-then-scores-sft659-step0-eval1766 · 结果、来源与解释</summary>

- Run 笔记：[e014-boxes-then-scores-sft659-step0-eval1766](runs/e014-boxes-then-scores-sft659-step0-eval1766.md)
- 最近记录更新：2026-10-15T12:25:25

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-boxes-then-scores-beta0-step150-eval1766 · 结果、来源与解释</summary>

- Run 笔记：[e014-boxes-then-scores-beta0-step150-eval1766](runs/e014-boxes-then-scores-beta0-step150-eval1766.md)
- 最近记录更新：2026-10-15T17:20:18

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-boxes-then-scores-collapse-analysis · 结果、来源与解释</summary>

- Run 笔记：[e014-boxes-then-scores-collapse-analysis](runs/e014-boxes-then-scores-collapse-analysis.md)
- 最近记录更新：2026-10-15T16:02:45

### 本轮分析
已完成父训练184步11776rollout/2944个完整G4组的离线分析。21..100共5120条原始/合法多框0；101..150仅2/3200；151..184为0/2176。78合法多框、65非法原始多框（46未终止）。28个同prompt合法单/多混合组中，多框相对单框平均reward差-.461663，score原始项差-.265374（权重1.1后-.291911）、IoU差-.161895、结构差-.007857；多框logged advantage-.532032、单框+.392659，6/28组多框reward更高。24个整组全合法组中差-.469068，多框advantage-.710598。71合法正样本多框Selected .404593/Oracle .751375。78条固定生成候选保留第一框的奖励反事实：完整多框16更好/46更差/16相同，平均delta-.215598，其中score-.256478、结构-.035385、IoU+.076265；37条覆盖改善，18条Selected改善。示例step12 IoU[0,.755915]/score[.45,.31]选错，完整reward1.57629，相比只保留第一框降低.30096。证据支持早期未完成惩罚、评分收益未兑现和序列级共同强化促成单框收敛；beta0仍发生故KL不是必要条件，未证明关闭KL无影响。

### 本轮局限
观察性日志与固定候选删框奖励反事实，不是重新生成或重训的因果消融；不能保证模型可直接单框生成原选中框。合法多框集中早期、同prompt混合仅28组，整体单/多均值有时间和难度混杂。优势使用日志原值；Python双精度复算与训练float32最大差.00372，不能称逐值精确复现。未测试/新模型推理，未改奖励、训练或Claim；本Run无Solid结论。

</details>

<details><summary>e014-discovery-priority-score04-beta0-sft659-200step-seed11451 · 结果、来源与解释</summary>

- Run 笔记：[e014-discovery-priority-score04-beta0-sft659-200step-seed11451](runs/e014-discovery-priority-score04-beta0-sft659-200step-seed11451.md)
- 最近记录更新：2026-10-15T23:28:56

### 本轮分析
Managed execution exited successfully with 0 declared and 6 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-discovery-score04-step200-eval1766-20261015T152856Z · 结果、来源与解释</summary>

- Run 笔记：[e014-discovery-score04-step200-eval1766-20261015T152856Z](runs/e014-discovery-score04-step200-eval1766-20261015T152856Z.md)
- 最近记录更新：2026-10-16T00:12:07

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-discovery-score04-step150-eval1766-20261015T161128Z · 结果、来源与解释</summary>

- Run 笔记：[e014-discovery-score04-step150-eval1766-20261015T161128Z](runs/e014-discovery-score04-step150-eval1766-20261015T161128Z.md)
- 最近记录更新：2026-10-16T00:37:26

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-step150-vs200-paired-analysis-20261016 · 结果、来源与解释</summary>

- Run 笔记：[e014-step150-vs200-paired-analysis-20261016](runs/e014-step150-vs200-paired-analysis-20261016.md)
- 最近记录更新：2026-10-16T00:37:49

### 本轮分析
同轮1766条逐dataset_index/id/dataset/target对齐。step150 Selected .6932669712 Oracle .7263236003 多框263/1766；step200 Selected .6916960158 Oracle .7573992982 多框791/1766。single→multi n528 Selected .6204368738→.5962361197 Oracle .6204368738→.7192414999；multi→multi n260 Selected .5840363228→.6465473505。Oracle命中但Selected失败67→133；150多框全零score84/263，失败中top tie29/67。最后50步候选覆盖改善但整体选框持平，不能断言显著退化或奖励因果。未做图像人工复核、显著性检验；未测试，无Solid/Claim提升。

</details>

<details><summary>e014-reward-order-simulation-20261016 · 结果、来源与解释</summary>

- Run 笔记：[e014-reward-order-simulation-20261016](runs/e014-reward-order-simulation-20261016.md)
- 最近记录更新：2026-10-16T01:02:25

### 本轮分析
离线合成模拟完成，单/双候选386262组，另含15类行为示例（M6用三框）。硬档位10/10跨档关系成立；较平滑方案仅1/10满足跨全网格严格分离，不能解释为实际样本90%排序错误。固定score=.1/.1、第一框IoU=.1，第二框IoU .4999→.5001时，较平滑reward 1.225625→.906375，下降.31925，源于二值score标签跳变。未改变训练奖励，未启动训练；合成网格不代表实际分布或训练效果。

</details>

<details><summary>e014-reward-constraint-solver-20261016 · 结果、来源与解释</summary>

- Run 笔记：[e014-reward-constraint-solver-20261016](runs/e014-reward-constraint-solver-20261016.md)
- 最近记录更新：2026-10-16T01:20:06

### 本轮分析
本地自动求解完成：46141条搜索约束、90972条留出约束(seed20261016，10000个初始1–6框合成回答)。smooth_binary和smooth_taper在公开函数族/系数边界内无解，保存不可约冲突；hard_binary权重H .34375/Oracle .05/Selected .4041666667/score .2020833333通过受控偏序，留出违反0，全局五档仅4/10。hard_tier权重L .65/Oracle .05/Selected .15/score .15，辅助C .05/D -.02/O -.02；留出违反0，五档10/10，解析相邻全档差下界.21。G4模拟使用总体std+1e-6，发现但选错可因组内其他回答更好获得负优势。未改变训练或部署，未证明训练收益。

</details>

<details><summary>e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451 · 结果、来源与解释</summary>

- Run 笔记：[e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451](runs/e014-20261015T172455Z-tier065-oracle005-selected015-score015-g8-kl0-sft659-400step-seed11451.md)
- 最近记录更新：2026-10-16T08:53:28

### 本轮分析

2026-10-16 用户授权暂停以评测step200；SIGINT后exit1、GPU已清空、step200保留。工具无paused执行状态，attempt以authorization/user interruption终止登记，不代表科研失败；未恢复。

</details>

<details><summary>e014-tier-g8-onecheck-20261015T183221Z · 结果、来源与解释</summary>

- Run 笔记：[e014-tier-g8-onecheck-20261015T183221Z](runs/e014-tier-g8-onecheck-20261015T183221Z.md)
- 最近记录更新：2026-10-16T02:32:23

### 本轮分析
本地一次性只读分析完成；仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。；窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。；完整报告 /home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-tier-g8-onecheck-20261015T183221Z/report.json

</details>

<details><summary>e014-tier065-g8-step200-eval1766-20261016T002327Z · 结果、来源与解释</summary>

- Run 笔记：[e014-tier065-g8-step200-eval1766-20261016T002327Z](runs/e014-tier065-g8-step200-eval1766-20261016T002327Z.md)
- 最近记录更新：2026-10-16T09:16:57

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-tier065-g8-step150-eval1766-20261016T011613Z · 结果、来源与解释</summary>

- Run 笔记：[e014-tier065-g8-step150-eval1766-20261016T011613Z](runs/e014-tier065-g8-step150-eval1766-20261016T011613Z.md)
- 最近记录更新：2026-10-16T09:43:39

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-score05-multibox-check-20261016T045945Z · 结果、来源与解释</summary>

- Run 笔记：[e014-score05-multibox-check-20261016T045945Z](runs/e014-score05-multibox-check-20261016T045945Z.md)
- 最近记录更新：2026-10-16T13:01:09

### 本轮分析
一次日志快照，8rank共有51个完整rollout步（原始编号0..50）。合法多框/全部：前20步43.01%、随后20步69.96%、最后11步57.67%，未消失但后段回落。最近20步2560条，合法2529，合法多框1749=68.32%，拼图89.17%、原图44.09%。1949合法正样本Selected=.540093、Oracle=.766167，gap=.226074；拼图gap=.297323。1482合法正多框中554后框改善Oracle、513后框补救首框未命中。仅28个混合单多框同输入组，多框平均advantage差-.258772，样本受条件筛选，不推断总体因果或未来坍缩。未修改训练、未新增测试、不持续监控；结果为训练采样，不替代固定验证。 完整报告 .pi/analysis/e014/e014-score05-multibox-check-20261016T045945Z/extended_report.json

</details>

<details><summary>e014-score04-step150-200-visual-20261016T060926Z · 结果、来源与解释</summary>

- Run 笔记：[e014-score04-step150-200-visual-20261016T060926Z](runs/e014-score04-step150-200-visual-20261016T060926Z.md)
- 最近记录更新：2026-10-16T14:12:59

### 本轮分析
离线可视化完成。两次1766样本id/GT/manifest对齐，生成15个案例（5类各3、按幅度选取且序列去重）与整体统计SVG、可筛选HTML。150→200合法多框率.148924→.447905，Selected .693267→.691696，Oracle .726324→.757399。成功后框补救45→103，存在正确候选但最终选错67→133；数量变化不能脱离多框基数解读，案例非代表性抽样。未新推理/未改训练/未提升Claim。源文件与图像哈希已保存；SVG/XML和样本映射核对通过，未进行浏览器人工视觉检查，未测试。

</details>

<details><summary>e014-score05-gap-check-20261016T064643Z · 结果、来源与解释</summary>

- Run 笔记：[e014-score05-gap-check-20261016T064643Z](runs/e014-score05-gap-check-20261016T064643Z.md)
- 最近记录更新：2026-10-16T14:46:52

### 本轮分析
本地一次性只读分析完成；仅一次训练采样快照，不能代替固定验证集评测；未自动重试或修改训练。；窗口内仍存在合法正样本多框，不判定已消失；按原图/拼图分开查看比例。；存在较大选框差距；优先离线检查正确候选低分与错误候选高分，针对评分目标优化，不仅提高框数收益。；完整报告 /home/zhengyuesong/Projects/NKU-MASTER/Projects/26-CVPR/incontext/.pi/analysis/e014/e014-score05-gap-check-20261016T064643Z/report.json

</details>

<details><summary>e014-score05-step100-check-20261016T074036Z · 结果、来源与解释</summary>

- Run 笔记：[e014-score05-step100-check-20261016T074036Z](runs/e014-score05-step100-check-20261016T074036Z.md)
- 最近记录更新：2026-10-16T15:41:17

### 本轮分析
快照含101个完整rollout步（编号0..100），step100权重文件已存在。最近20步2560条：合法率99.531%，多框48.633%，Selected .682695/Oracle .789470/gap .106775；拼图多框88.417%、Selected .652588/Oracle .802948/gap .150360；原图多框13.529%、Selected .735737/Oracle .765726/gap .029990。相对约81步窗口，多框减少且gap缩小，Oracle亦下降；不可将gap缩小全部归因于评分改善，输入样本不同且原图候选减少需关注。未改训练/未测试/无持续监控。 完整报告 .pi/analysis/e014/e014-score05-step100-check-20261016T074036Z/extended_report.json

</details>

<details><summary>e014-score05-progress-20261016T103959Z · 结果、来源与解释</summary>

- Run 笔记：[e014-score05-progress-20261016T103959Z](runs/e014-score05-progress-20261016T103959Z.md)
- 最近记录更新：2026-10-16T18:40:39

### 本轮分析
截至162个完整rollout步，exitnull，保存50/100/150。运行配置coverage_weight=.5（未改.2）、score=.5、G8/KL0/400。最近20步2560条合法率99.492%、多框58.75%；合法正样本Selected .709722/Oracle .769078/gap .059355。拼图多框98.878%、Selected .697954/Oracle .775551/gap .077597；原图多框20.579%、Selected .731914/Oracle .756872/gap .024958。相对约101步快照多框回升、gap较小，但不同输入窗口不可作为固定验证或因果结论。未改训练、未测试、无持续监控。 完整报告 .pi/analysis/e014/e014-score05-progress-20261016T103959Z/extended_report.json

</details>

<details><summary>e014-score05-progress-20261016T123919Z · 结果、来源与解释</summary>

- Run 笔记：[e014-score05-progress-20261016T123919Z](runs/e014-score05-progress-20261016T123919Z.md)
- 最近记录更新：2026-10-16T20:39:48

### 本轮分析
最新一次快照，共202完整rollout步。最近20步多框0.550781、Selected0.733889/Oracle0.775670/gap0.041781。配置与checkpoint见报告.pi/analysis/e014/e014-score05-progress-20261016T123919Z/extended_report.json。不同训练窗口非固定验证结论；未修改训练、未测试、不持续监控。

</details>

<details><summary>e014-discovery-score05-g8-step200-eval1766-20261016T124126Z · 结果、来源与解释</summary>

- Run 笔记：[e014-discovery-score05-g8-step200-eval1766-20261016T124126Z](runs/e014-discovery-score05-g8-step200-eval1766-20261016T124126Z.md)
- 最近记录更新：2026-10-16T21:05:29

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150 · 结果、来源与解释</summary>

- Run 笔记：[e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150](runs/e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150.md)
- 最近记录更新：2026-10-17T13:17:31

### 本轮分析
Managed execution exited successfully with 0 declared and 6 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-resume-multibox-20261016T165703Z · 结果、来源与解释</summary>

- Run 笔记：[e014-resume-multibox-20261016T165703Z](runs/e014-resume-multibox-20261016T165703Z.md)
- 最近记录更新：2026-10-17T00:59:13

### 本轮分析
续训单次快照：原始step200..275共76完整rollout步，累计约276，保存250，exitnull，300评测尚未生成。最近20步多框60.117%、Selected .734547/Oracle .777330/gap .042784；拼图多框97.177%、原图8.675%。原图Selected .706594/Oracle .725123/gap .018529；不同训练输入不可作固定评测性能下降结论。step200固定1766评测已完成，多框13.8165%、Selected .679512/Oracle .713852/gap .034340。coverage .5、score .5/G8/KL0维持；未改训练、未测试、不持续监控。一次只读审批连接中断未执行，同流程重试成功。 完整报告 .pi/analysis/e014/e014-resume-multibox-20261016T165703Z/extended_report.json

</details>

<details><summary>e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150-derived-001 · 结果、来源与解释</summary>

- Run 笔记：[e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150-derived-001](runs/e014-20261016T124428Z-score05-cover05-g8-resume200-to400-eval150-derived-001.md)
- 最近记录更新：2026-10-18T10:44:26

### 本轮分析
用户授权停止：8rank实际共同完成818，最新保存checkpoint800；不是完成1500。

### 本轮局限
旧checkpoint没有rank RNG，采样重新播种，不是精确随机轨迹恢复。预算延长为用户明确科学变化；其余训练与评测设置保持。单seed/已看测试集不作因果Claim。

</details>

<details><summary>e014-score04-step200-native-vqa1766-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-score04-step200-native-vqa1766-20261018](runs/e014-score04-step200-native-vqa1766-20261018.md)
- 最近记录更新：2026-10-18T11:23:46

### 本轮分析
Managed execution exited successfully with 0 declared and 14 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-score04-step200-native-vqa-exact1766-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-score04-step200-native-vqa-exact1766-20261018](runs/e014-score04-step200-native-vqa-exact1766-20261018.md)
- 最近记录更新：2026-10-18T11:49:10

### 本轮分析
Managed execution exited successfully with 0 declared and 15 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-score04-step200-native-vqa-drawn1766-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-score04-step200-native-vqa-drawn1766-20261018](runs/e014-score04-step200-native-vqa-drawn1766-20261018.md)
- 最近记录更新：2026-10-18T12:15:17

### 本轮分析
Managed execution exited successfully with 0 declared and 16 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-selection-sft-data-step200-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-selection-sft-data-step200-20261018](runs/e014-selection-sft-data-step200-20261018.md)
- 最近记录更新：2026-10-18T13:20:19

### 本轮分析
Managed execution exited successfully with 0 declared and 18 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-drawn-selection-lora-sft1epoch-20261018-r2 · 结果、来源与解释</summary>

- Run 笔记：[e014-drawn-selection-lora-sft1epoch-20261018-r2](runs/e014-drawn-selection-lora-sft1epoch-20261018-r2.md)
- 最近记录更新：2026-10-18T16:42:26

### 本轮分析
全部72步loss有限、finite_grad_fraction=1，adapter_delta_norm=2.736153869420579。训练更新耗时794.067s。固定8个训练样本before/after CE=0.007273048726347042/0.048288823978509754，原有loss_after<loss_before条件未满足，payload/training/metrics.json status=gate_failed，worker exit2→launcher exit1，根metrics复制未执行。前12/后12步平均训练loss0.455166/0.196551，但各步样本不同，不能用此推翻固定批次门禁，也不能声称泛化改善。初始化兼容问题已由完整训练验证解决；不更改门禁或自动重训。尚未内部验证或测试集评测。

</details>

<details><summary>e014-selection-lora-step72-validation334-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-selection-lora-step72-validation334-20261018](runs/e014-selection-lora-step72-validation334-20261018.md)
- 最近记录更新：2026-10-18T18:11:18

### 本轮分析
Managed execution exited successfully with 0 declared and 17 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-selection-lora-step72-test1766-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-selection-lora-step72-test1766-20261018](runs/e014-selection-lora-step72-test1766-20261018.md)
- 最近记录更新：2026-10-18T18:39:33

### 本轮分析
Managed execution exited successfully with 0 declared and 17 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-selection-lora-resume72-total5epochs-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-selection-lora-resume72-total5epochs-20261018](runs/e014-selection-lora-resume72-total5epochs-20261018.md)
- 最近记录更新：2026-10-18T20:08:34

### 本轮分析
实际history73..360连续且全部loss有限/finite_grad_fraction1/lr5e-5；累计history前72项与父训练完全一致。8个checkpoint108/144/180/216/252/288/324/360均核trainer_state步数、samples、scheduler、504 AdamW状态、adapter配置及SHA；最终adapter与step360哈希一致。固定8训练样本CE从恢复模型step72的0.048288823978509754降至0.000032193263558522034；adapter_delta_norm相对step72为2.826792710906639。本段训练3174.548s（约52.91min）。数据SHA及模型NF4/LoRA/seed/快照53ab765与批准配置一致。续训前36/末36步平均loss0.134879/0.001158仅描述训练，不替代验证。

### 本轮局限
当前仅验收训练事实，未执行step360内部验证或1766测试。低训练loss不能证明泛化或Oracle差距缩小；过拟合尚未排除。恢复重播种非精确RNG replay；名义warmup18但全续训实际lr5e-5。父1epoch gate_failed历史不改，Claim不改。

</details>

<details><summary>e014-selection-lora-step360-test1766-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-selection-lora-step360-test1766-20261018](runs/e014-selection-lora-step360-test1766-20261018.md)
- 最近记录更新：2026-10-18T21:41:20

### 本轮分析
21:41:06 managed complete成功。1766唯一ID/索引与固定候选GT重算、791合法VQA/964单框/11无候选、1582原图及渲染SHA核验通过；渲染与step72/native完全一致，模型step360 SHA/快照/提示词/参数已核。全量mIoU step72 69.9607→step360 70.3153（+0.3546pp）；Acc50 76.2174→76.6138（净增7）。多框mIoU62.9412→63.7329。对step72选择改变75：28 IoU改善/25损害/22持平，25命中修复/18损害；对原score83改善/57损害，65修复/46损害；对native76改善/30损害，70修复/20损害。全量原score69.1696、native67.8265、Oracle75.7399，仍差Oracle5.4246pp。分集GOT82.5101→82.7927，LaSOT66.4820→66.4491，TAO69.7865→70.3901。仅小幅且分集不一致的改善。完整证据.pi/analysis/e014/selection-sft/test1766_step360_audit.json。

### 本轮局限
管理工具将17项指标保存为辅助指标，未登记为Experiment主指标，不升级Claim。测试集重复探索且单seed、未检验显著性，不能称无偏独立测试或稳定泛化；生成器历史同视频暴露仍存在。训练loss大幅下降不能替代测试指标。无额外训练/评测/选checkpoint，父管理失败记录保留。

</details>

<details><summary>e014-selection-fulltrain-step200-gtaugment-20261018 · 结果、来源与解释</summary>

- Run 笔记：[e014-selection-fulltrain-step200-gtaugment-20261018](runs/e014-selection-fulltrain-step200-gtaugment-20261018.md)
- 最近记录更新：2026-10-19T01:12:40

### 本轮分析
Managed execution exited successfully with 0 declared and 40 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

### 本轮局限
Phase 1 records process evidence only; auxiliary metrics remain unregistered and cannot define primary evidence or Claim conclusions.

</details>

<details><summary>e014-selection-fulltrain-step2095-test1766-20261019 · 结果、来源与解释</summary>

- Run 笔记：[e014-selection-fulltrain-step2095-test1766-20261019](runs/e014-selection-fulltrain-step2095-test1766-20261019.md)
- 最近记录更新：2026-10-19T08:28:53

### 本轮分析
08:28:40 managed complete成功；1766唯一覆盖/冻结候选GT重算/791合法VQA/1582渲染SHA与小集step72及360完全一致，step2095 adapter SHA与推理快照已核。全量mIoU71.1392/Acc50 77.6897%，多框mIoU65.5724/Acc50 70.7965%。较小集step360全量mIoU+0.8239pp，103选择变化，48 IoU改善/28损害，41命中修复/22损害净19；较小集step72+1.1785pp，净26命中。相对score90改善/44损害、71修复/33损害净38，全量mIoU+1.9696pp。GOT/LaSOT/TAO mIoU82.7908/67.4391/71.2637；较小集step360分别约-0.0019/+0.9901/+0.8736pp。全量Oracle75.7399仍差4.6007pp，多框Oracle75.8440仍差10.2716pp。

### 本轮局限
扩大独立训练源、加入TAO、补GT及更新预算同时变化，不能单独归因GT补框。重复探索测试集、单seed，无显著性检验，不是无偏独立测试。辅助指标不升级主指标或Claim。训练保持用户中断状态，无自动恢复/追加评测。

</details>

## 详细审计正文（canonical）
这里保存指标定义、证据链、逐层结论边界与审核入口；后续 Run 更新不会覆盖本节。
