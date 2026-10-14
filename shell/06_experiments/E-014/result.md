# E-014 · 实验结果

> 记录截至：2026-10-14T09:07:05。记录更新不等于实际运行完成；程序完成也不等于科研结论成立。

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

## 详细审计正文（canonical）
这里保存指标定义、证据链、逐层结论边界与审核入口；后续 Run 更新不会覆盖本节。
