# SFT / 蒸馏源码契约审查

基线：`1622e5f64a70239d02145f017cfd991cf8318e47`。只核对源码与测试定义；未运行测试、import、模型、GPU或远端任务。此报告不意味着全仓审查完成。

## 配置到实际更新

- `builder.build_training`先构造model、dataset/collator，再构造runner。因此runner设置seed晚于fresh LoRA初始化（A007）。普通配置声明到模型加载的跨层前提还受单rank DDP入口问题A001影响。
- Runner的有效预算：samples_per_update=batch_size×world_size×accumulation，updates_per_epoch=ceil(dataset_size/samples_per_update)。max_epochs非空优先，max_steps不会成为额外上限（A003）。
- `batch(micro_step)`按当前rank分段，取dataset索引模dataset长度，没有随机shuffle。非整除边界会重复样本；samples_seen是处理量，不是unique样本数。小于全局batch的数据也不能自动获得rank间严格互不重复的索引。
- 每次更新先zero_grad；pipeline使用已完成step数；逐microbatch将CE+辅助loss除以accumulation后backward。非最终microbatch在world_size>1时用no_sync。
- backward后、optimizer.step前核对跨rank均值loss及有限gradient比例，必要时clip(error_if_nonfinite=True)。FiniteHook在更新后再次检查，不能用这个Hook替代前置检查。源码存在前置门禁，但没有本轮故障注入运行证据。
- optimizer始终AdamW，只读取lr/weight_decay（A018）。LambdaLR仅warmup，不是线性/余弦衰减；ceil(max_steps×warmup_ratio)控制ramp。optimizer用本次记录LR，scheduler在step后准备下一次LR。
- teacher-forced localization按logits[t-1]预测labels[t]，只统计非-100标签；不等于autoregressive验证指标。assistant_only_logits只裁lm-head输出/labels后缀，不裁完整model input；必须保留最早监督位置前一个预测位置。

## 完成、保存和恢复

- 固定诊断batch来自当前训练dataset的batch(0)。pipeline情况下训练前后只比较CE，避免比较不同辅助权重；静态auxiliary情况下比较配置总loss。该诊断不是独立验证集。
- `passed`要求固定batch的loss下降、adapter_delta_norm>0及finite_grad_fraction=1。预算已跑完、门禁通过、泛化收益是不同事实。最终adapter会在门禁结论之前保存，目录存在不证明passed。
- hooks按priority排序：有限性、日志/GPU、history、metrics writer。history追加并fsync；最终metrics经同目录rename发布。GPU hook区分DDP local peak与single-process可见设备列表，不代表整个设备占用或其他进程峰值。
- checkpoint边界是处理样本数。超过边界后保存当前完整更新，不是精确停在target_samples；名字含目标样本边界，trainer_state.samples_seen才是实际已处理量。rank0拒绝已有checkpoint目录并写adapter+trainer_state，其他rank等待barrier。
- 该保存没有事务完成marker：进程中断可留下半写目录，不能仅凭目录存在作为可恢复证明。validate_checkpoint检查必要文件存在，adapter tensor完整性还有A002缺口。
- initialize_from只加载adapter，保留新的optimizer/step/history。resume_from恢复adapter、AdamW、scheduler、step/samples/history、pipeline状态；二者互斥。optimizer状态移动到实际参数device。
- SFT格式不保存/恢复逐rank RNG。saved seed/max_steps未做兼容比较，dataset/layout未绑定（A017）；不能称精确随机轨迹恢复。预算延长、warmup重算与恢复optimizer的规则需明确，不自动沿用E-014冻结恢复契约。

## Pipeline状态与筛选

