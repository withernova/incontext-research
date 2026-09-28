# Top-10 整头置零实现检查

检查日期：2026-09-12。此记录仅描述代码检查，不是实验结果或 Run 授权。

新增文件：
- `../run_proposal_top10_head_ablation.md`：拟建 Run 的范围、条件、指标、输入与剩余缺口。
- `iploc_szy/head_screening/top10_head_ablation.py`：独立 runner、整头 hook、冻结输入和配对统计。
- `configs/head_screening/e012_top10_head_ablation.py`：待补齐真实来源的配置模板。
- `tools/run/e012_top10_head_ablation.sh`：python3 启动入口。
- `tests/test_top10_head_ablation.py`：聚焦契约与数值测试。

## 本地已执行

`python3 -m pytest -q shell/06_experiments/E-012/implementation/tests/test_top10_head_ablation.py`

结果：**21 passed，2 skipped**。

通过范围：同层匹配随机对照的可复现性及候选排除；非法/重复 heads；无效预测保留在 IoU 分母；坐标变化有效配对计数；越界、退化、多框和格式错误拒绝；冻结排名/Top-10/哈希一致性；静态 CLI 成功路径；已有输出目录拒绝覆盖；空配置在模型 import 前明确失败。

两个跳过项目均由于本地无 PyTorch：
1. 回答起点切分、所有 GT 回答 token 排除与图像完整性检查。
2. 使用真实 torch 张量的 GQA prefill/decode 置零、未选中 head 精确不变、异常恢复全局 attention 函数检查（此测试替代了 Transformers 模块入口，不等同于真实 Qwen 模型集成）。

Python 编译、AST 解析、启动脚本 `bash -n` 和新增文件尾随空白检查通过。

实际运行启动脚本的 `--validate-only`：预期 exit=1，列出未解决的 runtime config、manifest/ranking/samples 哈希及路径、output_dir、heads；未加载模型或创建实验输出目录。这是缺失输入保护检查，不能表述为真实 Run 输入预检通过。

当前治理目录没有可用的 Git 仓库，因此未执行成功的 `git diff --check`；使用上述直接文件检查。

## 尚待执行

- 将 R-001 作为显式参考后，核实 Top-10、模型/LoRA、排序来源与评估样本、annotation 坐标转换，填入冻结配置。
- 在完整 IPLoc + PyTorch + Transformers 环境运行全部聚焦测试，并用真实 Qwen 模型验证 attention dispatch、collator 边界、KV cache 多步生成与空 hook parity。
- 用独立先导输出目录进行 3 条/15 条件的实际模型检查，确认审计和生成输出完整后再评估完整 60 条预算。

未启动 GPU 实验，未创建正式 Run ID，未修改 canonical experiment、Claim、审批、授权或其它治理状态。可引用 Solid Run：无。
