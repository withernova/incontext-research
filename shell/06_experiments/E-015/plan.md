# E-015 · Qwen2 多shot SFT→GRPO多框→VQA

- status: running
- kind: standalone
- source_ref: 
- claim_refs: 
- priority: medium
- created: 2026-10-21T18:44:59
- updated: 2026-10-28T11:10:00

## 实验目标
采用Qwen2-VL-7B-Instruct与对齐FOCUS的基础多shot设置运行本方法：SFT→GRPO多框proposal→VQA选择；4shot训练、同一套模型评测1/2/4shot，使用4副本×2卡。与E-014分开记录和保存产物。

## 假设
增加同一目标轨迹的参考帧，可能降低跨帧变化导致的实例漏选，缩小实际IoU与proposal Oracle的差距；尚待实测。

## 成功标准
- 工程：4×2下4shot SFT、GRPO和选择器可完成，有限梯度、保存恢复与副本一致性正确。
- 科学：同1728 Query、同一E015已训练模型的1/2/4shot报告实际mIoU、Acc50、Oracle及可命中未选中数量；4shot相对1shot的变化按配对样本解释，不预设成功阈值。

## 失败/证伪标准
- OOM、非有限梯度、跨副本参数不一致、输入来源或哈希失败时停止并保留产物。
- 多shot实际指标不改善或下降时如实报告，不能将可运行当作方法有效。

## 实验安排
2026-10-28 已核实际训练首步：e015-qwen2-selector-e014clean4shot-20261028，全部16173条4shot（LaSOT2908/GOT7175/TAO6090），删511条（26个无有效四参考来源及18测试重合视频关联题目）；7806源样本，48870训练/测试唯一图像可读性/SHA检查通过。原1604题prompt逐条一致，候选排列/标签保留；视频/路径/内容SHA/受保护LaSOT类别交集均0。数据SHA6492bd956a13fae0be6018867328a00a7dddcbcbba03715514fbe18029d3ceeb。实际resolved配置与原E015仅数据路径/SHA、输出目录及epoch缩放衰减起止不同。4epoch/global16/4044更新；4×2GPU实际first update loss0.4964896869、finite_grad_fraction1.0、rank0双卡峰值allocated12.3623GiB（不是全卡峰值）；无OOM/Traceback。初始化耗时为四副本完整输入哈希复核，已完成进入训练。随后固定E0151289与E0141745各1/2/4shot评测，E014另保留同1727分母；只总体/分集。GRPO保持取消，尚无本次最终结果。证据.pi/analysis/e015/selector-e014clean4shot-20261028/{data_and_startup_observation,input_read_progress_observation,training_progress_observation,startup_managed_status}.json。

2026-10-28 用户纠正E014只应替换数据来源、E015内VQA必须统一，并明确重新训练。独立e015-qwen2-selector-e014clean4shot-20261028（dispatch-53cdbd225ddf60c0fcf23561）已受管启动CPU数据准备，随后自动训练和评测。复用E015真实已验收4shot参考清单，不自行重新取帧；原16684清洗行有26源不在有效四参考清单，关联题目删除；同时排除E01536测试类及两组所有1/2/4shot评测视频/图像，包括此前18跨数据集重合。候选/排列/标签保留，统一exact_instance多参考原图prompt与数字+EOS监督。实际训练配置复制原r3 selector resolved SHA0842fe71eaa034b314d6bb0a65e06d4f337102482cfc806ab13a0707e84c5a75：Qwen2 fresh LoRA r8/alpha16/NF4/BF16/SDPA/4×2GPU/layer10、4096patches/global16/4epoch/lr5e-5/warmup.03/clip.3/seed20260901/末1/4衰减.1/每.5epoch保存。只改数据/输出与按epoch缩放步数，保留数据规模导致更新量变化的边界。数据准备后核验原E0151604题prompt等同及新全体五图/框/隔离。训练完成后固定E0151289与E0141745各1/2/4shot评测，E014另报同1727子集，不单列多框。244独立指标；原1shot clean结果只留历史非统一协议诊断，GRPO不恢复。

