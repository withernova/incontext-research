# Head screening 与核心 Trainer 重构交付（2026-10-09）

## 完成内容

根据用户追加授权，重构整个代码仓库中职责过重的 head screening 模块，并改善核心 SFT/GRPO trainer 的紧凑写法和注释。通过 Windows `ssh.exe` 连接 `SZY-3090:30827`，已应用到 `/defaultShare/archive/songzhengyue/projects/IPLoc/mechanism/iploc-szy`，共 34 个文件；保留此前的配置整理、安全修复和 GRPO 职责拆分。

- `keepset_pruning.py`：1295 行降至 115 行；`target_vs_background_ablation.py`：1429 行降至 99 行。旧文件保留说明、兼容导入和原入口，原 Shell/config/analysis.entrypoint 可继续使用。
- 新增 `pruning/`：配置契约、条件、输入扰动、Hook、指标、执行与离线重算各自维护。新增 `target_background/`：输入契约、mask、Hook、生成、指标、报告和执行编排各自维护。
- 提取公共 `artifacts.py`、`checkpoints.py`、`localization.py`、`source_contracts.py`；保留原有 JSON 写入行为、adapter 完整性校验和协议参数，没有合并不同协议的数学口径。
- 展开 `engine/runner.py`、`rl/trainer.py`、`policy.py`、`preflight.py`、`sampling.py` 中的紧凑条件和分号写法，使用更明确的局部变量名，补充中文注释解释恢复、采样 seed、old/anchor/current log-prob、counterfactual、DDP 累积、有限性检查、更新顺序与保存边界。
- 新增远端仓库 `docs/HEAD_SCREENING_MODULES.md`：职责表、类似实验新增方式和 trainer 阅读顺序；更新 `MODULE_MAP.md`。

## 检查结果

- 107 个迁移的函数、类和常量通过 AST 对比；原文件剩余实现和核心 trainer 计算/执行顺序通过 AST 对比。对比仅忽略文档字符串、迁移所需的相对导入层级和明确记录的局部变量改名。
- 增加旧 CLI、analysis entrypoint、公共工具导入边界检查；修复重构过程中按文件路径加载模块时出现的相对导入兼容问题。
- 在独立源码快照运行全部 CPU 测试：**526 passed, 1 deselected, 4 warnings**。未执行的测试需要真实 Qwen processor 资产；测试使用临时数据和随机微型模型。
- 应用前核验全部原文件 SHA-256，应用后核验已测源码 SHA-256；真实仓库 `git diff --check`、兼容入口导入及新增测试文件一致性检查通过。

## 剩余风险与边界

未执行真实模型、NF4 或多卡 GPU 训练；现有 Torchvision 扩展不匹配提示仍在。AST 与 CPU 检查能够支持行为保持，但不能替代真实训练验证。

完整接入通用 Runner/Hooks、跨训练入口统一 checkpoint 契约和精确恢复仍是后续独立工作。这轮提取已有 head screening checkpoint 加载实现，未改变保存格式或扩展 resume 能力。

未读取历史 Run 结果、旧日志或模型权重，未启动实验、提交或推送代码，未修改 Survey Tool 审批、Claim、Run 授权或治理状态。Solid Run ID：无；报告仅提供工程验证，不形成实验效果结论。

补丁与逐文件哈希见同目录 `head_screening_refactor_20261009.patch`、`head_screening_refactor_20261009_hashes.json`。