- stages有从0开始的严格递增整数边界。completed_steps=83配置的stage用于update84。每次更新开始切换，不能在梯度累积中途切换。
- signature覆盖完整stages/screening声明；resume拒绝改变signature，保存stage_index、last_selection_step、active_loss_config和selection_source。restore后重建loss，不应把已冻结heads重新筛选；adaptive在下一refresh边界再筛。
- stage切换/refresh先关闭旧extractor hooks，再构造新loss。ramp fraction=(completed-start+1)/ramp_steps，第一步不是零权重。
- 筛选使用当前训练dataset，probe.collect的固定step参数0与固定抽样配置保持cohort；记录selection.json及pipeline_events。不能将其称独立test集或固定离线teacher。
- `_screen`保存/恢复Python、NumPy和实际model CUDA devices对应的Torch RNG；rank payload合并，由rank0选择并广播。失败被汇总为失败summary并raise，而不是静默保留旧heads。设备/实际probe模式行为未运行核验。

## 蒸馏输入、数学与梯度

- SampleGeometry要求恰好一个Reference与一个Query，T=1、grid可整除spatial_merge_size、visual token span与merged grid相等。bbox_token_positions转为p-1 rows；Reference GT用于occupancy。它不是自动支持2shot/video/任意视觉布局。
- SelectedAttentionExtractor记录选中Qwen3VLTextDecoderLayer的输入、position embeddings和mask。重算input layernorm→Q/K projection→Q/K RMSNorm→RoPE→GQA query_head//groups→scale/mask→float32 softmax后转query dtype。没有sequence²全部head矩阵，但仍有整段Q/K投影和选中row×key开销。
- mask=None时明确补因果约束，不解释为双向attention；有mask时按batch/选中rows取加性mask。验证layer属性和attention_dropout=0，拒绝缺失layer/非法head/row及nonfinite概率。
- 当前源码描述与目标Transformers实现一致性仍需真实版本测试。不能凭属性检查就声称所有版本、量化、SDPA/fused、checkpoint/DDP均数值等价。
- 每个head先对p-1 rows平均，再在Reference span内归一化，最后对heads等权平均。raw reference map独立等权平均，计算span mass与fractional occupancy object mass。形状分布不是raw mass归一化后再平均的替代口径。
- loss=coefficient×(KL(target distribution||student distribution)+smooth_l1(span mass)+smooth_l1(object mass))；先按sample平均，随后由Runner进行accumulation/DDP汇总。
- fixed teacher用已存maps；correct核验archived masses一致。cyclic_roll使用sample ID/seed决定非零同grid offset，同时滚distribution/raw map，span mass不变，object mass按原occupancy重新计算。不保证roll后完全离开GT。
- dynamic_teacher使用当前model Reference heads，target tensors detach；不直接通过teacher target反传，不等于冻结teacher模型，也不等于teacher部分参数永不通过其他student/CE路径获得梯度。
- gt_mask用Reference fractional occupancy归一化作为分布，span mass=1，object mass=sum(distribution×occupancy)。没有读取Query GT来构造该mask，也不需要teacher manifest；该辅助目标本身仍使用Reference GT监督。
- ConfidenceFormatLoss要求score值labels被mask，只对metadata给出的全部合法continuation token集合求负log概率质量；不是拟合指定confidence数值。因果predictor为position-1，支持suffix logits offset；不存在合法token集合/位置范围错误则raise。

## Periodic head hook依赖（筛选算法另审）

- HeadScreeningHook在更新后按samples_seen/当前dataset长度触发；超越多个sample边界时执行一次screen，再推进next boundary，不伪装每个越过边界都获得独立screen。
- before_run读取latest.json恢复screening index/previous sets/stability streak，拒绝latest.step高于恢复checkpoint的历史；与pipeline保存在trainer_state里的signature/selected heads不是同一契约。
- probe逐次使用seed+screening_index抽样，pipeline固定index0则维持固定cohort。两者不能混称固定筛选样本。
- probe临时eval/eager并在finally恢复原training flag和attention implementation；部分sample错误保存failures，hook聚合后写failed summary再raise，不自动切训练phase。
- stability需Query和Reference sets对上次Jaccard都达阈值，stable_candidate仅作候选标签，automatic_phase_transition=False。不证明head具有因果定位功能。
- finder内部的排序、null校准和GT使用仍归下一阶段审查；本段不是筛选算法全通过。

## Dataset / collator / score grammar依赖

