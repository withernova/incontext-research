# E-013 所用代码仓库整体审查（2026-10-09）

## 结论与范围

建议渐进重构，最高优先级是统一 checkpoint 保存/加载契约和训练生命周期。现有 Config → Registry/Builder → Dataset/Collator → Model → Runner/Hooks → Evaluator 结构可以保留；已有统一 launcher、来源快照、配置别名、防泄漏检查和较完整的测试，适合逐步收拢职责。

用户在执行过程中明确要求检查整个代码仓库，因此覆盖公共框架与专项分析源码。通过 Windows SSH 访问 `SZY-3090:30827`，实际仓库为 `/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy`。仅扫描源码、测试和入口文档；没有读取实际 Run、历史结果、训练日志或模型权重，没有运行训练，没有提交或推送代码，也没有修改 Survey Tool、Claim、Run 授权或治理状态。

已重新读取 canonical E-013：`planned/draft`，目标仍为多框输出及按置信度选框；假设、成功标准、对照等字段尚未填写。本次没有据此补造实验设计。可引用的 Solid Run ID：无；下文都是源码审查和隔离工程检查，不构成科学效果证据。

源码快照覆盖约 70 个包内源文件、106 个工具/脚本、109 个配置文件，以及原有 43 个测试文件。对全部 Python 文件做语法/结构扫描，对启动、数据、SFT、GRPO、checkpoint、评测和主要 attention hook 实现做重点检查。这不是对每个专项分析分支逐行完成正确性证明。

## 已复现并修复

| 问题 | 影响与修复 | 当前源码位置 |
|---|---|---|
| checkpoint 多 rank 竞争 | 原先所有 rank 都检查目录存在性；rank 0 创建目录后，后到的 rank 会误报覆盖。现在仅写入者检查并创建目录，其余 rank 进入同步。仍保留写入者拒绝覆盖的保护。 | `iploc_szy/engine/runner.py:339` |
| 非有限值检查晚于参数更新 | 原先 `FiniteHook` 在 `optimizer.step()` 后检查，而且可以不配置 Hook。现在在更新前检查跨 rank 汇总的 loss 和梯度，并让梯度裁剪拒绝非有限范数。测试验证 NaN loss、Inf 梯度和有限梯度的范数溢出均不会修改参数或初始化 Adam 状态。 | `iploc_szy/engine/runner.py:225` |
| 合法 padding ID 被替换 | `pad_token_id or eos` 会把 0 当作未设置。现在只在 ID 为 `None` 时回退到 EOS。 | `iploc_szy/rl/trainer.py:55` |
| 相同 IoU 的任意排序惩罚 | `rank_iou_delta=0` 时原先将相同 IoU 的候选纳入排序项。现在明确排除零差值，默认非零阈值行为保持一致。 | `iploc_szy/rl/multi_candidate.py:67` |
| 坐标测试污染全局模块 | 测试在收集阶段永久替换 `PIL` 和包模块，导致联合测试导入 Transformers 失败。改为 `patch.dict` 作用域，加载替身后恢复模块表。 | `tests/test_coordinate_token_alignment.py:37` |
| 测试与入口文档滞后 | checkpoint 日志测试缺少新增的 `checkpoint_kind` 参数；入口索引/手册未同步新增脚本。更新测试调用，并用已有源码审计脚本重新生成两份入口文档。 | `tests/test_head_stability_suite.py`、`configs/ENTRYPOINT_INDEX.md`、`docs/LAUNCH_CATALOG.md` |

新增 `tests/test_repository_training_safety.py`，原有防覆盖测试明确设置写入者身份。远端共变更 9 个源码、测试和文档文件；应用前核验旧 SHA-256，应用后逐文件核验与已测快照一致。

## 剩余风险，按优先级排序

### P1：GRPO checkpoint 与公共加载器的目录契约不兼容

位置：`iploc_szy/rl/trainer.py:310`、`iploc_szy/checkpointing.py:11`、`iploc_szy/run_management.py:49`。

