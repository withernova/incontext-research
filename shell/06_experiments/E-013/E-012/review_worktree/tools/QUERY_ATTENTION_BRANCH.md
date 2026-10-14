# Qwen3-VL query attention 分支

所有实验设置统一在 configs/sft/qwen3vl_8b_focus_branch.py。
常用修改位置：

- branch.source / branch.source_profiles：选择父 checkpoint。
  checkpoint 指向包含 adapter/ 与 trainer_state.pt 的完整目录。
- branch.nproc_per_node：并行 GPU 数；named_run.run_name：本次名称。
- runtime.test_dataloader.dataset.ann_file：eval manifest。
- evaluation.limit=None：完整 eval；seed、图像 token 上限与生成长度也在 evaluation 中。
- attention_intervention.auto_head_screening.top_k：自动选多少个 query heads，默认 5。
- auto_head_screening.samples=None：用完整 eval 筛选；设置正整数可固定筛选子集。
- attention_intervention.generation_steps="all"：整个实际生成序列；也支持 [0,1,...]。
- attention_intervention.heads=()：自动筛选；填写 LxxHyy 列表则直接使用。

启动仍用：

\`\`\`bash
bash tools/run/eval/run_e011_inter.sh
\`\`\`

该 launcher 读取上述统一配置并选择 branch.action=attention_intervene；
不修改统一配置中的默认 action，因此其他 train/evaluate launcher 仍照常使用。
可通过末尾 key=value 覆盖配置；--inspect 只解析配置，不加载模型或分配运行目录。
qwen3vl_8b_focus_query_attention_branch.py 仅保留为旧调用的兼容别名。

## 自动执行顺序

1. 加载统一 source 指定的 Qwen3-VL checkpoint，与 LoRA 配置做一致性检查。
2. 固定 eval manifest 哈希和样本索引，用同一个已加载模型在 eval 集筛选一次。
3. 复用 teacher-forced query bbox p-1 行与 R003 query 排名算法，固定 Top-K。
   probe 按层提取需要的行，避免保存所有层的完整序列 attention；
   排名按需读取 map，不把完整 eval 的空间 map 一起放入内存。
4. 对完整 eval 的每个样本执行 baseline、noop、gt_align，期间不再重筛 head。

自动筛选结果写入 query_attention/head_screening/selected_heads.json，
包含 checkpoint、manifest 哈希、筛选索引、seed、head 排名与最终 head 列表。
筛选失败或样本覆盖不完整时不进入预测干预，不自动换用随机 head。

## 生成时干预

取当前样本 query 的真实 GT，按 GT 框与 post-merge token-grid 的重叠面积，
在 attention×V 前重分配指定 head 对 query image 的概率，保留原 query 总 mass。
其余 token 概率不变。使用原生 Qwen3 Q/K norm、RoPE、GQA 与 KV cache。
实例 hook 随每次 generate 安装/恢复，原有训练和普通评估不启用。

将修改前后的 AV 差值加回原 backend 输出：no-op 差值严格为零；
GT 条件的差值传播到后续层和最终 bbox 生成。
no-op token 必须完全一致，logits 按统一配置中的 atol/rtol 检查，默认均为零。

每个样本的独立 JSON 保存三条件生成文本/token、前后 map、GT map、
token-grid、selected-token-count、query/GT mass、预测行、head 输出变化、
有效框、IoU、归一化中心距离与配对差值。
汇总 predictions.jsonl 保留指标及审计路径，避免全量 map 在跨 GPU 汇总时重复占用内存。
指标位于 evaluation/metrics.json；只在完整 coverage、no-op 和对齐 gate
通过且三条件均有有效框时允许解读结果。

generation_steps=all 按每个条件实际生成到 EOS 的长度检查 coverage；
固定整数列表则要求每一行实际执行。
筛选与干预使用同一 eval 集，且筛选行使用 GT assistant suffix，
结果属于该 eval 集上的机制诊断，不作为独立泛化评估。
