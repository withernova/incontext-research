# 全仓库本地审查与整理建议（2026-10-09）

## 当前结论

仓库已有清楚的 Config → Registry/Builder → Dataset/Collator → Model → Runner/Hooks → Evaluator 主链路，适合继续沿用当前轻量框架。问题主要集中在实验执行编排、checkpoint 接口和运行依赖边界，不需要为了外形统一而整体换框架。

这次完成的是整个仓库的本地静态扫描和关键链路人工审阅；不是逐行证明全部代码正确，也不是训练或实验效果验证。没有修改代码源文件。

## 来源与范围

- 当前目标仍为 canonical E-013，Workspace 03，`planned/draft`；只读接口重新核验过目标。
- 当前 Workspace 未配置本地 Git 开发。正式准备命令退出码为 1，返回 `Workspace is not bound for local Git development`。
- 最新源码经 Windows `ssh.exe` 从绑定的 `SZY-3090:30827` 仓库 `/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy` 取到 `/tmp/iploc-full-local-review-20261009`，用于本地只读审查。这是临时源码快照，不是工具管理的正式本地 Git clone，没有将它登记为绑定或部署版本。
- 范围包括 94 个库模块、29 个 Python 工具入口、47 个测试文件、121 份 Python 配置、1 份 JSON 配方及源码文档、Shell。核心关注配置/启动、数据与 token 对齐、SFT/GRPO、保存与恢复、评测、attention distillation 和 head screening。
- 未打开配置所指向的数据、权重、Run 结果、旧日志或凭据；未读取其他实验的结果证据。Solid Run ID：无。

## 优先处理的具体问题

### P1：通用 adapter 加载没有拒绝缺失的 LoRA 权重

位置：`iploc_szy/checkpointing.py:32`，尤其是 `set_peft_model_state_dict` 返回后的检查。

当前只检查 `incompatible.unexpected_keys`，没有检查适配器对应的 `missing_keys`，也没有核对 checkpoint 的完整键集合。因此部分 LoRA 张量缺失时，代码没有自己的完整性拒绝条件，存在残留初始参数与已加载参数混用的风险。这里不能直接把全部 base-model missing keys 判为错误，应只核验实际 adapter 的应有张量。

仓库 `head_screening/checkpoints.py:54` 已有读取 checkpoint 与已加载 adapter 张量并逐项校验的实现，可提取共同的严格校验逻辑，分别适配 wrapper 和 adapter 名称。优先补“删除一项 LoRA 张量必须失败”和“完整保存/加载一致”的集成检查。

证据等级：静态代码路径确认；本机未执行 PEFT 加载测试。

### P1：GRPO 保存结构与通用 checkpoint 消费接口不一致

位置：`iploc_szy/rl/trainer.py:438`、`:473`；`iploc_szy/checkpointing.py:11`；`iploc_szy/head_screening/checkpoints.py:10`；`tests/test_e013_grpo_tiny.py:24`。

GRPO 以具名 `policy` adapter 调用 `save_pretrained(.../adapter, selected_adapters=['policy'])`。仓库的真实 PEFT 微型模型测试明确从 `initial/policy` 加载这类保存；而通用 validator 期望 `adapter/adapter_model.safetensors`，head screening resolver 期望 adapter 根下直接有 `adapter_config.json` 和权重。训练输出交给通用消费者时缺少同一格式的解析契约。

GRPO 使用 `optimizer.pt`，SFT resume 要求 `trainer_state.pt`。这本身可以是不同算法的合理选择，但消费者不能将两者当成同一种 checkpoint；当前也没有 GRPO resume 入口。建议明确 adapter 名称、实际 payload 路径、processor 路径和训练状态类型，先覆盖 GRPO 保存 → 实际评测加载的贯通测试，不静默寻找 latest。

证据等级：源码及仓库现有测试代码交叉确认；本轮没有执行真实 PEFT 保存/加载。

### P2：纯配置导航依赖整套训练包导入

位置：`iploc_szy/__init__.py:16`；`tools/experiments.py:12`。

顶层包为 Registry 注册而立即导入所有组件。因此读取 config 或执行只读实验导航也会触发 attention-distillation 等模块导入 Torch。本机执行 `python3 tools/experiments.py list --experiment E-013` 确实在该链路报 `ModuleNotFoundError: No module named 'torch'`。

这不表示导航会加载真实模型，但使它无法在轻量审查环境中使用。建议将组件注册集中到显式的 registration 函数，在真正 build 时调用；配置解析、Registry 定义、目录导航保持轻量。必须检查实际构建入口及旧 import 接口，不能仅删除现有注册 import。

### P2：head screening 的 worker 仍然承担大量步骤

位置：`head_screening/pruning/worker.py:37` 的 `execute` 为 532 行；`target_background/worker.py:52` 的执行函数为 558 行；`top10_head_ablation.py:247` 的 `execute` 为 286 行。

上一轮拆出了输入、Hook 和指标，改善了模块边界，但两个 worker 仍同时承担模型准备、样本编码、基线、条件执行、记录写入和汇总。旧入口变薄不代表执行流程已经短小。

