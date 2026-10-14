# 全仓审查问题（初步，继续审查中）

基线：`1622e5f64a70239d02145f017cfd991cf8318e47`。下列位置相对代码仓库。`source_confirmed` 表示源码链路核对，不表示实际运行已复现。尚未运行测试、模型或远端任务；不据此否定历史已完成 Run 的结果。

优先级：P1 为可能阻止任务或使参数/科学动作失效的重要问题；P2 为可达接口缺陷、复现或维护风险；P3 为低风险维护建议。优先级不是科学收益判断。

## A001 — P1 / source_confirmed：单进程 DDP 配方未使用 torchrun

- 证据：`iploc_szy/launching.py:63–71` 只在 `nproc > 1` 时加 `torch.distributed.run`。`iploc_szy/utils/distributed.py:29–34` 在没有 RANK/LOCAL_RANK 时直接返回未初始化的 context。`iploc_szy/models/qwen3vl_lora_ddp.py:110–115` 无条件构造 `DistributedDataParallel`。
- 当前配置：`configs/sft/qwen3vl_8b_lora_focus_1shot_single.py`、`...single_4bit.py`、`...2shot_single.py` 均继承 `Qwen3VLLoRADDP`，并声明 `launch.nproc_per_node=1`。其中的注释明确要求 torchrun 单 rank。
- 当前 Shell：`tools/run/train/train_focus_1shot_single.sh`、`train_focus_1shot_4bit.sh`、`train_focus_2shot_single.sh` 都转发公共 launcher，没有补 torchrun。
- 触发：正常非 torchrun 环境，通过上述维护中的入口启动单 GPU 配方。CUDA 存在时也没有进程组；DDP 构造需要已初始化的组。不能把 nproc=1 自动等同于“不需要 torchrun”。
- 影响：在模型加载后失败；当前单卡快捷入口不能兑现其配方契约。共享候选评测若改为单 rank 且保留 DDP 模型，也有同类风险。
- 建议：显式区分进程数与是否需要 distributed envelope。保留单 rank DDP 契约，或明确支持非 DDP wrapper；不要在没有核对目录/模型行为时随意切模型。
- 测试边界：`tests/test_launch_contract.py` 检查 nproc 数值和快捷入口参数，但没有验证单 rank DDP 的 worker command 与进程组前提。未执行这些测试。

## A002 — P1 / source_confirmed：adapter 加载只拒绝 unexpected keys，未检查缺失 adapter 张量

- 证据：`iploc_szy/checkpointing.py:32–57` 调用 `set_peft_model_state_dict` 后仅检查 `unexpected_keys`；不存在 required adapter key 完整性检查。此前校验只要求文件存在。
- 触发：safetensors 文件可读取，但缺少一个或多个预期 LoRA 张量，并且其余 keys 没有 unexpected key。
- 影响：缺少的参数可继续保留 wrapper 的初始化值。评测或 SFT 初始化/恢复调用此共享接口时，可能把混合参数当成目标 checkpoint，后续样本覆盖/有限值 gate 不能证明 adapter 完整。
- 限制：未读取实际权重，也没有证据说明旧 checkpoint 已损坏。PEFT 返回的普通 base-model missing keys 不能全量当错误；必须区分应缺少的冻结 base 与必须存在的 adapter 参数。
- 建议：比较预期 adapter 参数集合与已加载集合，并检查 shape/finite、必要配置兼容。不能简单地对所有 `missing_keys` 非空报错。
- 测试边界：当前路径校验测试使用占位文件，仅证明 subdir 约束；没有缺少 LoRA 张量仍通过加载的反例定义。未执行模型或加载测试。

## A003 — P1 / source_confirmed：同时存在 max_epochs 时，max_steps 覆盖静默失效

- 证据：`iploc_szy/engine/runner.py:109–120` 用 `ceil(max_epochs * updates_per_epoch)` 优先生成 max_steps；只在 max_epochs 为 None 时采用传入 max_steps。构造器允许两个字段同时非空。
- 触发：对具有 `runner.max_epochs` 的普通 SFT 配方设置 `runner.max_steps=7`，或对 branch 设置 `runtime.runner.max_steps=7`，但没有另设 max_epochs=None。
- 影响：CLI/config/snapshot 可以显示用户传入的 max_steps，但执行预算仍由 epochs 决定。短任务可能消耗远超预期的 GPU 时间。
- 当前例：focus single 配方有 max_epochs=12，四卡 NF4 配方沿继承链保留该字段；E-012 配方也显式 max_epochs=3。
- 建议：明确互斥或明确取较小预算，并在实际执行前展示有效预算。若保持 epochs 优先，也必须拒绝冲突覆盖或明确提示，不能静默丢弃。
- 测试边界：现有 launcher 测试只确认 runner.max_steps 覆盖进入命令/配置，并没有核对 Runner 的有效预算。未运行任何训练。

