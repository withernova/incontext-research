# 公共评测与候选指标源码审查

基线：`1622e5f64a70239d02145f017cfd991cf8318e47`。覆盖当前`tools/evaluate.py`与bbox/confidence AP/multi/variable evaluators的公共链路；干预与auto heads内部仍待独立审查。不执行模型、测试或远端任务。

## 执行与来源

- 顺序是load_experiment_config→执行期resolve_evaluation_artifacts→validate_prepared_run→rank0 snapshot→动作专用校验→构造wrapper→视觉上限→adapter→dataset→选样本→分rank生成→gather→覆盖校验→指标与保存。
- metadata解析发生在snapshot之前，因此resolved snapshot记录实际恢复的四个标准LoRA字段；这不解决高级LoRA模式/张量完整性缺口A014/A002。
- 普通固定评测显式evaluation.checkpoint；named_run取resolved_resume_checkpoint。不能从当前Shell默认配置补造历史Run来源。
- configure_vision_limit用patch_tokens×patch_size²设processor.image_processor.size.longest_edge；这是原始patch-token像素上限，不是直接的merged语言visual token数量，也不是测得每个样本真实token数。
- 普通生成使用sample.messages[:-1]，剥离最终assistant GT；加载sample.image_paths对应图片并apply_chat_template(add_generation_prompt=True)。Variable dataset保留空assistant占位，Query GT不入生成消息。其他自定义dataset必须满足最后一轮assistant契约，不能把任意messages列表机械截尾。
- generate直接使用peft_model而非DDP wrapper forward，逐rank独立生成，传max_new_tokens/do_sample。seed只用于seeded_random选样本，普通worker没有为随机generation设置Torch seed；当前frozen greedy配方不能据此归为随机生成。
- native tools/infer.py是另一入口，不自动继承此worker的视觉/选样本/do_sample实现（A006）。

## 覆盖与异常

- head选样本取前limit；seeded_random用独立random.Random(seed)，抽无放回并排序。普通limit大于dataset时clamp，干预入口显式拒绝大于dataset。负/零limit拒绝。
- selected_indices[rank::world_size]决定分片；gather后按dataset_index排序，必须逐项等于selected_indices且ID去重数量等于total。这个门禁证明对当前dataset的覆盖，不证明输入SHA/原始冻结1766身份。
- 普通逐样本生成异常不转invalid继续；异常向外传播。rank0写失败事件时仅记异常类型，原异常仍raise；finally关闭distributed context。
- enriched rows合并原dataset/sequence/rank/index与evaluator逐样本输出。evaluation目录用exist_ok=False且predictions用open(x)，拒绝覆盖旧评测。metrics用同目录临时文件rename。
- 此目录没有事务级完成marker；中断可能留下partial predictions或缺metrics。只有目录/文件存在不等于complete。
- 干预完整性失败先保存audits/metrics(status=integrity_failed)再raise，不应该删除失败证据。实际是否进入干预仅由branch.action决定，普通launch.action缺口见A004。

## bbox、候选及GT边界

- box_iou先parse_box；返回None或零union时为0。但部分非法结构float转换会抛异常、非有限值也未明确拒绝（A020），不能把文档invalid=>0当所有输入都兑现。普通LocalizationEvaluator的parse_rate只表示坐标可解析，不是面积>0、严格回答格式或正确定位。阈值准确率/miou默认分母全部rows，invalid按0计。
- ConfidenceLocalizationEvaluator独立报告strict answer-score格式合法率，legacy bbox解析先隔离answer四坐标，避免将score作为第四坐标。bbox可用与strict format valid是不同字段。
- fixed multi parser允许1..max_candidates并拒绝任何malformed candidate/extra text；prompt要求exactly N，requested_count_compliance另报。因此合法率不等于exact count compliance。
- variable parser不设固定box count cap；至少一个完整严格pair，数量仍受生成token预算限制。Malformed整条无有效candidates；parsed count=0不等于raw answer opening数=0，raw_prediction必须保留。
- select_candidate只接收candidates的score，最高score且最早tie；GT不参与Selected。之后才计算各candidate IoU、Oracle和duplicate判据。
- First/Selected/Oracle三个口径不能混淆；全单框时逐样本相同是定义恒等，不证明ranking成功。duplicate是两预测IoU>=.9，不是已验证同一真实实例。
- variable spatial_order输出中心顺序逆序率；format合法不等于spatial_order有效。nonfirst_acc仅在earliest-argmax Oracle不是首框的合法样本上比较索引，含IoU最大值tie的earliest规则；不是tie-aware所有非首候选正确率或总定位准确率。
- per-dataset指标重新构造evaluator，分母为各dataset样本数；overall是样本加权，并非dataset等权macro。

## AP口径

- confidence_ap.interpolated_ap将相等score整组加入，避免量化score tie的任意行序；逆序precision envelope后对recall变化积分。不是11/101点插值，更不是完整多物体检测匹配。
- ap_metrics从每行strict单框confidence输出生成至多一条detection；invalid prediction不进入precision分母，但该GT仍计recall分母。AP50_95按10个IoU阈值均值。
- ap_metrics要求非空rows，但调用者需先用valid_target筛除无效/退化GT；函数本身不自动筛。total_gt必须是正确正整数，detections/score/IoU必须满足单目标调用契约。
- helper不做输入去重、多GT matching、负样本GT数量推导或来源coverage检查。不能脱离消费者门禁把它推广到任意检测列表。

## 未完成范围

- query_attention.py/auto_query_heads.py以及head干预内部仍未在本报告完成语义核对。
- Shared AP三个消费者的cohort/数据来源/异常与GT筛选还需逐个核对。旧AST算法等价不能替代本轮消费者审查。
- 当前没有新推理或真实AP结果；不改旧1766结果或科学Claim。