GRPO 使用命名 adapter `policy`，调用 `save_pretrained(..., selected_adapters=['policy'])`。当前 PEFT 实际生成 `adapter/policy/adapter_model.safetensors`；公共验证和评测入口要求 `adapter/adapter_model.safetensors`。此外，GRPO 保存 `optimizer.pt`，公共恢复要求 `trainer_state.pt`。

已用两维随机 Linear + LoRA 验证保存路径，并确认公共验证器拒绝该输出。当前源码中的 GRPO 输出不能直接满足公共加载契约。没有读取实际 checkpoint，不能断言某次真实输出是否经过外部转换。

建议建立唯一 checkpoint 解析接口，显式记录算法、adapter 名称和可用恢复状态，并兼容已有保存布局。验收必须包含 SFT/GRPO 保存→公共评测加载的 round-trip；训练恢复与仅加载权重应分别校验。

### P1：公共 adapter 加载器会接受缺失 LoRA 张量

位置：`iploc_szy/checkpointing.py:33–55`；可参考仓库内较严格的 `iploc_szy/head_screening/bbox_gradient.py:82`。

公共加载器只拒绝 `unexpected_keys`，没有核验完整 LoRA 张量集合。随机小模型测试中，删除一项 `lora_A` 权重后仍能返回成功。这可能让部分 adapter 参数保持初始化值，造成无声的错误评测。

建议核验本次目标 adapter 的张量键、形状和加载结果；不能直接拒绝所有 `missing_keys`，因为冻结基座参数本来就不在 adapter 文件中。将严格加载逻辑收敛到共享接口，避免分析入口和公共入口采用不同标准。

### P1：checkpoint 发布缺少完整性提交步骤

位置：`iploc_szy/engine/runner.py:339`、`iploc_szy/rl/trainer.py:307–311`、`iploc_szy/checkpointing.py:11–30`。

当前直接向最终 checkpoint 目录写 adapter 和训练状态；验证器主要检查文件存在。写入中断会留下半成品目录，已存在的文件也不代表写入完成。写入者异常时其他 rank 还可能停在同步点；本次只修复了目录竞争，没有完成异常广播机制。

建议写入临时目录，保存必要的完整性清单，完成核验后原子发布；多 rank 在同步前交换成功/失败状态。需要覆盖中断写入、损坏文件、重复保存和写入失败传播的测试。

### P2：resume 不能保证恢复相同训练轨迹

位置：`iploc_szy/engine/runner.py:339–426,660`、`iploc_szy/rl/trainer.py:159–324`。

SFT 保存 optimizer/scheduler/进度，但不保存各 rank 的 Python、NumPy、CPU/CUDA RNG 状态；恢复时重新设置初始 seed。启用 dropout 或随机变换后，恢复轨迹会与连续训练不同。当前常用零 dropout 配置不等于通用保证。

GRPO 的中间 optimizer 文件也不包含完整 RNG/采样进度，训练入口没有完整 resume 逻辑。建议统一恢复状态格式并明确“加载权重继续新训练”和“精确恢复”的区别。以随机微型模型验证连续训练与中断恢复的参数/采样一致性。

### P2：GRPO 预检查不够完整

位置：`iploc_szy/rl/trainer.py:76–119`、`iploc_szy/rl/objective.py:16`。

部分标量只做大小比较，没有统一检查有限性、类型和整数约束；例如 `beta=NaN`、`learning_rate=Inf` 无法被现有比较可靠拒绝，保存间隔和奖励参数也没有完整的启动前验证。奖励参数错误可能在加载大模型后才暴露。

建议把模型加载前的参数校验集中为轻量 schema，并共享训练入口与 `--inspect` 的校验逻辑；不要把路径/数据校验与 GPU 初始化混在同一函数中。

### P2：解析与评测协议边界不统一

位置：`iploc_szy/prompting/coordinates.py:35`、`iploc_szy/evaluation/bbox.py`、`tools/evaluate.py:78–82,145`。

通用 `parse_box` 会接受自由文本中的前四个数字，列表中的非数值会抛异常，非有限坐标没有统一拒绝。用合成输入验证了 `[None,0,1,1]` 抛 `TypeError`、NaN 坐标被接受，以及无 bbox 的四数字文本被当作框。置信度协议有更严格的独立解析器，不能据此认为所有旧协议同样严格。

