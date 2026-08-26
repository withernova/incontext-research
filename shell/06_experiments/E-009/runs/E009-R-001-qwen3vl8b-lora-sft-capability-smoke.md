# E009-R-001-qwen3vl8b-lora-sft-capability-smoke · Qwen3-VL-8B 基础 LoRA 微调能力烟雾实验

- workflow: v2 / ready_to_run / 等待执行授权
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-af1194c524865c4b9bad8a4f / queued

## 1. 研究设计
### 研究问题
当前工作区能否在不改动基础权重的前提下，对本地 Qwen3-VL-8B-Instruct 完成一次可复现的多模态 LoRA 监督微调闭环？
### 本轮目的
用极小的图像—指令—框答案数据完成加载、前向、反向、参数更新、保存和重载，直接判断当前机器与软件栈是否支持基础 SFT；本 Run 不评估 IPLoc-ID 的科学效果。
### 假设或比较预期
在隔离环境中安装与本地 Qwen3-VL 匹配的 PyTorch、Transformers、PEFT 与 Accelerate 后，冻结视觉编码器和基础模型，仅训练 rank-8 LoRA，可在单张 24 GiB GPU 上完成至少 3 个优化步骤并保存可重载 adapter。
### 数据与主要变量
运行时在 E-009 专属产物目录生成 4 张简单几何图像及 8 条确定性监督样本；每条包含单图、定位指令和归一化 xyxy 框答案。该数据只验证训练链路与可学习性，不代表 IPLoc/IPLoc-ID 数据分布。

唯一处理是启用 LoRA 并执行监督更新。控制包括：更新前基线损失、同一固定 batch 的更新后损失、只读基础权重校验、LoRA 参数变化检查，以及保存后重新加载 adapter 的输出/损失一致性检查。样本、顺序、seed、图像尺寸和 prompt 在看结果前固定。

## 2. 指标设计
主判据为 capability gate：训练依赖可导入、单 batch 前向损失有限、反向梯度有限、至少 3 次 optimizer step 完成、LoRA 参数实际变化、adapter 保存并成功重载。学习信号辅判据为同一固定 batch 的更新后 loss 低于更新前 loss；显存峰值和总耗时只作资源记录。
## 3. 代码架构
在 mechanism/iplocid 内新增独立、最小的 Qwen3-VL SFT smoke 模块与可读 launcher，复用现有 vlm loader/消息格式中兼容部分但不改动 attention 实验代码；输出机器可读 metrics.json、冻结配置、训练日志与 adapter 目录。先做 CPU 级数据/collator 测试，再申请执行 smoke。
- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试：（待登记）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 4. 运行与 Experiment Steward
- command: `bash mechanism/iploc-szy/run_e009_r001.sh`
- commit: ``
- workspace: 02
- tmux: incontext-E-009-E009-R-001-qwen3vl8b-lora-sft-capability-smoke
- log: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-001-qwen3vl8b-lora-sft-capability-smoke/logs/train.log
- output: /defaultShare/archive/liuwenchu/projects/IPLoc/experiments/E-009/E009-R-001-qwen3vl8b-lora-sft-capability-smoke/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 5. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 6. 结果分析
（程序结束后由 pi 与研究者分析，Outbox completed 不等于科研分析完成。）

## 简短局限
合成小样本与最多 8 步只验证训练闭环和过拟合信号；不能证明真实 IPLoc/IPLoc-ID 数据可训、训练稳定、泛化提升、多卡效率或论文结果可复现。24 GiB 单卡是否足够仍需实际峰值显存 gate 验证。

<details><summary>历史兼容字段与补充执行信息</summary>

```json
{
  "necessity": "当前有完整 Qwen3-VL 基础模型和 4×24 GiB GPU，但系统与 Miniconda Python 均缺训练依赖；IPLoc/IPLoc-ID 没有公开训练入口，Rex-Omni 的入口又固定为 Qwen2.5-VL，因此仅凭现有文件不能确认 Qwen3-VL SFT 可运行。",
  "evidence_basis": "只读勘察已确认：本地模型 10/10 分片齐全；IPLoc-ID 的既有 adapter 使用 rank 8、排除 visual、作用于语言侧 q/k/v/o 与 MLP 投影层；Rex-Omni 提供监督训练数据组织思路但其现有 train.py 只适配 Qwen2.5-VL。",
  "implementation_summary": "需要补一个仅服务于 E-009 的最小 Qwen3-VL LoRA SFT 入口：生成确定性小数据，正确屏蔽非答案 token，执行短训练并验证 adapter 重载。当前只登记设计，不改代码、不安装依赖、不启动训练。",
  "implementation_details": "实现须显式使用 Qwen3-VL 对应 AutoProcessor/模型类，检查 image token 与 labels 对齐；只将 LoRA 参数设为可训练；每步记录 loss、梯度有限性和显存；保存前后在 eval/no_grad 下复测固定 batch。不得复用 Rex-Omni 中固定 Qwen2.5-VL 的模型类，不得覆盖 iplocid 当前未提交改动。",
  "model_config": "本地 Qwen3-VL-8B-Instruct；bf16；基础模型与视觉模块冻结；LoRA r=8、alpha=16、dropout=0，目标模块沿用本地 IPLoc-ID adapter 的语言侧投影层并排除 visual；batch size 1、gradient checkpointing 开启、单 GPU。若显存 gate 失败只能停止并另提量化方案，不在本 Run 静默改配置。",
  "metric_definition": "loss_before/loss_after：同一 tokenized 多模态 batch 上、仅对 assistant 答案 token 计交叉熵；finite_grad_fraction：有梯度的可训练参数中梯度全为有限值的比例；adapter_delta_norm：更新前后全部 LoRA 参数差的 L2 范数；reload_loss_abs_diff：保存前与重载后固定 batch loss 的绝对差；peak_gpu_memory_gib：torch CUDA 峰值分配显存。",
  "integrity_gates": "开始前：10 个基础模型分片均存在、目标 GPU 可用、专属输出目录为空或为本 Run 可恢复目录。训练中：labels 含至少一个非 -100 答案 token、loss/梯度有限、可训练参数全部为 LoRA 且数量大于 0、基础参数无变化。结束时：steps>=3、adapter_delta_norm>0、adapter_config 与权重文件存在、独立重载成功、reload_loss_abs_diff<=1e-4。任一项失败即报告 gate_failed，不把部分产物称为支持 SFT。",
  "expected_outcome": "若环境与实现兼容，应在单卡完成短 LoRA 更新，固定 batch loss 出现下降且 adapter 可无损重载；否则错误将定位到依赖、显存、Qwen3-VL 数据对齐、反向或保存重载中的具体阶段。",
  "acceptance_criteria": "工程支持：所有完整性 gate 通过。基础可学习性：loss_after < loss_before。只有两者同时满足才记为“当前环境支持基础 Qwen3-VL LoRA SFT smoke”；仅能前向或仅能保存均不算通过。",
  "claim_boundary": "通过时只能得出“该机器在所记录依赖与配置下可完成 Qwen3-VL-8B 的基础 LoRA 多模态 SFT smoke”。不得声称支持全参数 SFT、正式规模训练，或对个性化目标定位有效。",
  "audit_paths": "E-009 Run note；远端 experiments/E-009/E009-R-001-qwen3vl8b-lora-sft-capability-smoke/{config.json,metrics.json,train.log,adapter/}；实现后补充精确代码路径、commit/dirty diff 与测试命令。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