此前记录：
2026-10-28 E014固定proposal×新Qwen2 VQA1/2/4shot全部完成exit0/marker/tmuxfalse，官方complete→analysis_pending，192指标。逐条3×1745候选/ID/IoU和汇总复核通过。排除18训练原视频重合的共同1727，VQA mIoU71.099571/68.499787/63.174226%，score69.525995%，Oracle76.117321%；完整1745为70.987200/68.284446/63.057456%，score69.429856/Oracle75.953191。排除后分集VQA：LaSOT582为67.056922/64.675987/59.244500，GOT180为82.306882/83.128905/75.212571，TAO965为71.447245/68.077207/63.298785。同1727历史Qwen3 VQA1shot72.220238%，新Qwen2 1shot低1.120668pp。无效回答0/13/153：2shot十三条Reference 1/2，4shot148条越界3/4（88/60）+5条Reference X，全部EOS；提示编号/多参考适配问题，不能据此归因纯格式或否定多参考价值。诊断性invalid→score回退4shot仅增加5.089593pp至68.2638%，非正式指标。固定同候选只改VQA参考数；报告总体/分集，不单列多框子集。GRPO仍取消，未重启/更改parser或Claim。

此前记录：
2026-10-27 立即评测e015-qwen2-cleanvqa-e014-124shot-now-20261027已实际进入1shot模型推理：4副本均有输出，首次观察共62条，其中23条实际VQA选择全部合法；8GPU加载约9.0/11.4GiB交替。固定输入预检与9968项SHA核验通过，exit为空。后续按既定命令顺序2/4shot，尚无完整结果。GRPO已取消于115步，最近checkpoint100，不自动恢复。

此前记录：
2026-10-27 用户明确取消当前GRPO并立即评测。e015-qwen2-tier3-ddp8-full-20261027和旧等待e015-qwen2-cleanvqa-e014-124shot-20261027已精确SIGTERM、exit143/无残留，官方authorization fail/nonretryable；8卡释放，step50/100 checkpoint保留。独立立即Run e015-qwen2-cleanvqa-e014-124shot-now-20261027（dispatch-1a4159a9fd9b2d1e44fae7a0）已受管启动，直接复用已冻结1745查询/1727排除重合子集与1/2/4shot清单。取消等待依赖，不改科学配置；旧两项不恢复，GRPO后续自动评测取消。当前立即Run输入SHA复核/初始化阶段，尚未结果验收。

此前记录：
2026-10-27 更新：1/2/4shot固定候选输入已核验完毕，新Run已进入CPU事件等待；同1745查询，训练原视频重合18/图像路径及SHA重合0，另报排除后的1727。当前没有GPU推理结果；待正式GRPO及既定评测成功结束再运行。

2026-10-27 用户纠正为1/2/4shot全部评测，不做/报告多框子集。旧e015-qwen2-cleanvqa-e014-proposals1766-20261027仅等待进程已停止exit143，官方scientific fail（范围变更，无推理）。新e015-qwen2-cleanvqa-e014-124shot-20261027（dispatch-1f26c0a89994a8dd0ff0eac4）受管启动CPU输入准备：原1766排除21个不足5标注帧的TAO，同1745 Query×1/2/4shot，E014候选冻结不重生成，只增加新Qwen2 VQA参考；当前E015采样规则。全参考并集重新核训练重合；报总体/三数据集及排除重合子集，不报多框子集。准备后等待当前完整GRPO及其既定评测exit0、8卡空闲，48h上限；不暂停/恢复训练。尚无新推理结果。

此前记录：
2026-10-27 新Qwen2 clean VQA4172 × E014固定1766 proposal对照已受管排队：e015-qwen2-cleanvqa-e014-proposals1766-20261027（dispatch-a6f84698836c47ee8d3e6690）。当前仅CPU等待 e015-qwen2-tier3-ddp8-full-20261027及其既定评测exit0、8卡无compute进程后自动启动；48h超时或父非0则不启动。不暂停/恢复父训练。固定1shot/791多框，BF16/4×2GPU；18条LaSOT视频与新VQA训练重合、无图像路径/SHA重合，报告完整1766与排除后1748及分集/多框/旧VQA-score-Oracle对照。尚无新推理结果。