## A004 — P1 / source_confirmed：普通 launch.action=attention_intervene 被 worker 当成 baseline evaluate

- 证据：`iploc_szy/launching.py` 的 WORKERS 支持 `attention_intervene`，普通 launch section 可选择它。`tools/evaluate.py:142` 仅用 `branch.action` 判断是否启用干预；缺 branch 时始终 False。
- 触发：普通评测 recipe 声明 `launch.action='attention_intervene'`，并给定 attention_intervention，而不是 branch recipe。
- 影响：不会运行干预比较，也不会运行干预专属完整性 gate；走普通 baseline 评测。公共 launcher 的动作与 worker 实际科学动作不一致。
- 限制：当前现成 attention branch 配方具有 branch.action，不受这个特定条件影响。没有证据说历史 branch 干预未执行。
- 建议：共享同一有效 action 解析，或在入口明确拒绝不受支持的非 branch 干预配置；不能让动作静默退化。

## A005 — P2 / source_confirmed：普通 named_run 的非训练动作被标为 train

- 证据：`iploc_szy/branching.py:223–233` 的 branch_summary 默认 train，不取 launch.action；`run_management.py:295` 和 validate_prepared_run 也只看 branch.action。`tools/run_branch.py` 用该 summary 准备动作和内部 override。
- 触发：普通 recipe（没有 branch）同时设置 named_run 与 `launch.action='evaluate'` 等非 train 动作。公共 `uses_named_run` 明确接受这些动作。
- 影响：manifest/log/action 可变成 train；adapter-only 评测来源会因为错误的 train 路径而要求 trainer_state.pt；还会注入不必要的 runner 初始化字段。worker_command 却根据 launch.action 选择评测 worker，构成跨层不一致。
- 建议：动作解析只保留一份。非 branch named-run 支持哪些动作，要用显式校验和契约测试约束。
- 测试边界：`test_named_plain_recipe_passes_effective_config_to_worker` 仅覆盖普通 train/new、train/resume；分支 evaluate 测试不能覆盖这一组合。

## A006 — P2 / source_confirmed：native infer 配方中的评测参数没有落实

- 证据：`configs/_base_/e011_frozen_eval.py` 声明 vision_max_patch_tokens=2048、do_sample=False、selection、seed。`configs/eval/qwen3vl_8b_native_grounding.py` 选择 infer worker。`tools/infer.py` 只使用 limit/max_new_tokens/adapter，generate 只传 max_new_tokens；没有调整视觉上限，也没有传 do_sample。
- 当前影响：源码声明的 native 2048 上限和显式 greedy 设置没有成为执行约束。实际行为取决于 processor/model 的默认配置，而 adapter evaluate worker 明确调整视觉上限并传 do_sample。
- 限制：未检查实际模型 generation_config/processor 配置，不能据此断言历史 native 运行一定抽样或一定使用某个像素上限。
- 附加接口风险：若将 selection 改为 seeded_random，infer 仍读前 limit 行，seed 不参与该选择。
- 建议：通用生成/视觉上限/样本选择在执行期复用同一职责实现，或拒绝/去除不受支持的声明。保存实际使用的生成与视觉配置，区分 native 与 adapter 的真实预算。

## A007 — P2 / source_confirmed：SFT seed 在 LoRA 初始化之后才设置

- 证据：`iploc_szy/builder.py:13` 先 MODELS.build，wrapper 内调用 get_peft_model 创建 LoRA；Runner 之后才构造。`engine/runner.py:_prepare_run` 才调用 `_set_seed`，其注释却说保持 initialization reproducible。
- 触发：从 base model fresh 初始化，未加载固定 adapter，且调用者没有提前设置 Torch RNG。
- 影响：runner.seed 控制后续训练随机性，但不控制此前 LoRA 初始参数。DDP 广播可使本次各 rank 一致，不能使不同 fresh Run 的初始化由同一个 runner.seed 重现。
- 限制：从完整固定 adapter warm-start 的分支可覆盖初始随机权重；不应把这条问题推广到所有历史训练。GRPO 使用独立 policy 初始化链路，尚未在本条中评价它。
- 建议：在 model 构造之前设置有效 seed，且记录初始化来源与初始状态摘要。这会改变未来 fresh Run 的初始化，应明确版本化，不能冒充纯目录重构。

