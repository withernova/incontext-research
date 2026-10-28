# e015-iploc144-qwen2-4shot-restart-r3-20261023 · IPLoc官方144修正划分后Qwen2四参考帧重新训练

- workflow: v2 / analysis_pending / 结果分析
- review_status: approved
- group_id: 未分组
- execution_dispatch: dispatch-35dd5e036dab5110a63caeb6 / completed

> v2 主表只有四栏：研究问题 / 目的 / 方法 / 详细实现细节。历史字段仍有内容时会归入对应小节并保留原文。

## 1. 研究问题
（待补充）

## 2. 目的
修正数据泄漏与近邻参考帧采样后重新启动自有SFT→GRPO多框score→VQA，使用作者发布144条评测。

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
- **IPLoc144 1shot VQA mIoU** (`iploc144_vqa_miou_1shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot VQA Acc50** (`iploc144_vqa_acc50_1shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot Proposal Oracle mIoU** (`iploc144_oracle_miou_1shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot Proposal Oracle Acc50** (`iploc144_oracle_acc50_1shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot Oracle与实际mIoU差距** (`iploc144_oracle_gap_1shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 1shot 候选可命中但未选中数量** (`iploc144_oracle_miss_count_1shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理1shot；非法/空输出IoU=0
- **IPLoc144 2shot VQA mIoU** (`iploc144_vqa_miou_2shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot VQA Acc50** (`iploc144_vqa_acc50_2shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot Proposal Oracle mIoU** (`iploc144_oracle_miou_2shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot Proposal Oracle Acc50** (`iploc144_oracle_acc50_2shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot Oracle与实际mIoU差距** (`iploc144_oracle_gap_2shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 2shot 候选可命中但未选中数量** (`iploc144_oracle_miss_count_2shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理2shot；非法/空输出IoU=0
- **IPLoc144 4shot VQA mIoU** (`iploc144_vqa_miou_4shot`)：100*mean(selected IoU)；VQA mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot VQA Acc50** (`iploc144_vqa_acc50_4shot`)：100*mean(selected IoU>=0.5)；VQA Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot Proposal Oracle mIoU** (`iploc144_oracle_miou_4shot`)：100*mean(max candidate IoU)；Proposal Oracle mIoU；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot Proposal Oracle Acc50** (`iploc144_oracle_acc50_4shot`)：100*mean(max candidate IoU>=0.5)；Proposal Oracle Acc50；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot Oracle与实际mIoU差距** (`iploc144_oracle_gap_4shot`)：100*mean(oracle IoU-selected IoU)；Oracle与实际mIoU差距；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0
- **IPLoc144 4shot 候选可命中但未选中数量** (`iploc144_oracle_miss_count_4shot`)：count(selected IoU<0.5<=oracle IoU)；候选可命中但未选中数量；paired common-query mean or count / 作者发布LaSOT144共同测试Query，官方commit27682bc2，同一E015训练pipeline，推理4shot；非法/空输出IoU=0

## 4. 详细实现细节
修正后独立重启：官方IPLoc commit27682bc2的LaSOT144条1/2/4shot逐条保留；训练LaSOT排除官方全部36类别，剩余真实原始类别补集（非声称FOCUS35/35）；GOT/TAO仅原train来源并保留旧holdout源视频保护。训练参考索引i*(N//4)，Query=N-1，TAO按标注目标时间线，异常样本剔除不挪动帧。GRPO双方身份按测试类别及源视频排除，整正负对及ABBA关联组过滤。旧E015有68个测试Query污染，SFT和selector均从官方Qwen2基础权重fresh LoRA启动，不复用旧adapter。复用已发布28c72aff代码、双卡×4副本及图像缓存。原SFT4epoch/global64/lr2e-4和GRPO400步奖励/score/prompt不变；GRPO后先官方144各shot评测并保存proposal，再独立VQA训练评测。新iploc144指标命名空间，无旧1728基线。任何数据审计或训练错误停止；输入脚本和来源SHA完整记录。此为自有方法在作者公开评测清单上的训练适配，不是FOCUS完整复现。 官方清单6个Query GT零面积及2/4shot零面积参考框原样保留；评测不套用训练清洗，零面积GT按现有IoU实现记0，144条分母不变，异常单独审计。r2数据准备在GPU训练前主动停止，原因是评测检查过严，保留其退出事实。

- 公共包：``
- 入口：``
- 配置：``
- Shell launcher：``
- 复用模块：（待登记）
- 新增模块：（待登记）
- 测试路径（不代表已执行）：（未登记，可留空）

> 代码应直接修改当前 Workspace 绑定仓库中的实际模块目录；只有仓库已有独立 launcher/adapter 目录时才使用它。工具不要求新建 codespace、实验索引或 runner 目录，科研逻辑不得为了登记 Run 而复制一份。

## 5. 运行与 Experiment Steward
- command: `/songzhengyue/miniconda3/envs/IPLoc/bin/python -c 'import pathlib,hashlib,json,os; b=pathlib.Path('"'"'/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/inputs/command.json'"'"').read_bytes(); assert hashlib.sha256(b).hexdigest()=='"'"'3d63e17bca4df1b9a0a53be941e5aac56b2277559a3116615a2d93dffd5413aa'"'"'; os.execv('"'"'/bin/bash'"'"',['"'"'bash'"'"','"'"'-c'"'"',json.loads(b)['"'"'command'"'"']])'`
- commit: `28c72afff503650316e37039c5931f2587b62b45`
- workspace: 03
- tmux: incontext-E-015-e015-iploc144-qwen2-4shot-restart-r3-20261023
- log: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/managed_console.log
- output: /defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/outputs
- Steward 摘要：```json
{
  "execution_completed_at": "2026-10-26T01:10:11",
  "evidence": {
    "log": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/managed_console.log",
    "artifact": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json",
    "result_message": "managed execution exited 0; metrics parsed; human analysis required"
  },
  "note": "程序已结束，等待科研结果分析"
}
```

## 6. 关键结果
### iploc144_vqa_miou_1shot = 60.93249183877414
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_vqa_acc50_1shot = 67.36111111111111
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_miou_1shot = 60.93249183877414
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_acc50_1shot = 67.36111111111111
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_gap_1shot = 0.0
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_miss_count_1shot = 0
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_vqa_miou_2shot = 61.162480906632446
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_vqa_acc50_2shot = 65.97222222222221
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_miou_2shot = 61.98003586156338
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_acc50_2shot = 66.66666666666666
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_gap_2shot = 0.8175549549309324
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_miss_count_2shot = 1
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_vqa_miou_4shot = 65.23348855828748
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_vqa_acc50_4shot = 72.91666666666666
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_miou_4shot = 65.38908655975659
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_acc50_4shot = 72.91666666666666
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_gap_4shot = 0.15559800146911495
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

### iploc144_oracle_miss_count_4shot = 0
- 比较：未记录
- 差值：未记录
- 不确定性：未记录
- 产物：/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json
- 解释：待分析

## 7. 结果分析
Managed execution exited successfully with 18 declared and 0 auxiliary metric observations. Scientific interpretation remains a human-reviewed draft.

## 简短局限
Phase 1 records process evidence and declared metrics only; it does not validate causal or Claim conclusions.

<details><summary>历史字段原文（保留，不再进入主表）</summary>

```json
{
  "necessity": "旧E015训练与官方测试有68相同Query，旧adapter不复用；用户明确授权修正并重启。",
  "implementation_details": "修正后独立重启：官方IPLoc commit27682bc2的LaSOT144条1/2/4shot逐条保留；训练LaSOT排除官方全部36类别，剩余真实原始类别补集（非声称FOCUS35/35）；GOT/TAO仅原train来源并保留旧holdout源视频保护。训练参考索引i*(N//4)，Query=N-1，TAO按标注目标时间线，异常样本剔除不挪动帧。GRPO双方身份按测试类别及源视频排除，整正负对及ABBA关联组过滤。旧E015有68个测试Query污染，SFT和selector均从官方Qwen2基础权重fresh LoRA启动，不复用旧adapter。复用已发布28c72aff代码、双卡×4副本及图像缓存。原SFT4epoch/global64/lr2e-4和GRPO400步奖励/score/prompt不变；GRPO后先官方144各shot评测并保存proposal，再独立VQA训练评测。新iploc144指标命名空间，无旧1728基线。任何数据审计或训练错误停止；输入脚本和来源SHA完整记录。此为自有方法在作者公开评测清单上的训练适配，不是FOCUS完整复现。 官方清单6个Query GT零面积及2/4shot零面积参考框原样保留；评测不套用训练清洗，零面积GT按现有IoU实现记0，144条分母不变，异常单独审计。r2数据准备在GPU训练前主动停止，原因是评测检查过严，保留其退出事实。",
  "artifacts": "/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/metrics.json\n/defaultShare/archive/songzhengyue/projects/IPLoc/experiments/E-015/e015-iploc144-qwen2-4shot-restart-r3-20261023/managed_console.log"
}
```

</details>

## 自由笔记（Obsidian）

这里可记录过程观察；结构化更新不会覆盖本节。
