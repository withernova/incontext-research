# 现有入口文件的职责分层

## 结论

本轮已实际整理入口层，不只是增加规则或导航。三份配置和八个 canonical Shell 已归到对应职责目录。旧路径保留薄转发。核心包原有职责目录保留；历史产物未移动。

- 仓库：`code-repositories/03/iploc-szy`。
- 初始 Git 干净，基线：`3c7ed5cdcde16c096b65021935002074f8080e51`。
- 本地提交：`982553de383bf58ed771428f8b34aaf65a7e381c`。
- 工程审阅：`4f135af8d694a648`，passed/current，无 blocking 或 warnings。精确提交 47 个任务文件。
- 未 push、同步服务器、部署、创建或运行 Run。

## 实际归位

| 原位置 | 当前维护位置 |
|---|---|
| `configs/sft/qwen3vl_8b_focus_branch.py` | `configs/tasks/qwen3vl_8b_focus_branch.py` |
| `configs/sft/qwen3vl_8b_focus_tasks.py` | `configs/tasks/qwen3vl_8b_focus_tasks.py` |
| `configs/sft/qwen3vl_8b_grounding_tasks.py` | `configs/tasks/qwen3vl_8b_grounding_tasks.py` |
| `tools/run/run_branch.sh`、`run_focus_tasks.sh` | `tools/run/tasks/` |
| `tools/run/run_reference_query_alignment.sh`、`run_dynamic_reference_query_alignment.sh` | `tools/run/train/` |
| `tools/run/run_head_stability_suite.sh` | `tools/run/analysis/` |
| `tools/run/analysis/e014/` 中 step800、multi_v2 step200、min/cap5 step150 的三个冻结评测 Shell | `tools/run/eval/e014/` |

原配置只保留 `config_alias`，不维护两份参数。原 Shell 只转发对应文件并传递 `"$@"`。已有编号兼容配置/历史命令继续通过这些路径引用；不回写历史 Run 的 command 或 snapshot。Grounding adapter Shell 的当前默认改指 tasks canonical 配置。

新 `configs/README.md` 说明共享默认、单用途配方、多动作选择、实验差异和旧兼容入口。生成的 `tools/run/README.md` 将当前职责目录和历史兼容表分开。README、AGENTS、MODULE_MAP、配置指南、入口索引和相关用法同步当前路径。

没有新增 worker、算法或 runner。保留已有包目录的 models/datasets/engine/rl/evaluation/head_screening 职责划分，不为形式整齐大规模搬动源码。

## 必要的路径与导航调整

1. 配方默认 `branch.parent_config` 改用 `../sft/`，实际仍指同一父配方。
2. moved Shell 的 `_common.sh` 相对路径改为 `../_common.sh`；仍使用原公共机制。
3. `branching.py` 仅补旧 alias 显式 CLI sibling 父配方兼容：canonical/CWD 解析已失败、调用路径不同、且用户确实覆写 parent_config 时，才回退原调用目录。默认解析及原有成功解析的优先级不变。测试定义覆盖新旧配置与缺失父路径，未执行。
4. A016 两个 head-circuit Shell 的 ROOT 改为 `../../../..`。按物理目录计算已指仓库根；未执行该分析，不声称历史结果已修复或重算。
5. 源码导航区分冻结 eval 与 analysis，canonical 配置反查兼容引用；明确 direct worker 优先于不匹配的 generic action，同时保留通用 launcher 和匹配 analyze worker 的实现路径。

## 静态证据与限制

检查脚本/结果位于项目 `.pi/code-review/directory-layering-20261013/`，不入源码提交。

- 三份新配置相对父路径规范化后，与旧配置完整 AST 相同。仅另清理三行继承来的尾部空白。
- 八份 canonical Shell 去除导航/说明并规范化 helper/config 路径后，执行主体与旧文件相同。旧转发目标、参数传递和执行位逐项核对。
- 除上述父路径兼容外，109 个 package 文件与初始提交逐字相同。
- 137 份 Python 按 3.9 AST 解析通过；96 份 Shell 的 `bash -n` 通过。
- 四份导航/目录文档的 1640 个本地 Markdown 链接位于仓库内且存在。
- `--check-navigation`、基线完整 diff-check、staged diff-check 通过。source-only trace 实际查看 task 配置、旧冻结转发链和稳定性 suite。
- 首次提交阶段暴露 copied recipe 原有尾部空白，审阅拒绝并未提交。已修正、重查、重新审阅后提交；没有绕过门禁。

这些证据只证明限定的源码/路径与语法性质。不等于实际 Config 运行、第三方依赖兼容、模型或分布式执行验证。新增/更新测试定义未运行；没有构建、项目 import/smoke、模型、GPU、服务器或实验执行。

## 仍未完成

全仓审查仍基于 `1622e5f64a70239d02145f017cfd991cf8318e47`，目标未完成。27 项基线问题保留，只有 A016 在本轮作源码路径修正；不是所有审查问题已修复或实际复现。覆盖账本不因迁移/导航数量增加而自动记作 reviewed/passed。新 HEAD 不是全仓通过版本。

旧 CP150 评测完成状态本轮未查询，保持未知。训练不恢复；不继承旧执行授权或部署 latest。历史数据、checkpoint、日志、结果、Run ID 和源版本事实未改。