## A008 — P2 / repository_hygiene：793 个历史检查/备份产物被 Git 跟踪

- 证据：当前 git ls-files 中 `.task-backups` 273 项、`.task-checks` 520 项；包含测试临时配置/快照、run_index/锁、checkpoint 占位文件和软链接。`.gitignore` 未覆盖这两个目录。
- 影响：当前源码、历史测试副本和产物混在同一 Git 清单，扩大 clone/审查/导航范围，容易把旧快照当实现或验证证据。后续新增检查也有继续纳入 Git 的风险。总大小约 3.67 MB，不是声称有大型真实模型权重；81 个跟踪软链接均解析到代码仓库边界之外，本次没有跟随读取。
- 限制：这些目录不在当前配置导航扫描入口中；不声称会自动执行、安装入 package、泄漏凭据或包含真实模型权重。未执行检查产物代表的历史测试。
- 建议：先核对保留/溯源需求，再制定归档与 Git tracking 策略；添加未来产物 ignore。不能自动删除这些文件或改写已发布历史。

## A009 — P2 / source_confirmed：单卡 sensitivity Shell 的 --inspect 仍创建输出

- 证据：`tools/run/analysis/e013/e013_reference_sensitivity_probe.sh` 在任何 Python inspect 分支前执行 mkdir -p "$RUN"；默认列表模式还用重定向创建 checkpoints.json。只有随后调用的 Python 检查 --inspect。
- 触发：使用该 Shell 的 --inspect，不论目录模式或默认 checkpoint 列表模式。
- 影响：Python 不加载模型不等于 Shell 整体只读。计划查询也会留下新 Run 式目录；默认模式写一个配置文件。
- 限制：这个旧单卡 CLI 的 inspect 明确还检查 manifest/checkpoint 并构造 dataset，不是通用 launcher 的纯源码模式。八卡新 Shell 不执行上述 mkdir；不能把问题推广到全部 inspect 接口。
- 建议：明确区分纯源码计划、只读输入 preflight 和正式执行；Shell 先识别 inspect，再决定是否创建 Run 输出。

## A010 — P2 / source_confirmed：单卡 sensitivity 在所有样本无效时仍 exit 0

- 证据：`tools/analysis/run_e013_reference_sensitivity.py:1007–1050` 将逐样本异常转为 valid=False，并在写 summary/Markdown 后无条件返回 0。summarise_checkpoint 支持 n_valid=0/null，但 main 没有有效样本 gate。
- 触发：一个或多个 checkpoint 的样本全部未通过候选解析、token span 或重放等检查；比如生成只有一个候选，而探针要求固定三个。
- 影响：原始结果确实记录 n_invalid 和原因，但成功退出码不能代表有可用探针证据。上层只看 exit 0 或 summary 文件存在可能错误完成任务。
- 限制：不能称为“完全隐藏错误”，因为 JSON 记录了无效数/原因。历史单卡任务状态未知，不补造其失败。八卡版本已有独立有效性门禁，后续还需逐行核对其覆盖。
- 建议：有数据但无证据的情况用明确 degraded/failed 状态和非零退出；保留原始无效记录。部分有效时同时报告分母和共同 cohort。

## A011 — P3 / source_confirmed：单卡探针“坐标 token LP”的名称比实现更窄

- 证据：CANDIDATE_RE 的 group 1 包含整个 [x1,y1,x2,y2]；candidate_spans 使用 match.span(1)，再将全部重叠 token 纳入 bbox_logp。方括号/逗号等格式 token 也可能被纳入，不只是四个数值字段。
- 影响：当前量是 bbox 字符串的 token log-probability，不能不加说明称为纯数值坐标 token 的概率。遮蔽差值也包含这些格式 token 的条件概率变化。
- 限制：这不自动使统计量无效，也不证明报告数值错误。BPE token 可能跨字段边界；不能强行拆一个 token 的概率。
- 建议：优先精确命名现有口径，保存实际选中 token/字符边界。若另做纯坐标字段口径，须明确 token 重叠规则和科学变化，不能静默换算法。

## A012 — P2 / source_confirmed：collator 的 assistant_only=False 不改变标签

- 证据：`iploc_szy/datasets/collator.py` 构造器保存 self.assistant_only，但 __call__ 始终将 labels 全部置为 -100，再只填 assistant suffix；没有读取 assistant_only 的条件分支。
- 触发：显式配置 collator.assistant_only=False。
- 影响：参数进入配置快照，但不产生预期的 supervision 切换。当前默认 True 的行为不受影响；不能声称现有训练实际用了 full-text CE。
- 建议：若只支持 assistant-only，就明确拒绝 False；若增加其他监督范围，应作为科学变化实现和验证，不借审查自动改变默认目标。