评测解码会删除全部 special tokens，而 GRPO 保留非 EOS special tokens 供严格解析；某些非法生成因此可能在训练和评测时被不同地计为有效。评测还默认使用 `train_dataloader` 和头部样本；对于训练诊断可以接受，但独立评测应显式声明数据划分和选择方式。

建议分离兼容解析和严格解析，不静默改变既有指标定义；为评测增加终止状态与原始输出审计信息，并显式记录 split/selection。

### P2：依赖声明和当前环境存在可复现性风险

`pyproject.toml` 没有版本约束，部分直接使用的 NumPy、Matplotlib、SciPy 以及量化相关依赖没有按用途明确声明。attention 提取和干预代码依赖 Transformers 的内部结构；测试通过不能保证任意升级版本仍兼容。

当前检查环境为 Torch `2.8.0+cu128`、Torchvision `0.19.1+cu121`、Transformers `4.57.3`、PEFT `0.17.1`、NumPy `1.26.4`、bitsandbytes `0.48.2`。测试实际出现 Torchvision 图像扩展无法加载的警告。PIL 路径通过不代表该扩展可用；本次没有改装环境。

建议记录经过验证的依赖集合，并把 CPU 测试、attention 内部接口兼容检查和真实 GPU/NF4 smoke 分开运行。应先解决当前二进制扩展不匹配，再把该环境作为重现基线。

## 重构顺序

1. **checkpoint 层**：集中 adapter 定位/完整加载、完整性提交、SFT/GRPO 格式兼容和恢复状态；先解决上面的 P1。
2. **训练生命周期**：从 SFT/GRPO 大函数中抽出预检查、单次更新、保存和分布式清理；GRPO 的 rollout、anchor 重放、counterfactual、loss 汇总分别有明确接口。保持现有 reward、采样分布、seed 和数据选择行为，避免重构时混入算法修改。
3. **专项分析复用**：先抽取重复的模型/processor 加载、视觉 span/grid 审计、hook 安装恢复和原子结果写入；保留各专项指标定义。`target_vs_background_ablation.py` 约 1,429 行、`keepset_pruning.py` 约 1,295 行，存在约 300 行的执行函数，是维护负担较重的区域。
4. **配置与环境**：公共基础配置仅保存可移植默认值，将机器路径与实验参数显式分开；保留已有配置别名。恢复/训练契约稳定后再做入口精简和包注册懒加载。

SFT 当前按确定性索引循环取样，没有 epoch shuffle；这是已有行为。本次没有新增 shuffle，也没有改变 reward、学习率、训练数据、主指标或实验结论边界。

## 验证与限制

- 原始源码的隔离回归检查复现 4 个失败：目录竞争、Inf 梯度更新未阻止、padding 0 被替换、零阈值 IoU tie 惩罚；另在联合收集阶段复现模块污染。
- 修复后，重点组合测试 **138 passed**，包括随机微型 Qwen3-VL 双图生成/重放、policy 梯度与冻结 anchor 检查。
- 扩大到全部测试后，发现过期测试调用和过期入口文档；修正后在显式指定快照导入路径的隔离环境中 **498 passed, 1 deselected**。未执行的 1 项需要真实 Qwen processor 资产。
- 初次全库检查的两个 CLI 子进程导入失败来自快照未安装到 Python 环境；显式给子进程提供快照源码路径后通过，没有为此修改生产 CLI 代码。
- 全库检查仅使用合成数据和随机微型模型；没有运行真实 8B、NF4 或多卡 GPU smoke。目录竞争由确定性时序模拟验证，不能替代真实分布式故障检查。
- 全库测试仍有 4 条警告，含 Torchvision 扩展加载失败、随机模型保存时的 PEFT 配置提示和 attention 审计中带梯度张量转标量的提示。
- 应用到实际远端仓库前后逐文件 SHA-256 核验通过；`git diff --check` 通过。原工作树干净，当前只包含本次 9 个文件的变更；未提交、未 push。

复核补丁与文件哈希清单见同目录 `code_review_20261009.patch`、`code_review_20261009_hashes.json`。