此前记录：
2026-10-27 用户重新明确授权完整训练，独立e015-qwen2-tier3-ddp8-full-20261027（dispatch-c70a2d98c912ae736d428a90）已受管启动。8×1GPU DDP、Qwen2、4shot、G4、新三档奖励/coverage最大0.1、同SFT636初始化；400更新、warmup4、save50，总采样较旧4副本400步翻倍。每步候选统计/峰值/副本一致性；训练后固定三数据集每shot1289的1/2/4shot proposal+clean VQA评测，BF16推理仍4×2GPU。当前仅启动验收，不宣称训练或评测完成。此前停止的两个Run保持停止。

此前记录：
2026-10-27 用户要求立即停止：原4×2 GRPO已停在18步；8×1 DDP试跑已停在4/8步（exit143），8卡显存各2MiB。所有训练/试跑停止，保留日志；不自动恢复、重试、评测或启动新训练。

此前记录：
2026-10-27：用户明确直接停止4x2三档GRPO（18步，尚无checkpoint）。独立e015-qwen2-tier3-ddp8-probe-20261027正在8卡单副本4shot/G4能力短测，保持分辨率和奖励，8更新。检查显存、跨8副本一致性、梯度和实际吞吐；不自动继承正式400步训练。

## 变量与对照
统一Qwen2-VL-7B-Instruct；4shot训练；推理shot数1/2/4，同Query与checkpoint。全套相对E014同时改变模型、视觉预算、训练设置和训练源集合，非单因子比较。

## 最小测试
既有8视频1/2/4shot短SFT与恢复、selector短SFT更新/哈希已验证，但Qwen2 legacy像素字段曾覆盖size，旧显存不能解释为4096预算。已修复共享预算与早期NCCL barrier；最新9项CPU回归通过（含真实处理器5图预算和Qwen3像素一致性），GPU8例VQA每例5图、实际4032rawpatch/图、8有效编号EOS。正式SFT逐batch新增actual-grid守卫。

## Baseline
E014原step200多框proposal+linear5388选择器；在共同1728 Query重算，不能直接用原1766全量均值对比。

## 处理组与消融
仅自有SFT+GRPO可变数量多框+独立VQA。无固定三框、无FOCUS attention loss/专有奖励、无额外FOCUS方法复现。

## 指标与混淆变量
proposal score mIoU/Acc50、Oracle mIoU/Acc50，VQA mIoU/Acc50、Oracle可命中但未选中数量、分数据集及多候选子集、有效编号EOS比例；工程记录峰值显存/更新数/有限梯度/副本SHA。

4shot均匀采帧含接近Query的支持帧，因此shot变化也改变时距；E014历史测试集已多次探索。源视频隔离不等同跨数据集像素去重。

## 风险与开放问题
共同清单训练10175/测试1728；原10524训练剔除305源视频重合、36越界标注、8缺轨迹；原1766测试剔除17越界、21缺轨迹。原GRPO另有26重合源视频，将在完整原始审计后整对/整ABBA剔除。

完整数据最长样本显存及GRPO rollout/update尚待实际阶段验证；多帧是否同时改善proposal覆盖和VQA实例选择尚未知。

## 资源预算
8×RTX3090，4副本每副本2卡。NF4/BF16/SDPA、10/18层切分、每图4096 rawpatch。SFT4epochs/global64；GRPO400updates/G4/global4pairs；selector4epochs/global16；测试1728×3shot。单seed，按实际日志记录时长，不承诺全链耗时。

## 人类预授权的自动审核策略
```json
{
  "enabled": false,
  "auto_review_on_create": false,
  "policy_version": "run-review-automation/v1",
  "notes": ""
}
```

> 默认关闭。策略只能由人类通过专用 Experiment UI/API 显式保存；自动审核不会执行命令，也不会修改 Claim verdict。

## 人类配置的 Execution Outbox 策略
```json
{
  "enabled": false,
  "auto_queue_on_authorize": false,
  "auto_deliver_on_pi_live": false,
  "claim_lease_minutes": 30,
  "max_delivery_attempts": 5,
  "notes": ""
}
```

> 自动排队不执行命令；自动派发仅向实时绑定的协调 pi 发送 Prompt，收到 Prompt 不代表 claim/ACK。

## 自由笔记（Obsidian）
这里可补充研究设计推演；工作台更新结构化方案时不会覆盖本节。
