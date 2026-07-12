# E-001 · 实验结果

## 当前状态
已完成 **R-001 baseline_none 的 2 样本冒烟测试**，并已生成可视化。R-002/R-003/R-004 仍未正式运行。

> 重要：当前结果只验证工程链路可用，不构成对 containerization 假设的正式支持或反驳。

## 运行汇总
| Run | Variant | Seed | 状态 | 样本数 | 主要产物 |
|---|---|---:|---|---:|---|
| R-001 | baseline_none | - | completed | 2 | predictions JSONL + 可视化 JPG |
| R-002 | within_object_shuffle | 0 | draft | - | 待运行 |
| R-003 | full_shuffle | 0 | draft | - | 待运行 |
| R-004 | padding_expand | - | draft | - | 待运行 |

## R-001 结果摘要
R-001 使用无干预 baseline，在 COCO val 上跑通了 2 个 visual-prompt 样本：

- 模型：`/home/featurize/work/mechanism/checkpoints/Rex-Omni`
- 数据：`/home/featurize/data/COCO2017`
- 输入 JSONL：`/home/featurize/work/mechanism/explog/E-001/coco_visual_prompt_16.jsonl`
- 预测文件：`/home/featurize/work/mechanism/explog/E-001/R-001/outputs/predictions_0_2.jsonl`
- 可视化目录：`/home/featurize/work/mechanism/explog/E-001/R-001/visualizations`
- 可视化索引：`/home/featurize/work/mechanism/explog/E-001/R-001/visualizations/manifest.json`

生成的可视化图：

- `00000_000000289343_none.jpg`
- `00001_000000061471_none.jpg`

可视化颜色约定：

- 蓝色：visual prompt / reference box
- 绿色：GT box
- 红色：模型预测 box

## 工程结论
1. Rex-Omni 本地 checkpoint 可以在当前服务器上加载并完成小样本推理。
2. `evaluation/inference_visual_prompt.py` 的 E-001 intervention 输出字段可正常写入 JSONL。
3. 新增脚本 `evaluation/visualize_e001_predictions.py` 可以直接把预测、GT 和 prompt box 渲染到图像上。
4. 后续正式/半正式 Runs 应统一采用“推理 → 预测 JSONL → 可视化 JPG + manifest”的流程。

## 已记录的环境问题与解决方式
1. **Hugging Face 自动下载失败**  
   - 现象：SSL EOF，vLLM 无法解析 `IDEA-Research/Rex-Omni`。
   - 解决：使用本地 checkpoint `/home/featurize/work/mechanism/checkpoints/Rex-Omni`。

2. **用户目录 flash_attn ABI 不兼容**  
   - 现象：`flash_attn_2_cuda` undefined symbol。
   - 解决：运行时设置 `PYTHONNOUSERSITE=1`，屏蔽用户目录中的不兼容 Python 包。

3. **错误的 vLLM attention backend 设置**  
   - 现象：`VLLM_ATTENTION_BACKEND=TORCH_SDPA` 导致 vLLM 报 `Invalid attention backend for cuda`。
   - 解决：去掉该环境变量，仅保留 `PYTHONNOUSERSITE=1`。

4. **tmux 审查问题**  
   - 现象：命令失败后 tmux 自动退出，用户无法 attach 审查。
   - 解决：后续使用持久 tmux 脚本；即使命令结束，也保留 shell 供审查。

## 对 Claims 的影响
暂不改变任何 claim 状态。R-001 只是 baseline smoke test，没有与 R-002/R-003/R-004 形成对照，因此不能判断 containerization 假设。

## 后续计划
运行 R-002/R-003/R-004 时，应全部使用：

- 本地模型路径：`/home/featurize/work/mechanism/checkpoints/Rex-Omni`
- 输入 JSONL：`/home/featurize/work/mechanism/explog/E-001/coco_visual_prompt_16.jsonl`
- 图像根目录：`/home/featurize/data/COCO2017`
- 环境变量：`PYTHONNOUSERSITE=1`
- 可视化脚本：`evaluation/visualize_e001_predictions.py`

## 局限性
- 当前只跑了 2 个样本；不能用于统计结论。
- 当前只完成 baseline，没有完成 paired intervention 对照。
- 干预是 image-space / prompt-box 级别，不能直接证明内部 visual token 机制。