## A013 — P2 / source_confirmed：冻结评测把生产完整性门禁写成 assert

- 证据：`tools/run/analysis/e014/e014_step800_eval1766_8gpu.sh` 的两段 Python 用 assert 检查 Git/GPU、源清单 SHA/1766 数量、训练 prompt/checkpoint step、只读来源未变、预测覆盖、实际快照及 prompt。
- 触发条件：Python 以优化模式执行时，assert 不保留。当前 Shell 未显式确认这些生产校验仍启用。
- 影响：worker 自己的 dataset/coverage 校验只证明对当前输入完整，不等价于原 frozen 数据/step/source 绑定。最后 result.update 还固定写 evaluated_samples=1766；失去 assert 时，这个数字不再受真实行数约束。
- 限制：没有证据说明历史运行开启了优化模式；正式 Run 的外部批准/授权门禁与这些来源校验不是一回事，不能据此声称外部授权已被绕过。
- 建议：生产来源、资源和完成性检查用显式 if/raise；固定覆盖数应来自已校验的实际结果。测试中的 assert 与生产输入门禁必须区分。

## A014 — P2 / source_confirmed：checkpoint 元数据只恢复四个 LoRA 字段，未拒绝其他模式

- 证据：`evaluation/runtime_config.py:resolve_evaluation_artifacts` 仅恢复 r/lora_alpha/lora_dropout/target_modules；`models/qwen3vl_lora_ddp.py` 构造 LoraConfig 仅传这四项、task_type 和固定 bias=none。普通 adapter loader 也不比较实际 adapter_config 与构造出的配置。
- 触发：开启 lora_from_checkpoint，并给定含非默认 alpha_pattern/use_rslora 等额外模式的 checkpoint；或者手动在 model.lora 中声明这些字段。
- 影响：额外字段不会进入构造，也不会在 metadata 阶段被明确拒绝。张量形状相容并不能证明原计算路径相同。支持标准 LoRA 不等于支持任意 PEFT 配置。
- 限制：未证明 SFT659 或当前历史 checkpoint 使用这些模式；没有运行任何高级 PEFT 测试。涉及新张量/不同 shape 的模式还可能在底层直接失败，不能一概声称所有高级模式都会静默通过。
- 建议：先限定并验证本实现支持的 metadata 子集；不支持的非默认字段 fail closed。需要新能力时复用 metadata/模型职责层显式扩展，不把科学计算变化夹进路径整理。`rl/policy_resume.py` 已对 rank_pattern/alpha_pattern/use_rslora/use_dora 等做配置一致性核对，可复用其严谨原则，但恢复和评测契约仍需区分。

## A015 — P2 / scientific_design_risk：E-013 multi3 与 rank 配方没有构成 rank 开关差异

- 证据：`configs/experiments/E-013/training/e013_multi3_branch.py` 没有设置 rank_weight=0；`rl/multi_candidate.py:multi_reward` 默认 rank_weight=.5、rank_margin=.1、rank_iou_delta=.1。`e013_multi3_rank_branch.py` 显式设置的正是这三个默认值；显式 group_size=4 也已由共同父配方提供。
- 影响：这两个配置在所声明训练参数上的差异是名称/说明与显式写出默认值，不是关闭/打开候选排序奖励。不能将其历史结果差异当作 rank 单因素消融。
- 限制：这是已在旧 E-013 algorithm audit 记过的风险，本次将其纳入当前全仓覆盖，不冒充新发现。没有声称实际模型权重或历史数值完全相同；硬件、非确定性、实际 CLI 和执行版本仍需真实记录核对。
- 建议：历史结果标明有效默认参数与结论边界。未来若需要 rank 消融，使用明确且经批准的不同参数/预算/seed 设计；不能在审查中偷偷将旧 baseline 改成 rank_weight=0。

## A016 — P1 / source_confirmed：迁移后的两个 head-circuit Shell 少回溯两级目录