建议再按阶段抽取 `_prepare_model`、`_prepare_sample`、`_run_baseline`、`_run_conditions`、`_write_records`、`_finalize_report` 一类的子函数；传入明确依赖，保留协议参数和逐样本顺序。先拆执行编排，再考虑跨协议复用。不同 row scope、mask 或指标口径不能为了减少重复而强行合并。

### P2：恢复能力仍不是精确断点续训

位置：`engine/runner.py:370`、`:406`；`rl/trainer.py:477`。

SFT checkpoint 保存 optimizer、scheduler、pipeline、seed 和进度，没有保存逐 rank 的 Python/Torch/CUDA RNG 状态；恢复从设置 seed 开始。因此包含 dropout 等随机操作时，不应声称与不中断训练逐步一致。GRPO 最终状态只保存一个 rank 的 CPU Torch RNG，且无恢复入口。

这是源码中已注明的能力边界，不是这次重构引入的新回归。后续独立设计 RNG/进度契约与不中断对照，保持“初始化新分支”和“恢复同一训练”分开。

### P2：依赖版本与训练选项缺少可复现安装契约

位置：`pyproject.toml:9`；`rl/policy.py:21`。

依赖没有声明本仓库所需的已验证版本范围；NF4 加载路径需要 bitsandbytes，源码也直接使用 NumPy，而当前依赖清单没有对应明确声明。新安装环境是否支持 Qwen3-VL、相应 processor 与量化路径，不能由无界版本清单保证。

建议记录一套实际验证环境及训练/测试/量化的可选依赖组，不在没有验证时猜版本或升级环境。本轮未安装依赖。

## 与当前模块格式的关系

Config 继承、Registry 注册、Builder 注入 processor、Runner/Hooks、Evaluator 这些边界已经存在。当前最有价值的是稳定这些接口，而不是按检测框架的目录名称搬文件。

GRPO 的 `train()` 已为 93 行，阶段子函数也已落地；继续把它拆得更碎收益有限。建议优先补真实 checkpoint 贯通验证，再处理两个 500 行 worker。SFT `run()` 为 161 行，可在后续将一次 optimizer update 和最终汇总独立出来，但它已经具有 batch、loss、同步和保存辅助方法。

小实验配置已有 canonical 目录及兼容 alias，应继续复用。新增实验放在自己的 `configs/experiments/E-xxx/`，专项流程保持薄入口，不复制一套模型加载器。

## 本轮检查结果

| 检查 | 结果 |
|---|---|
| 291 个 Python 文件 AST 解析 | 无语法错误 |
| 121 份 Python 配置递归继承/alias 加载 | 全部成功 |
| 1 份 JSON 配方解析 | 成功 |
| 78 个 Shell 的 `bash -n` | 全部成功 |
| 库内显式相对模块 import 的源码定位 | 未发现目标模块缺失 |
| 只读实验导航 | 退出码 1；本机缺少 Torch，顶层注册 import 触发依赖 |
| 本地完整 pytest、微型模型、真实 GPU | 本轮未执行；本机缺少 Torch/Transformers/PEFT |

静态检查明细及 Python 源码 SHA-256 存于同目录 `local_repository_review_20261009_checks.json`。此前远端测试通过记录不作为本轮本地测试通过的证据。

## 修改顺序与当前阻塞

### 用户追加优先级：可读性优先

用户明确要求优先解决阅读困难。下一轮代码整理以可读性为主，不先引入新框架或改变训练行为。checkpoint 风险保留在审查清单，行为修复单独评估。

具体阅读障碍不仅是行数：GRPO `_backward_and_log` 有 14 个位置参数，`_train_pair` 有 11 个；rollout 记录通过长元组及数字索引访问。此前抽函数虽缩短了主入口，但增加了参数追踪成本。应使用有语义的记录字段、明确的输入组织和阶段命名，同时避免引入新的通用抽象层。

可读性整理顺序为：先梳理 GRPO 的采样记录、reward/反事实判定和 backward/log 边界；再拆 SFT 一次更新与最终汇总；最后将两个长 worker 按样本准备、基线、条件执行、写入和汇总分段。展开单行控制流和分号，注释说明因果顺序、梯度和协议边界，不机械解释每行。保留现有入口、配置、日志字段、随机调用顺序及 loss 缩放。

完成标准是主流程能顺序读懂、子函数职责单一、依赖和记录字段易追踪；文件数增加或函数行数减少本身不算完成。正式源码仍需绑定准备成功后才能修改。

1. 正式绑定项目内仓库，按工具 `code prepare` 检查并准备版本。
2. 收紧 adapter 完整性校验，明确 SFT/GRPO 保存与消费契约，补实际 PEFT 集成测试。
3. 拆两个 head screening worker，保留旧 CLI/config 接口并验证条件执行顺序。
4. 解耦纯配置工具与训练组件注册；清理紧凑写法和剩余调试输出。
5. 将精确恢复、多卡异常传播、依赖版本固定作为独立验证任务。

正式源码修改仍被 Workspace 绑定阻塞。依据 research-survey C3 的“只在绑定本机仓库内做允许的代码修改”，没有将临时快照当正式 clone，也没有回退到 SSH patch；没有修改绑定、审批、Claim、Run 授权或其他治理状态，没有 push、部署、训练或代码提交。