- IPLocManifestDataset读取一个或多个JSON list，可选逐manifest SHA及dataset_names筛选；缺请求dataset或零target rows会拒绝。记录角色缺省为前面Reference、最后target_role；path/box/role数量必须一致。此legacy缺省是输入约定，不是已证明原标注身份。
- bbox被当作pixel xyxy，读实际image尺寸后按normalized_scale转为紧凑文本。默认1000与prompt一致；自定义scale必须另核对prompt、parser/评测单位，不能把参数存在当整链支持证明。ID是筛选后record_index-target_index，不是稳定全局图像身份；更换cohort/输入可复用同ID（A019相关）。
- focus_confidence的score placeholder取query_path SHA对应101个合法值之一，与bbox质量无关。训练mask score数值，bbox/格式suffix仍CE；该占位不是校准真值。修改路径也会改变占位上下文，不是完整相同输入证明。
- collator分别渲染prefix/full，同图经过processor并验证prefix input IDs是full前缀；唯一answer token subsequence限定在assistant suffix，避免误对齐Reference同文本。
- bbox_token_positions包含整个bbox answer字符串；coordinate_token_positions另按四个数字field的offset映射，拒绝token跨多个数值field。不要混淆bbox span与纯数值坐标token；不能拆开跨界BPE概率。
- 最终batch根据attention_mask有效索引重映射位置，支持左右padding。labels先全部-100，再填assistant suffix；assistant_only=False无分支（A012）。score数值专门-100，metadata保留合法continuation集合/视觉grid/原始patch数量。
- score grammar枚举0.00..1.00共101路径，拒绝空/重复/非prefix-free编码；实际rendered score必须等于其中一条路径，且score token不得跨格式字符。每位置合法集合只依据此前数值token前缀，不指定某个score值。
- 公共parse_box宽松结构处理仍有A020转换失败/非有限缺口；strict confidence parser明确finite、0..1000、面积>0及严格两位小数，不是相同契约。
- 本轮尝试读取旧称datasets/collators.py返回ENOENT；实际实现是datasets/collator.py。没有据此登记缺失模块问题。

## Teacher目录与来源风险

- precompute按dataset_index从rank步进world_size分配，模型eval/inference_mode，提取后按完整ID/index coverage finalize；不是每rank重复全量。
- NPZ记录保存distribution/raw map/occupancy/masses，manifest保存heads/checkpoint/source_manifest路径、geometry与NPZ SHA。FixedTeacherStore检查ID集合、SHA、head列表、shape/finite/occupancy和normalization。
- 但partial resume没有绑定原teacher/input身份，旧NPZ可以被赋予本次身份并混用（A019）。消费端的同ID/同几何也不证明相同图像、prompt、processor或checkpoint条件。哈希完整性与来源适用性必须分开。

## 已读测试定义及缺口（未执行）

- `test_repository_training_safety.py`定义非写rank可以join已建目录、非有限loss/gradient/clip norm在optimizer前abort等；这不是本轮DDP/GPU运行证据。
- `test_training_pipeline.py`定义stage/refresh/ramp、fixed/adaptive resume、signature拒绝改变、GTmask梯度、RNG保存、真实tiny Runner accumulation边界和CE-only loss gate。
- `test_attention_distillation.py`定义与安装Qwen eager比较、mask=None因果、ensemble口径、teacher hash/geometry roundtrip、loss累积及dynamic target detach。仍未定义partial teacher来源改变、同ID同geometry输入内容变化或SFT layout漂移反例。
- `test_assistant_only_logits.py`定义suffix/full CE及lm-head/hidden梯度等价、空监督拒绝和teacher-forced IoU口径；是简化causal CE，不是安装Qwen模型集成证明。
- `test_coordinate_token_alignment.py`用char tokenizer与whole-answer token反例定义数字field/标点分离和跨field拒绝，并用patch.dict恢复stubs；没有证明真实tokenizer所有边界案例。
- 单机tiny/eager定义不覆盖真实8B/NF4/PEFT/非重入checkpoint/DDP；未执行任何这些测试。