- 证据：`tools/run/analysis/e012/e012_head_circuit_path_patching.sh` 和 `e012_head_circuit_zero_attention.sh` 都用 `dirname(BASH_SOURCE)/../..` 计算 ROOT。现在所在目录是 tools/run/analysis/e012，回溯两级得到 tools/run，而不是代码仓库根。
- 触发：从维护中的新路径或旧转发 alias 调用这两个 Shell。
- 影响：cd/PYTHONPATH 指向 tools/run；相对 configs/experiments/... 也在错误位置寻找。即使外部 PYTHONPATH 使模块可导入，config 路径仍不成立。bash -n 成功和导航目标存在不能检查这个问题。
- 限制：没有运行这两个脚本，没有判断历史旧路径版本受影响。其他 E-012 Shell 使用固定 PROJECT 或不同 helper，不可一概归为同一个相对目录问题。
- 建议：复用已有 repo-root/launcher helper，或按实际新目录验证回溯层级。不要只修改导航表掩盖实际 cd 路径。
- 后续源码修正（不改变本报告基线）：2026-10-13 入口分层提交 `982553de383bf58ed771428f8b34aaf65a7e381c` 将这两个 ROOT 改为 `../../../..`，物理路径静态核对指仓库根。审阅 `4f135af8d694a648` 通过；未执行 head-circuit 分析、未重算历史结果，实际运行恢复未验证。详见 `shell/01_repo/directory_layering_20261013.md`。

## A017 — P2 / source_confirmed：SFT resume 校验身份/进度，但未校验数据与训练布局一致

- 证据：`engine/runner.py:_save_checkpoint` 保存step/samples/seed/max_steps/optimizer/scheduler/pipeline，却不保存dataset SHA、world size或batch/accumulation契约。restore只校验格式、pipeline signature和step<=当前预算；saved seed/max_steps没有兼容性比较。`run_management.py` 的resume分支只核对experiment/run/checkpoint所属目录和初始化指向，不比较有效训练配置。
- 触发：同一named Run resume时改变manifest/其内容、batch_size、world_size、accumulation或seed，仍满足路径和预算门禁。
- 影响：batch(micro_step)按当前布局与恢复step重新计算数据索引，旧samples_seen却原样继承；数据轨迹和进度口径可不一致。新snapshot记录新配置，不等于运行已检查其与原段兼容。optimizer/scheduler加载也可能覆盖用户填写的配置值。
- 限制：SFT源码已明示没有逐rank精确RNG恢复，不把该已知限制伪装成新实现缺陷。无证据表明历史恢复发生了配置漂移。延长预算可作为显式设计，但不是无条件允许所有训练条件漂移。
- 建议：明确固定字段/可变字段及预算延长规则；记录来源配置、输入摘要、布局与恢复段。改变数据/优化方案时优先新branch warm-start。不得在审查中机械套用E-014冻结8rank/step100契约或暗改旧恢复行为。

## A018 — P2 / source_confirmed：SFT optimizer 配置只读取 lr/weight_decay，其他字段静默忽略

- 证据：`engine/runner.py:__init__` 接受optimizer mapping，始终构造torch.optim.AdamW，只取lr和weight_decay；没有未知key校验。CLI与config合并会保留type/betas/eps/amsgrad等键并写入resolved快照。
- 触发：显式设置这些未实现字段，或误拼已支持的键。
- 影响：声明的优化器/超参数不等于实际执行值，可能使比较或复现误读。当前已有配方只用lr/weight_decay，不据此声称旧Run实际用了错误优化器。
- 建议：限定支持字段并拒绝未知键；若增加可选优化器，作为独立能力扩展并记录实际class/defaults。不能为了修复审查问题自动改变已有AdamW默认行为。

## A019 — P1 / source_confirmed：teacher partial-resume 没有来源绑定，可将旧 maps 标为新 teacher

- 证据：`attention_distillation/precompute.py` 只拒绝已有manifest.json，允许继续含records/的目录。`load_teacher_record` 对已有sample_index.npz核对有限值、shape、occupancy、归一化和mass，但数组不含原sample_id、checkpoint、heads或输入摘要；返回记录的sample_id/geometry直接来自本次参数。`finalize_teacher_manifest`随后把所有记录登记到本次checkpoint/teacher_heads/source_manifest名下。`tools/precompute_e009_reference_teacher.py`和launcher也没有核对旧partial目录的来源身份。
- 触发：第一次precompute留下部分NPZ、尚无manifest.json；用另一个checkpoint/head集合，或同geometry但改变图像/样本身份的输入，在同一output_dir再次执行。
- 影响：已有记录可被复用而不经本次模型计算，新旧maps可混在一个被标为新来源的manifest中。逐文件SHA只能确认实际数组字节，并不能证明这些数组来自manifest声明的teacher。
- 消费端边界：FixedTeacherStore核对schema/heads/sample IDs/NPZ hashes及几何，不核对当前训练图像内容、prompt token全文或manifest输入摘要。因此同ID/同几何也不是相同模型输入证明。
- 限制：没有证据说明历史teacher目录发生了此类混用。当前geometry与NPZ完整性校验仍有作用，不称其完全没有校验。不是DDP重复全量或运行复现。
- 建议：partial目录创建时绑定checkpoint权重/config、heads、source manifest与实际模型输入/视觉处理指纹；每条记录绑定sample身份和输入。恢复必须核对原绑定，不能在finalize时用当前声明重新标注旧数组；消费时核对适用输入契约。改变teacher或输入应使用独占新目录。
- 测试缺口：test_teacher_store_is_one_to_one_hashed_and_geometry_fail_closed仅定义同来源roundtrip与geometry不符，未覆盖partial目录来源改变且同geometry仍通过的反例。测试未执行。

