# E-012 · 链式法则内核数值检查

日期：2026-09-14。

结论：本次合成输入检查支持同一 post-softmax attention 节点上的
`A * dL/dA = <dL/do, A*V>`，以及 contribution 乘以 `1-epsilon` 时局部导数为负的 signed contribution。
**这不是完整 R004 的真实模型检查，也不是 head 筛选或因果必要性证据。**

## 实际完成的检查

- 从服务器已安装的 Qwen3-VL 源码中直接加载 `repeat_kv` 和 `eager_attention_forward`；使用原函数 AST，不改写函数逻辑。完整源码 SHA-256 保存在 JSON。
- CPU 上运行 8 组固定合成 Q/K/V，seed 为 20260914–20260921；分别使用 FP64 和 FP32。
- 每组为 4 个 query heads、2 个 KV heads、16 个 token、head dimension 8。指定 Reference keys `[2,8)`，prediction rows `[12,16)`。
- 下游为固定随机投影与 tanh 后的 token 平均 CE；使用合成标签，未使用真实 bbox、图像或 LoRA checkpoint。
- 同一计算图分别取得 attention 和 head output 的 autograd 梯度，再独立计算等式两侧。
- 固定 head 0/3，检查单条 Reference edge 和全部指定 Reference edges；epsilon 为 0.001/0.01。直接缩放 AV，不重新 softmax。比较中央差分与 `-sum(e)`，同时保存单侧差分。

## 结果

| 检查 | FP64 | FP32 |
|---|---:|---:|
| 合成输入数 | 8 | 8 |
| 被检查 Reference edges | 768 | 768 |
| 两路贡献最大绝对误差 | 1.4745e-17 | 7.4506e-9 |
| 两路贡献最大相对 L2 误差 | 2.2222e-16 | 1.1246e-7 |
| 无干预 AV 重放 loss 最大误差 | 0 | 0 |
| 有限差分比较数 | 64 | 64 |
| 符号可分辨数 | 64 | 62 |
| 可分辨项符号一致数 | 64 | 62 |
| 有限差分最大绝对误差 | 1.1020e-6 | 2.6210e-4 |

全部代数比较通过预设容差。有限差分通过脚本声明的截断/舍入容差；FP32 的另外 2 项标记为符号不可分辨，没有计入符号一致数。

## 边界与未完成项

- 未测试真实图像、真实 bbox-loss 行提取、真实 LoRA checkpoint、BF16/GPU、GT occupancy 或完整模型 hooks。
- 指定 Python 环境导入完整 Qwen3-VL 模块时，遇到 `operator torchvision::nms does not exist`。本次只加载独立 attention 内核，不将其解释为完整模型环境正常。
- 远端写入检查脚本时遇到 `No space left on device`，随后通过标准输入在内存中运行，JSON 仅保存在本地。未清理其它文件。
- R004 尚未指定 checkpoint 和样本 manifest；已向用户询问。没有改写 Run 状态、授权、Claim 或 Experiment 指标。

原始记录：[R004_chain_rule_kernel_20260914.json](R004_chain_rule_kernel_20260914.json)。

检查代码：[check_reference_chain_rule.py](../implementation/tests/check_reference_chain_rule.py)。
