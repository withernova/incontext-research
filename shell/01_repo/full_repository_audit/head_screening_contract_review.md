# Head筛选与干预源码审查（进行中）

基线：`1622e5f64a70239d02145f017cfd991cf8318e47`。已读公共probe/metrics/finder/hook、checkpoint/localization和head_criteria全篇；其余collector/干预/chain-rule/pruning/target-background尚未全覆盖。未运行测试或模型。

## Probe / metric / finder

- TeacherForcedDualSpanAttentionProbe按seed+screening_index抽无放回dataset indices，再rank-stride。读取SFT GT assistant suffix的bbox p-1 rows，不能冒充natural-response replay。bbox rows必须在supervised suffix中。
- 视觉span从image token连续区间得出，必须匹配image_grid_thw、T=1、merge整除与merged token count；Reference count明确校验。多Reference即使声明require_reference_count>1，当前保存map/GT只取first Reference、Query取last，不把它等同多Reference ensemble。
- eager模式临时替换attention implementation并还原；model training flag在finally恢复。selected模式转auto_query_heads.selected_probe_maps，该实现仍待下一步核对。两种方式是否数值等价没有本轮运行证据。
- 每sample保存q_to_q/q_to_r、Reference/Query fractional GT occupancy、span/row位置。浮点存储可选float16/32，是有损精度选择，不能称保存所有原始模型概率无损；failure记录与正常records分列。
- component_token_entropy是超过mean×multiplier的binary support上8连通component token count熵，不是attention概率熵、4连通或GT区域熵。无component返回inf，JSON展示为null。
- chord_threshold对排序后的mean span masses求最大到端点chord距离，N<=2返回min；不存在通用statistical significance含义。
- retained_mass_support先在span内归一化，stable降序取达到rho所需的最少token，ties偏固定flatten顺序。S50 fractional IoU使用fractional occupancy，并非连续bbox IoU或任意视觉resolution不变证明。
- R003:全样本head mean span mass做elbow gate、排除指定layers；逐sample eligible heads按component entropy/ID取per_sample，按frequency/ID排序固定head sets。该ranking不读取GT occupancy，但query bbox rows来自teacher forcing GT。
- T003:Reference entropy除log(grid cells)，reward=-entropy_weight×Hnorm+iou_reward_weight×max(0,S50-fIoU-iou_threshold)。在每sample全head reward排名后统计Top1/Top10；fixed sets只从出现过Top1的heads按Top1 frequency/ID取，unique不足明确raise。
- T003诊断ranking表另外使用Top1/Top10/mean reward/ID，多级tie顺序不同于fixed sets。不能只截diagnostic ranking前N来补造frozen selected_sets。
- Reference GT明确参与T003 discovery；R003QueryHeadFinder只走Query R003排序，但公共_load仍验证Reference target。gt_used_in_ranking=False不是输入完全不含GT。
- 若eligible maps全部uniform/empty threshold support，entropy可能全inf而仍按ID排序；1-cell grid entropy normalization也不具通常意义。当前未运行这些边界，不能据排序成功证明有效空间head；未来门槛须按版本/科研设计明确，不暗改原算法。

## Periodic lifecycle

- HeadScreeningHook的sample边界、resume history ahead拒绝、latest/history发布、两role Jaccard和stability、无自动phase transition见sft_distillation_contract_review.md。
- periodic改变screening_index而改变cohort，pipeline固定0保持抽样cohort；两种稳定性观察不可混称。
- failure summary先保存、随后raise。文件存在/summary completed、稳定candidate、科学因果定位三个层级不同。

## Checkpoint与生成边界

- head_screening/checkpoints.resolve_checkpoint只解析显式目录，不自动latest；核对LoRA类型、记录base path与当前base一致，提供adapter config/weights SHA。processor优先adapter旁/所属Run，再base。
- attach_checkpoint使用PeftModel.from_pretrained(is_trainable=False)，随后expected vs actual adapter state keys/shape/exact value校验，和普通checkpointing只查unexpected的A002不是同一实现。它仍不证明base模型文件字节相同或全部依赖兼容。
- localization.strict generated parser要求恰一bbox、匹配括号、finite/范围/正面积。不能将普通parse_box的宽松行为或A020覆盖到此接口。
- generation_prefix要求batch1、监督suffix在完整视觉span之后、assistant边界末尾准确、允许input keys白名单、无padding；序列键在assistant回答前裁切，保留图像键。未知键fail closed，GT只用于事后比较/明确诊断条件。
- paired_metrics区分natural generation IoU和teacher-forced IoU；无效框按0、坐标MAE仅两条件都合法时提供。当前helper假定传入target/boxes已由上层验证，不能将其当任意bbox验证器。

## A/B/C head criteria

- decodability从A frozen_input读取indices，使用train-fold feature mean/std和target mean来fit ridge，test fold不参与standardization；OOF residual计算整体R²，不是每fold R²均值。
- A021确认capture_head_outputs未按传入bbox rows取attention，只做whole-query-sequence A@V平均，而payload标签仍声称bbox p-1 row mean。尚无旧B Run受影响证据。
- 即使修正rows，teacher-forced GT prefix与自然行为不同，不能把线性可读性当因果steerability或held-out无GT定位能力。随机5fold没有在此模块按sequence group分组；是否跨sequence重复、源A cohort已防混杂，需读实际输入/显式记录，不补造泄漏结论。
- C当前实现从teacher-forced baseline预测box（不是函数docstring所称GT box）构造±shift高斯目标，保留目标head选中row的Query mass，重算A@V并看paired center displacement slope。clamp导致actual shifts不一定±名义shift，分母用actual span。
- 无法解析baseline、退化或不可用geometry/配对会跳过；fired count要求hook实际触发。逐head有效数可不同，CI/cohort不能凭排名表推稳定效果。
- A022确认全head零有效paired observations仍completed/exit0；null数值和skip计数保留，非完全隐藏。
- source/indices/候选ranking checkpoint与数据适用性、当前GT派生geometry和其他干预路径仍待下阶段cross-check。只读模型不等于不写输出；main独占work_dir并发布ranking/summary/failure。

## 已读测试定义（未执行）

`test_head_screening.py`定义8连通entropy、fractional S50、R003/T003 role/GT标签、span/subsequence及half-epoch/Jaccard。它不覆盖A021 bbox rows忽略、A022零有效C、真实PEFT/NF4/eager/selected等价、完整resume/manifest来源；不能用这些定义宣称全head模块通过。