## A020 — P2 / source_confirmed：宽松bbox parser 对部分非法结构抛异常，而不是返回None

- 证据：`prompting/coordinates.py:parse_box` 对四元素list/two-point list直接float转换，没有捕获ValueError/TypeError，也没有finite检查。字符串成功json.loads/ast.literal_eval后递归进入同一分支。`evaluation/bbox.py`的box_iou/LocalizationEvaluator依赖invalid=>None/IoU0契约。
- 触发：普通bbox评测收到可解码JSON但坐标含null/非数值字符串等非法输出；或坐标为非有限值。前者不是返回None，而是转换异常。
- 影响：普通evaluate worker先收集全量生成结果、再调用evaluator，随后才创建predictions输出。一个此类输出可导致整批指标计算退出且尚未保存逐样本predictions，不能按invalid=0 IoU统计。非有限坐标也不被parse_box明确拒绝。
- 限制：focus_confidence严格parser有独立finite/范围/面积门禁，不能把问题推广到所有候选评测。源manifest非法GT主动fail是合理行为；本条关注公共parser声明和对非法生成结果的处理契约。未运行反例，没有证据说明旧结果曾触发。
- 建议：公共parser显式处理转换失败/非有限坐标，区分结构解析与严格几何有效性；保留原始生成输出与invalid原因。不要借修复改写历史宽松free-text取前四数的科学口径。

## A021 — P1 / source_confirmed：decodability的head-output capture未使用bbox rows

- 证据：`head_screening/head_criteria.py:capture_head_outputs(model, rows, store)`接受rows，但intercepted中直接对attention[0]整个query序列做einsum("hrk,hkd->hrd",...)，随后picked.mean(dim=1)，没有按rows索引。run_decodability传入probe的bbox p-1 rows，输出probe标签却写teacher_forced_bbox_pminus1_row_mean_A_times_V。
- 触发：运行该模块decodability模式，输入序列除bbox预测rows外还有其他token（正常Reference/Query prompt即满足）。
- 影响：ridge特征实际是全query sequence的每head A@V平均，不是所声明bbox预测rows平均。R²和head排序可以对应另一读出对象；不能把标签当实际提取事实。
- 限制：未执行该模块、未核验旧B实验执行版本或结果。命名/文档意图不代表历史已按这段当前源码运行；steer_rows是另一函数，本条不自动推广到C模式。
- 建议：显式核验并只选择声明rows，保存实际row indices/数量。建立非bbox rows具有不同输出值的反例；若保留whole-sequence口径，应另作版本化诊断并改实际标签，不静默替换旧结果。

## A022 — P2 / source_confirmed：steerability所有head无有效配对时仍completed/exit0

- 证据：`head_screening/head_criteria.py:run_steerability`对未解析/退化baseline、不可用geometry或无法形成正负配对的样本跳过；每head空slopes写samples=0/slope_mean=None等，但最终payload.status固定completed，main成功路径return0，没有最低有效配对门禁。
- 触发：所有候选head的所有样本都无法形成有效±shift配对；例如baseline全invalid或全部geometry不满足。
- 影响：可发布没有任何有效steerability观测的成功状态。null与skipped计数确实存在，不能称错误完全隐藏；上层只检查exit/status会误把产物存在当有效证据。
- 限制：未运行或证明历史C结果为零有效。不同head的有效sample集合也可能不同，比较必须报告各自/共同cohort，不自动把部分缺失判为训练失败。
- 建议：区分完成计算与有可用科学证据；无有效配对明确degraded/failed并记录原因，按预设最小有效数和共同cohort判断比较是否可解释。保留失败/null产物，不补造slope或静默删样本。

## A023 — P2 / source_confirmed：Query干预的native A@V误差只记录、不参与完整性门禁

