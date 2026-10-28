# E-014 历史checkpoint候选扩集审计

## 范围与结论

用户要求按历史checkpoint互补候选方案查找新数据，并跨E-012/E-013核查。本轮为只读资产、协议和样本身份审计：没有执行新推理、训练、checkpoint筛选评测或修改Claim。用户提供的base_commit只是所附材料的版本标记，本轮以实际本地文档和远端文件核验，不切换代码版本。

找到了可作为候选生成来源的真实权重。但尚未产出新训练题，不能报告新增有效样本数。旧测试预测不得回填训练；旧训练rollout只覆盖原训练子集，不能解决TAO覆盖。

## 已核实的代表权重

远端共同根：`SZY-3090:/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/`。以下权重均存在，adapter配置已读、SHA已计算；尚未执行模型加载或新推理。推荐依据协议类型和历史训练身份，不依据本轮测试成绩。

| 定位 | 相对路径（checkpoint） | adapter SHA256 | 建议用途 |
|---|---|---|---|
| E012 单框无score | E-012/ref10-query5-correct-step247-3ep-v1/training/checkpoints/samples_00031566_step_000494 | 55f7c527dd9aaeade013d216524ec804a699d70f4cec2001f97e8acf0186669f | 首轮：单框互补来源；不是0置信度模型 |
| E013 confidence SFT659 | E-013/focus-confidence-sft/checkpoints/samples_00042136_step_000659 | edcaaa4fc25adcf608af068c0c05375d5ef24ba9e55eea00567a71f9d596673a | 首轮：使用已记录的三框位置/边界假设v2提示词；权重原本是单框SFT，须区分训练与推理协议 |
| E013 原始单框GRPO500 | E-013/focus-confidence-sft/branches/20260921T172801747698Z--focus-confidence-grpo-overnight-ready/grpo/checkpoints/step_000500 | cdc3ff75a1b54db11c798494fbbc17e0c76b9e29cb043923bd3ca69ddb54d0b9 | 备用单框+score来源 |
| E013 三实例GRPO650 | E-013/focus-confidence-sft/branches/20260922T165640005821Z--multi3-instances-grpo-lr8e5-3ep/grpo/checkpoints/step_000650 | 5ab9b21c623df533430baa88f48ba383002a4fd7a23c65cef3721950ca4fbb15 | 首轮：原生focus_multi3_instances_v1候选组 |
| E013 rank-cf450 | E-013/focus-confidence-sft/branches/20260928T170859Z--multi3-instances-grpo-rank-cf-lr8e5-3ep/grpo/checkpoints/step_000450 | b1fbe4ded81ce7e186bf9574e5d2613c4037a270956ebf9fabae05875b27a884 | 备用同协议来源，不因多一个checkpoint而增加独立样本权重 |

前三类首轮来源是E012494、SFT659三框v2、三实例650；原E014 score0.4/step200完整训练预测继续复用。不需要一开始把所有历史checkpoint跑一遍。若三种新增来源各覆盖8367对，新增生成预算为25101个源-协议组合（这是建议预算，尚未启动）。

E012实际resolved配置为focus协议，ReferenceQueryAttentionDistillation，初始化E009 step247；其训练vision预算1024，与当前选择器4096不同，收集时需明确使用的生成预算，不能抹去历史差异。E013旧GRPO的max_pixels=262144也与现有生成4096 patch预算不同。首轮建议新收集统一4096，明确属于新生成条件，而非历史运行复现。

## 旧预测与训练日志复用

1. 找到17个非空标准`predictions.jsonl`：15个1766全量文件、2个8例smoke文件。全部逐行按dataset_index/dataset/sequence对应当前测试清单；不准回填训练。这个对应检查不替代Reference图像/变换认证。
2. E013旧`trainable_pairs.json`有2000个正例。其中1607对与当前8367清单同时满足Reference/Query图像路径（仅归一化历史根目录前缀）及两个原始bbox完全一致：GOT10k1453、LaSOT154、TAO0。
3. 只检查rank0日志的可定位原图正例覆盖如下。它们尚未通过候选严格解析、EOS、坐标/IoU复算和去重入库门禁；不等于新增合格选择题数。其他rank尚未全量审计，不能当作全日志覆盖。

