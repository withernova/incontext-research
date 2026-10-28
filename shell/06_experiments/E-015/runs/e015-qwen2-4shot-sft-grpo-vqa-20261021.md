# e015-qwen2-4shot-sft-grpo-vqa-20261021 · Qwen2四参考帧完整方法训练与同模型多shot评测

- workflow: v2 / failed / 运行失败
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-8c6ae75f6165d2823559fa09 / failed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
（待补充）

## 2. 目的
按统一Qwen2基础设置运行自有SFT→GRPO多框→VQA方法，检验增加参考帧后实际选择与Oracle差距。

## 3. 方法（干预 · 对照 · 指标与判定规则）
（待补充：干预什么、和什么比、什么算通过）

### 已注册指标定义
- **1shot VQA mIoU** (`vqa_miou_1shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot VQA Acc50** (`vqa_acc50_1shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot Proposal Oracle mIoU** (`oracle_miou_1shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot Proposal Oracle Acc50** (`oracle_acc50_1shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot Oracle与实际mIoU差距** (`oracle_gap_1shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **1shot 候选可命中但未选中数量** (`oracle_miss_count_1shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **2shot VQA mIoU** (`vqa_miou_2shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot VQA Acc50** (`vqa_acc50_2shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot Proposal Oracle mIoU** (`oracle_miou_2shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot Proposal Oracle Acc50** (`oracle_acc50_2shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot Oracle与实际mIoU差距** (`oracle_gap_2shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **2shot 候选可命中但未选中数量** (`oracle_miss_count_2shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **4shot VQA mIoU** (`vqa_miou_4shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot VQA Acc50** (`vqa_acc50_4shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot Proposal Oracle mIoU** (`oracle_miou_4shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot Proposal Oracle Acc50** (`oracle_acc50_4shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot Oracle与实际mIoU差距** (`oracle_gap_4shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **4shot 候选可命中但未选中数量** (`oracle_miss_count_4shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 1728共同测试Query，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **历史E014 VQA mIoU** (`baseline_vqa_miou`)：100*mean(historical IoU on common1728 query indices)；历史E014 VQA mIoU；mean / 同1728 Query重算旧原proposal+linear5388；非单因子对照
- **历史E014 Oracle mIoU** (`baseline_oracle_miou`)：100*mean(historical IoU on common1728 query indices)；历史E014 Oracle mIoU；mean / 同1728 Query重算旧原proposal+linear5388；非单因子对照

## 4. 详细实现细节
用户授权独立E015：Qwen2-VL-7B-Instruct官方eed13092，4shot训练同checkpoint评测1/2/4，4副本×2张3090、10/18层、NF4/BF16/SDPA、每图4096 rawpatch。无FOCUS attention loss/专有奖励。SFT4epochs/global64/lr2e-4/warmup.03/clip.3，保持原CE/置信度格式损失.1；GRPO自有variable discovery score04 beta0、G4、192token、lr1e-5/warmup.01/clip1，400更新匹配旧8副本200更新的1600rank-pair呈现（不等同数据/随机序列相同）。源4000+对称数据先完整审计，再按26重合源视频整正负对/整ABBA四元组排除，绝不改历史输入。10175条SFT训练，1728条共同测试。SFT后用最终GRPO生成选择训练候选，源视频分组15%验证；仅训练nonempty低Oracle追加GT、保留原候选并全循环换序；独立fresh选择LoRA4epochs/global16/lr5e-5末1/4线性到.1。单框直通，多框strict number/EOS。最后同一模型1/2/4shot全1728评测，并重算E014 linear5388在共同Query上的指标。参数/代码/输入SHA/各阶段配置与产物均保留，任一失败停止。GRPO GPU尚未独立验证，将在正式阶段检查有限梯度和逐步跨副本SHA；新结果不能单独归因shot数。 26源视频排除在原始4000行中删除105完整正负对、在对称1000源对中删除115整组，最终3790+3540=7330行/3665训练pair；原正负行各1895。 正式选择器沿用主线lr5e-5，warmup.03和clip.3与本轮SFT基础设置统一；能力补测的clip1仅为工程短测，不冒充正式参数。 真实预算修复后使用28c72aff（含7c1b73e预算修复）：Qwen2 legacy min/max_pixels与size同步；SFT、GRPO、推理均检查实际patch上限。此前SFT能力峰值18.5GiB对应超出4096的旧实际输入，不能当成正式预算下显存。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-4shot-sft-grpo-vqa-20261021/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'c280d74a698a061a76655c49f206d4864cb89ab25ba1baa933a6bfe4bea7e06c'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'`
- commit: `28c72afff503650316e37039c5931f2587b62b45`
- workspace: 03
- tmux: incontext-E-015-e015-qwen2-4shot-sft-grpo-vqa-20261021
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-4shot-sft-grpo-vqa-20261021/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-qwen2-4shot-sft-grpo-vqa-20261021/outputs
- Steward 摘要：尚未启动；浏览器不会自动启动 Extension

## 6. 关键结果
（程序完成后登记具体数值、比较对象和结果文件。）

## 7. 结果分析
【已作废，不作为有效科学结果】用户2026-10-23明确要求当前实验作废。当前数据构造未充分核实FOCUS/IPLoc官方划分与support/query采样，不能据此作benchmark对比或score/shot收益结论。按授权向本Run四shot评测torchrun PID444727发送SIGTERM，保留实际退出码、全部历史数据/checkpoint/日志/结果。此为用户撤销本次实验，不是训练数值失败；禁止自动重试或复用这些数据/模型作为重建实验的有效基线。

## 简短局限
所有本次数据派生的SFT/GRPO/选择器模型及1/2shot指标仅保留追溯；4shot评测中止。撤回此前方法收益与FOCUS数值优劣的解释，不抹除原始执行事实。

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "既有可视化显示参考帧时距与实例漏选问题；独立E015避免混淆旧模型和固定三框实验。",
  "implementation_details": "用户授权独立E015：Qwen2-VL-7B-Instruct官方eed13092，4shot训练同checkpoint评测1/2/4，4副本×2张3090、10/18层、NF4/BF16/SDPA、每图4096 rawpatch。无FOCUS attention loss/专有奖励。SFT4epochs/global64/lr2e-4/warmup.03/clip.3，保持原CE/置信度格式损失.1；GRPO自有variable discovery score04 beta0、G4、192token、lr1e-5/warmup.01/clip1，400更新匹配旧8副本200更新的1600rank-pair呈现（不等同数据/随机序列相同）。源4000+对称数据先完整审计，再按26重合源视频整正负对/整ABBA四元组排除，绝不改历史输入。10175条SFT训练，1728条共同测试。SFT后用最终GRPO生成选择训练候选，源视频分组15%验证；仅训练nonempty低Oracle追加GT、保留原候选并全循环换序；独立fresh选择LoRA4epochs/global16/lr5e-5末1/4线性到.1。单框直通，多框strict number/EOS。最后同一模型1/2/4shot全1728评测，并重算E014 linear5388在共同Query上的指标。参数/代码/输入SHA/各阶段配置与产物均保留，任一失败停止。GRPO GPU尚未独立验证，将在正式阶段检查有限梯度和逐步跨副本SHA；新结果不能单独归因shot数。 26源视频排除在原始4000行中删除105完整正负对、在对称1000源对中删除115整组，最终3790+3540=7330行/3665训练pair；原正负行各1895。 正式选择器沿用主线lr5e-5，warmup.03和clip.3与本轮SFT基础设置统一；能力补测的clip1仅为工程短测，不冒充正式参数。 真实预算修复后使用28c72aff（含7c1b73e预算修复）：Qwen2 legacy min/max_pixels与size同步；SFT、GRPO、推理均检查实际patch上限。此前SFT能力峰值18.5GiB对应超出4096的旧实际输入，不能当成正式预算下显存。"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
