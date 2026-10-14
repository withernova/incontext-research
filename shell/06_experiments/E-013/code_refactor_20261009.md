# 代码轻量重构交付（2026-10-09）

## 完成内容

用户授权在当前代码仓库做简单重构，重点是后续类似实验的复用和小实验可管理性。实际修改通过 Windows SSH 应用到 `SZY-3090:30827` 的 `/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy`，保留前一轮安全修复。

### 实验配置归档

E-013 的 12 份 Python 配置归入 `configs/experiments/E-013/training/`、`evaluation/`。原 `configs/sft/e013_*.py`、`configs/grpo/e013_*.py` 变为薄 `config_alias`，旧配置路径和启动命令仍可用。参数只维护 canonical 文件。

新增 `configs/experiments/README.md` 和 E-013 README，说明通用 recipe、实验训练/评测/分析配方以及一次性工具的分工。JSON 单设备低层示例保留原位置。

### 只读实验导航

新增 `tools/experiments.py`，直接复用已有源码审计与配置合并逻辑：

```bash
python tools/experiments.py list
python tools/experiments.py list --experiment E-013
python tools/experiments.py show CONFIG.py
python tools/experiments.py show CONFIG.py --cfg-options runtime.grpo.learning_rate=0.00008
python tools/experiments.py diff FIRST.py SECOND.py
```

`list` 去除兼容配置的重复项，并显示已登记的专项 Shell。实验归属来自源码目录或显式文件名前缀；没有从运行结果、checkpoint 或说明文字推断归属。专项入口没有明确进程数时显示 `—`。

`show` 展示最终配置、来源文件和统一启动计划；专项配置明确保留原入口，没有伪造通用 worker。`diff` 展示最终合并参数的增加、删除与改变，能区分缺失字段和显式 `None`。

这些命令不分配运行目录、不检查实际数据/checkpoint、不启动任务。通用执行仍使用 `bash tools/run.sh CONFIG.py --inspect`，专项小实验保留现有接口。

### GRPO 职责拆分

从 `iploc_szy/rl/trainer.py` 抽出：

| 模块 | 职责 |
|---|---|
| `preflight.py` | 配置、配对数据和图像路径校验 |
| `policy.py` | policy/anchor、量化、LoRA 与 DDP 加载 |
| `sampling.py` | rollout、EOS、位置缓存和 completion log-prob 重放 |
| `trainer.py` | 配对更新编排、梯度累积和保存 |

原有从 `trainer` 导入 `inspect_config`、`load_policy`、`rollout`、`completion_logp`、`reset_positions` 的接口保留。新代码可直接从职责模块导入。函数主体和训练更新循环的 AST 核验一致，采样分布、mask、EOS、policy/anchor 顺序和梯度缩放保持原有实现。

更新 `CONFIG_MANAGEMENT.md`、`MODULE_MAP.md`，新增 `docs/GRPO_MODULES.md`，并通过已有 `audit_entrypoints.py` 刷新配置索引与入口手册。共变更 38 个文件，其中主要是 12 份配置迁移及其旧路径别名。

## 检查结果

- 在独立源码快照中比较全部 12 份 E-013 重构前后有效配置：一致，仅排除必然变化的 parent-config 来源路径。
- 旧/新配置等价、配置来源保留、从其他工作目录调用、CLI 覆盖、源码导航无模型/输入检查副作用均通过。
- 聚焦配置/GRPO/兼容检查：**124 passed**；随后补充专项小实验导航测试。
- 最终全部 CPU 测试：**522 passed, 1 deselected**，包括随机微型 Qwen3-VL 双图重放、梯度与冻结 anchor 检查。未执行的 1 项需要真实 processor 资产。
- 应用前逐文件核验当前远端旧 SHA-256，应用后核验与已测源码一致。当前真实仓库的 `list`、`show`、旧/新配置 `diff` smoke 通过；`git diff --check` 通过。

## 边界与后续风险

这轮落实配置管理和职责拆分，没有改变实验数据范围、reward、学习率、seed、采样分布或保存布局。没有读取历史 Run 产物、训练日志或模型权重，没有执行训练，没有改动 Survey Tool、Claim、Run 授权或治理状态，也没有提交或推送代码。

GRPO 完整接入通用 Runner/Hooks、统一 checkpoint 格式、严格 adapter 完整加载和精确 resume 仍需独立验证；之前审查中的相关风险继续存在。未做真实 8B/NF4 或多卡 GPU 检查。测试保留已记录的 Torchvision 扩展及随机模型/attention 提示，没有为此改装环境。

当前 canonical E-013 仍为 `planned/draft`；假设、成功标准等设计字段未补造。Solid Run ID：无。本交付只报告代码工程验证。

重构补丁与文件哈希清单见同目录 `code_refactor_20261009.patch`、`code_refactor_20261009_hashes.json`。