- 证据：`evaluation/query_attention.py:QueryAttentionHook._interface`计算native_head_output_max_abs_error，实际写回采用native output + (modified recomputed A@V - original recomputed A@V)。generate_comparison完整性只检查no-op tokens/logits、head-step覆盖和自产生的map alignment，没有检查该native误差。no-op的AV delta按构造恒为零，不能独立检验重算A@V与backend一致。
- 触发：原backend A@V与重算A@V出现超出容许数值误差的差异，但no-op输出不变、map alignment及coverage通过。
- 影响：仍可标integrity_passed，而gt_align写回不能被证明等于替换原backend相应概率后的A@V。记录误差字段不是拒绝不兼容计算路径的门禁。
- 限制：未运行eager/SDPA/量化或证明实际误差超标；正常数值roundoff不应一律当失败。该问题是验收条件缺口，不声称现有GT干预结果全部错误。
- 建议：明确native重算误差的绝对/相对容差与finite gate，并区分map alignment、query/row mass、native AV一致性。保留原AV-delta设计以避免no-op引入roundoff，不静默替换科学算法。

## A024 — P2 / source_confirmed：显式Top10 samples分支未将冻结GT与当前dataset标注核对

- 证据：`head_screening/top10_head_ablation.py:validate_spec`仅要求samples的target_box_source='annotation'、bbox几何有效、ID/index唯一及文件SHA。execute显式samples分支核对sample_id/dataset，但没有把frozen.target_box与dataset.query_answer派生标注比较；直接用frozen.target_box计算paired_metrics。source_run_dir分支则从当前dataset.query_answer生成target_box。
- 触发：显式samples文件有同ID/index/dataset但错误的正面积target_box，且声明/输入文件SHA都与当前配置一致。
- 影响：可将有效但不是该样本标注的bbox当annotation GT发布定位指标。哈希确认文件版本，不证明target_box_source声明属实。
- 限制：仅显式samples接口，不推广到已从dataset派生GT的source_run_dir分支。没有读取或证明历史samples文件错误，也没有运行反例。
- 建议：执行前逐样本核对冻结GT与固定dataset标注（含scale/rounding规则），保存实际来源。若设计确需替代GT，必须明确诊断协议而非沿用annotation标签；不重写历史结果。

## A025 — P2 / source_confirmed：FineReadout hook设置失败时没有恢复global eager函数

- 证据：`head_screening/pruning/hooks.py:FineReadoutZeroHook.installed`先替换implementation.eager_attention_forward，再解析vocab/查找唯一embedding/注册tracker hook；这些步骤在try/finally之前。若它们raise，generator context尚未yield且恢复代码未进入。
- 触发：tracker存在时vocab无效、embedding匹配数不是1或pre-hook注册异常。
- 影响：调用失败后global eager_attention_forward仍指向本次intercepted闭包；同进程之后的模型前向可能受到残留条件影响。全局函数替换不是instance-local QueryAttentionHook的恢复实现。
- 限制：标准Qwen模型正常embedding路径不一定触发；正式worker若立即退出不会继续后续模型任务。未执行故障注入或断言旧Run受影响。
- 建议：将替换后的全部setup放在恢复保护范围内，或先完成不会变更global状态的校验再安装；测试异常发生在yield之前与body之内两条路径。不得自动改执行逻辑。

## A026 — P2 / source_confirmed：纯head/support-box条件也强制要求跨序列换图donor

- 证据：`head_screening/pruning/worker.py:execute`所有条件类型都调用_prepare_frozen_interventions；该helper无条件为每sample寻找不同cluster的donor，找不到则raise，不检查plan是否包含swap_reference/swap_query。
- 触发：合法单sample或全同cluster子集，任务只做head removal、row_scope、无需shuffle的support-box或仅black图像条件。
- 影响：无关的换图前提阻止本任务，且模型已加载。samples_per_dataset=1在来源/计划检查中可以通过，不等于正式执行支持这个小范围任务。
- 限制：当前多序列大cohort通常有donor；不说现有全部Run失败。swap模式确实需要跨序列donor，不能为了修复取消其科学约束。
- 建议：根据实际条件构造所需donor/黑图/support输入，仅swap分支强制跨序列；保留冻结seed/身份与来源记录。

## A027 — P2 / scientific_design_risk：pruning的supported标签把random undecided当作未保持