| 来源 | 可定位原图正例rollout条数 | 独立图像对 |
|---|---:|---:|
| 三实例650训练轨迹 | 2028 | 385 |
| 三实例rank600训练轨迹 | 1840 | 385 |
| rank-cf训练轨迹 | 1480 | 370 |
| 单框GRPO训练轨迹 | 1880 | 385 |
| collage完整训练的original部分 | 2268 | 522 |

这些轨迹混合了训练过程中的多种权重、采样解码和重复访问，不能标成某一个保存checkpoint的固定预测。collage行本轮直接排除，不将其框坐标迁移到原Query。

两条历史eval-checkpoints adapter软链接已失效（collage step1400和pilot step100）；真实grpo/checkpoints路径存在，但本轮没有选择这些拼图模型。测试fixture目录中的假adapter也不能作为真实checkpoint。

初次按manifest `id`连接得到0匹配，是当前manifest没有id字段导致的无效连接，不是零重叠结论。`identity_audit.json`已改用两图+bbox精确对应（训练）和索引/数据集/序列（测试）纠正；`prediction_reuse_audit.json`初始id-match字段不得用于隔离判断。

## 下一阶段的数据构造约束

- 只在现有8367合法正例上收集，保持原视频/序列隔离；不限定于已入选3571例，有机会使原先单候选等被排除样本成为新有效题。能新增多少独立源待真实预测后统计。
- 原生组优先；跨模型组只补互补情形，先合并完全相同框，再检查最佳-次佳间隔。几乎重合的两个好框不能通过增加GT伪造清晰标签。
- `K>=2、Oracle>=0.5、best-second>0.05`。原Oracle<0.5且非空时，只在训练副本补GT。无合法候选不直接造题。
- 只有生成器score失误证据的组标成generator-selection-error，不冒称当前VQA也选错。当前VQA难例挖掘需要另行实际前向。
- 不向VQA提供checkpoint来源、score、IoU或GT来源标识。输入沿用当前无框原图+bbox协议。
- 原生组、互补组、GT组、普通保留组分别记录；不先编造比例或最终数量。跨模型组比例及普通/难例混合需在真实分布出来后固定。
- 采样建议：数据集各1/3，再等概率独立图像对，再候选组，再编号轮换。若静态展开，完整权重应含`p(dataset)/N_dataset × 1/M_x × 1/K_g`，不能只写最后两个因子。须对训练sampler是否实际消费权重做实现核验，不能仅在JSON加一个weight字段就声称已平衡。
- 图像对等权不等于视频组等权；继续报告独立图像对和原视频/序列组数。编号平衡按K条件统计。
- 优先报告各数据集新增独立源数、生成器选择错误组、自然互补组、仍需GT组、原有组重合率；总轮换行数仅为辅助指标。

## 科学边界

复用历史模型增加的是候选情景，不自动增加新的图像场景。TAO/LaSOT需要在完整合法清单上收集，单靠旧2000正例日志不能补足。历史checkpoint可能见过更广训练范围，现有1766又反复用于探索；本轮隔离不消除历史暴露，不能宣称无偏泛化。

“单框＋0置信度”尚未唯一确定：E012 focus没有score；E013 SFT只屏蔽score数值CE，并非固定0。旧单框SFT评测1754个有score结果中仅3个score=0，GRPO500为212/1766；这些仅用于辨认输出协议，不能据此排名或挑选模型。

## 证据

- `.pi/analysis/e014/historical-candidate-sources-20261019/{remote_paths.txt,asset_probe.json,prediction_reuse_audit.json,identity_audit.json,shortlist_verified.json}`。
- `shell/06_experiments/E-013/sft_implementation.md` §损失边界。
- `shell/06_experiments/E-013/multi_candidate_evaluation.md` §固定协议v2。
- `shell/06_experiments/E-014/prompt_comparison.md` §当前常用prompt与变长prompt。
- E012文档实际位于`shell/06_experiments/E-013/E-012/`，不是顶层E-012；远端实验目录则是顶层E-012。