- 证据：`head_screening/pruning/metrics.py:paired_verdicts`的extreme_point_supported用candidate holds且所有random verdict!='holds'；supported scales用all protected_holds且not any(random_holds)。verdict有holds/collapses/undecided三值，跨阈值CI会被判undecided，仍满足上述random条件。
- 影响：这些标签不要求随机对照明确collapses，也没有直接的candidate/protected-minus-random配对差异CI。不能将supported直接解释为显著优于随机或随机定位已崩溃；没有证明不保持，不等于证明差于candidate。
- 限制：可以作为预先声明的操作性决策规则，但应准确命名和限制其含义。未核对历史Run具体CI/标签触发，不修改研究Claim或治理verdict。
- 建议：保留三值结论，单列random undecided；若要比较差异，设计并报告共同cohort的直接配对对照差与CI，不静默修改旧判定阈值。

## 已排除的怀疑

- 已读 `rl/data.py:load_collage_rows` 明确拒绝相同 identity 或相同 query_source_group；symmetric_data 还核验 AB/BA 对同一 source_id 集合的反转。因此不能只根据“同类别配对”就断言 E-014 拼接了同一个源实例。源标注本身的真实性仍依赖原 reviewed 数据，不是凭空证明真实身份。
- `attention_distillation/precompute.py` 已按 rank 分配 dataset_index 并 gather/finalize。不能因为 precompute_teacher 使用多进程就断言会重复写整份 manifest。

## 待核对的风险，不算确认问题

- generic managed envelope 与真实 executor scaffold 的匹配范围；需要核对工具契约，不能只根据目录名猜。
- A014 已确认字段映射/构造未覆盖高级模式；具体 PEFT 版本的各模式 tensor/scale 行为仍未运行验证。
- infer 在已经带 PEFT 的 wrapper 上再 PeftModel.from_pretrained 的语义；需要核对实际 PEFT 版本，暂不下结论。
- 依赖版本/可选 NF4 依赖的声明与实际使用 API 是否匹配。
- SFT 恢复兼容缺口见A017；teacher来源绑定缺口见A019。其余干预/数值/统计与全仓语义覆盖仍待完整审查。

## 验证记录

- 实际完成 Git 基线与 tracked 清单/哈希记录。
- stdlib AST 按 Python 3.9 语法解析 754 个非软链接 Python 文件（包含旧检查/备份）；没有 syntax error。此项不证明语义正确，也不证明所用标准库/API 在 Python 3.9 可运行。
- bash -n 对 88 个导航 Shell 实际返回 0；只解析语法，不执行 source、heredoc 或任何训练/分析命令。
- 21 个快捷 Shell 经过精确三命令模板/共享 helper/引号 argv 核对；42 个 config_alias 经过仅单一 literal assignment 与库内目标/继承图核对。可判定这些入口自身的结构，不替代其 config/worker 算法审查。
- 已实际全文读取230个当前仓库文件；按逐文件实际read布尔证据去重，早期仅对read_complete累加的计数已纠正。覆盖账本不把“读过”算成全部语义通过。
- 129配置的87非config_alias文件均全文读取、42alias-only AST精确核对；88Shell主体全部全文或短模板核对。27相对转发与导航一致，1历史绝对外部checkout单独标明未验证部署身份，第一次28全模板断言实际拒绝，没有掩盖该例外。
- 29个 literal -m/analysis entrypoint 文件/函数/显式re-export源码存在性已核对；初次将R008 re-export视为没有direct def的检查失败已纠正，不记成缺失实现或运行证据。
- GRPO20文件的源码契约见grpo_contract_review.md，Config/Shell总体路由见config_shell_review.md。公共生命周期、SFT/蒸馏、公共候选评测及head核心部分见相应contract_review报告；测试只读定义，未执行。仍未完成所有head/干预/统计/数据消费者/测试/文档/Run语义审查。
- 全量 129 配置的 AST call/import 清单：没有 import，调用仅 dict、两次 sum(screening_counts.values()) 和一次 list(range(8))。三个非纯 dict 配置已全文核对；当前配置未见顶层模型/产物/GPU/目录 IO。该结论不把 Config.runpy 变成任意输入的安全沙箱。
- 搜索少量 Python 3.10/3.11 专属 API 形态未发现命中；dual_role_metrics 的 int | None 有 future annotations，不能据语法表面判断 Python 3.9 不兼容。这仍不是完整运行兼容性验证。
- source-only 导航实际读取 129 个配置、88 个 Shell 的源码引用；没有执行配置/Shell 或启动 worker。
- 先前一次启发式 model 名匹配把 Qwen3VLSFTCollator 混入候选。已丢弃该输出，改为只匹配三个已读的模型 Registry 类；不能用未核对的 regex 候选作为问题。
- 不存在新增测试、模型/GPU、训练、评测或远端运行结果。源码仍保持基线不变。
